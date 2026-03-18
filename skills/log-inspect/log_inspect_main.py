#!/usr/bin/env python3
"""
日志巡检统一入口脚本
封装完整流程:解析需求 → 拉取日志 → 分析 → 生成报告 → 推送
"""

import os
import sys

# Windows 控制台强制 UTF-8，避免 emoji 编码报错
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json
import argparse
import subprocess
import re
import socket
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple, List

# 导入工具组 API 拉取器
from tool_api_fetcher import ToolAPIFetcher


class LogInspector:
    """日志巡检主类"""
    
    def __init__(self, config_path: str = "config/environments.json"):
        self.script_dir = Path(__file__).parent
        self.config_path = self.script_dir / config_path
        self.environments = self._load_config()
        
    def _load_config(self) -> Dict:
        """加载环境配置"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 移除模板配置
        config.pop('_template', None)
        return config
    
    def parse_natural_language(self, text: str) -> Dict:
        """
        解析自然语言需求
        示例: "帮我分析桐乡病区护士站今天上午8-10点的日志"
        """
        result = {
            'hospital': None,
            'service': None,
            'cluster': None,
            'start_time': None,
            'end_time': None,
            'level': 'ERROR|业务处理耗时'
        }
        
        # 匹配医院名称（支持部分匹配）
        for hospital_key in self.environments.keys():
            # 完全匹配
            if hospital_key in text:
                result['hospital'] = hospital_key
                break
            # 部分匹配：检查医院 key 的前缀（2-5个字）是否在文本中
            for length in [5, 4, 3, 2]:
                if len(hospital_key) >= length and hospital_key[:length] in text:
                    result['hospital'] = hospital_key
                    break
            if result['hospital']:
                break
        
        # 匹配服务名称（如果环境配置中有 services 映射）
        if result['hospital']:
            env = self.environments[result['hospital']]
            if 'services' in env:
                for service_name in env['services'].keys():
                    if service_name in text:
                        result['service'] = service_name
                        break
            
            # 匹配集群名称（如果是多集群配置）
            if 'grafana' in env and 'clusters' in env['grafana']:
                for cluster in env['grafana']['clusters']:
                    cluster_name = cluster.get('name', '')
                    if cluster_name in text:
                        result['cluster'] = cluster_name
                        break
        
        # 匹配时间范围
        result['start_time'], result['end_time'] = self._parse_time_range(text)
        
        # 匹配日志级别
        if 'ERROR' in text.upper() and 'WARN' not in text.upper():
            result['level'] = 'ERROR'
        elif 'WARN' in text.upper() and 'ERROR' not in text.upper():
            result['level'] = 'WARN'
        
        return result
    
    def _parse_time_range(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """解析时间范围"""
        now = datetime.now()
        
        # 匹配"今天"、"昨天"
        if '今天' in text:
            date = now.date()
        elif '昨天' in text:
            date = (now - timedelta(days=1)).date()
        else:
            # 尝试匹配具体日期 YYYY-MM-DD 或 MM-DD
            date_match = re.search(r'(\d{4}-)?(\d{1,2})-(\d{1,2})', text)
            if date_match:
                year = date_match.group(1).rstrip('-') if date_match.group(1) else str(now.year)
                month = date_match.group(2).zfill(2)
                day = date_match.group(3).zfill(2)
                date = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d").date()
            else:
                date = now.date()
        
        # 匹配时间段
        time_match = re.search(r'(\d{1,2})[点:：]?-?(\d{1,2})[点:：]?', text)
        if time_match:
            start_hour = int(time_match.group(1))
            end_hour = int(time_match.group(2))
            
            # 处理"上午"、"下午"
            if '下午' in text and start_hour < 12:
                start_hour += 12
                end_hour += 12
            
            start_time = f"{date} {start_hour:02d}:00"
            end_time = f"{date} {end_hour:02d}:00"
        else:
            # 默认最近1小时，保留当前分钟，不再截断到整点
            start_time = (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
            end_time = now.strftime("%Y-%m-%d %H:%M")
        
        return start_time, end_time
    
    def _check_port(self, host: str, port: int, timeout: float = 2.0) -> bool:
        """
        检测端口是否可达
        
        Args:
            host: 主机地址
            port: 端口号
            timeout: 超时时间（秒）
        
        Returns:
            True 如果端口可达，False 否则
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception as e:
            return False
    
    def _parse_grafana_url(self, url: str) -> Tuple[str, int]:
        """
        解析 Grafana URL，提取主机和端口
        
        Args:
            url: Grafana URL (例如: http://127.0.0.1:16291)
        
        Returns:
            (host, port) 元组
        """
        import re
        match = re.match(r'https?://([^:]+):(\d+)', url)
        if match:
            return match.group(1), int(match.group(2))
        else:
            # 默认端口
            if url.startswith('https://'):
                return url.replace('https://', '').rstrip('/'), 443
            else:
                return url.replace('http://', '').rstrip('/'), 80
    
    def fetch_logs(self, hospital: str, service: str, start_time: str, 
                   end_time: str, level: str = "ERROR|WARN", 
                   cluster: Optional[str] = None) -> str:
        """
        拉取日志
        返回日志文件路径
        
        Args:
            hospital: 医院名称
            service: 服务名称
            start_time: 开始时间
            end_time: 结束时间
            level: 日志级别
            cluster: 集群名称（多集群时必须指定）
        """
        env = self.environments.get(hospital)
        if not env:
            raise ValueError(f"未找到医院配置: {hospital}")
        
        # 检查环境类型
        env_type = env.get('type')
        if env_type == 'k8s' and 'grafana' in env:
            return self._fetch_from_loki(env, service, start_time, end_time, level, cluster)
        elif env_type in ('tool_api', 'traditional') and 'toolApi' in env:
            return self._fetch_from_tool_api(env, service, start_time, end_time)
        else:
            raise ValueError(f"不支持的环境类型: {env_type}，或缺少 toolApi/grafana 配置")
    
    def _fetch_from_loki(self, env: Dict, service: str, start_time: str, 
                         end_time: str, level: str, cluster: Optional[str] = None) -> str:
        """从 Loki 拉取日志（支持多集群）
        
        Args:
            env: 环境配置
            service: 服务名称
            start_time: 开始时间
            end_time: 结束时间
            level: 日志级别
            cluster: 指定的集群名称（多集群时必须提供）
        """
        
        # 获取应用名称
        if 'services' in env and service in env['services']:
            app_name = env['services'][service]
        else:
            app_name = service
        
        # 生成输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 检查是否为多集群配置
        grafana_config = env['grafana']
        clusters = []
        
        if 'clusters' in grafana_config:
            # 多集群配置
            all_clusters = grafana_config['clusters']
            
            # 如果用户没有指定集群，给出提醒
            if not cluster:
                cluster_names = [c.get('name', f'集群{i+1}') for i, c in enumerate(all_clusters)]
                raise ValueError(
                    f"该医院有 {len(all_clusters)} 个集群，请指定要查询的集群：\n" +
                    "\n".join([f"  - {name}" for name in cluster_names]) +
                    f"\n\n示例：\n  python log_inspect_main.py \"分析{env.get('name', '医院')}{service}{cluster_names[0]}今天上午8-10点的日志\"\n" +
                    f"  或使用参数：--cluster {cluster_names[0]}"
                )
            
            # 查找指定的集群
            matched_cluster = None
            for c in all_clusters:
                if c.get('name') == cluster:
                    matched_cluster = c
                    break
            
            if not matched_cluster:
                cluster_names = [c.get('name', f'集群{i+1}') for i, c in enumerate(all_clusters)]
                raise ValueError(
                    f"未找到集群 '{cluster}'，可用的集群有：\n" +
                    "\n".join([f"  - {name}" for name in cluster_names])
                )
            
            clusters = [matched_cluster]
            print(f"[医院] 已选择集群: {cluster}")
        else:
            # 单集群配置（向后兼容）
            clusters = [{
                'name': '默认集群',
                'url': grafana_config['url'],
                'datasource_id': grafana_config['datasource_id']
            }]
        
        # 存储所有集群的日志文件（现在只会有一个）
        log_files = []
        failed_clusters = []
        
        # 遍历集群（现在只会有一个）
        for idx, cluster_info in enumerate(clusters, 1):
            cluster_name = cluster_info.get('name', f'集群{idx}')
            grafana_url = cluster_info['url']
            datasource_id = cluster_info['datasource_id']
            
            print(f"\n{'='*50}")
            print(f"[集群] {cluster_name}")
            print(f"{'='*50}")
            
            # 检测端口
            host, port = self._parse_grafana_url(grafana_url)
            print(f"[检测] 检测端口: {host}:{port} ... ", end='')
            
            if not self._check_port(host, port):
                print(f"[失败] 失败")
                print(f"[警告]  端口 {port} 无法访问，可能原因：")
                print(f"   1. 端口转发未开启")
                print(f"   2. Grafana 服务未启动")
                print(f"   3. 防火墙阻止了连接")
                print(f"[建议] 建议：检查端口转发配置或联系运维")
                failed_clusters.append(cluster_name)
                continue
            
            print(f"[成功] 成功")
            
            # 生成该集群的输出文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.script_dir / f"logs_{timestamp}_{cluster_name}.log"
            
            # 构建命令
            cmd = [
                sys.executable,
                str(self.script_dir / "loki_fetcher.py"),
                "--grafana", grafana_url,
                "--datasource", str(datasource_id),
                "--app", app_name,
                "--start", start_time,
                "--end", end_time,
                "--level", level,
                "--limit", "5000",
                "--min-chunk", "0.25",
                "--saturation-threshold", "3",
                "--fallback-window-seconds", "10",
                "--output", str(output_file)
            ]
            
            print(f"[检测] 正在拉取日志...")
            print(f"   医院: {env.get('name', '未知')}")
            print(f"   集群: {cluster_name}")
            print(f"   服务: {service} ({app_name})")
            print(f"   时间: {start_time} ~ {end_time}")
            print(f"   级别: {level}")
            
            fetch_start_ts = datetime.now()
            try:
                result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True, timeout=1200)
                
                if result.returncode != 0:
                    print(f"[失败] 日志拉取失败: {result.stderr}")
                    failed_clusters.append(cluster_name)
                    continue
                
                # 检查文件是否存在且有内容
                if output_file.exists() and output_file.stat().st_size > 0:
                    fetch_end_ts = datetime.now()
                    fetch_duration_s = int((fetch_end_ts - fetch_start_ts).total_seconds())
                    self._last_fetch_meta = {
                        'fetch_start': start_time,
                        'fetch_end': end_time,
                        'fetch_duration_s': fetch_duration_s
                    }
                    # 保存第二阶段需要的参数
                    self._last_grafana_url = grafana_url
                    self._last_datasource_id = datasource_id
                    self._last_app_name = app_name
                    print(f"[成功] 日志拉取完成: {output_file}")
                    log_files.append(str(output_file))
                else:
                    print(f"[警告]  该集群无日志数据")
                    
            except subprocess.TimeoutExpired:
                print(f"[失败] 日志拉取超时（5分钟）")
                failed_clusters.append(cluster_name)
            except Exception as e:
                print(f"[失败] 日志拉取异常: {str(e)}")
                failed_clusters.append(cluster_name)
        
        # 汇总结果
        print(f"\n{'='*50}")
        print(f"[统计] 拉取结果")
        print(f"{'='*50}")
        
        if not log_files:
            raise RuntimeError(f"集群 '{cluster_name}' 的日志拉取失败，请检查配置和网络连接")
        
        # 返回日志文件（现在只有一个）
        return log_files[0]
    
    def _fetch_from_tool_api(self, env: Dict, service: str,
                             start_time: str, end_time: str,
                             trace_id: Optional[str] = None) -> str:
        """从工具组 API 拉取日志（适用于 tool_api / traditional 类型）

        普通巡检：取第一个节点
        指定 traceId：拉取所有节点并合并（跨节点追踪）
        """
        if 'services' in env and service in env['services']:
            app_name = env['services'][service]
        else:
            app_name = service

        tool_api_config = env.get('toolApi', {})
        base_url = tool_api_config.get('baseUrl')
        app_id = tool_api_config.get('appId')
        env_id = tool_api_config.get('envId')
        node_ips = tool_api_config.get('nodeIps', [])  # 可选：限定目标节点 IP

        if not all([base_url, app_id, env_id]):
            raise ValueError("toolApi 配置不完整，需要 baseUrl、appId、envId")

        fetcher = ToolAPIFetcher(base_url)

        # 1. 查询节点列表
        print(f"\n{'='*50}")
        print(f"[工具组] 查询节点列表...")
        nodes = fetcher.get_nodes(app_name, app_id)
        if not nodes:
            raise RuntimeError("未获取到节点列表，请检查 code/appId 配置")

        # 2. 按 nodeIps 过滤（如果配置了）
        if node_ips:
            nodes = [n for n in nodes if n['ip'] in node_ips]
            if not nodes:
                raise RuntimeError(f"按 nodeIps 过滤后无节点，请检查配置: {node_ips}")

        # 3. 选取目标节点
        if trace_id:
            target_nodes = nodes
            print(f"[工具组] traceId 模式，拉取全部 {len(target_nodes)} 个节点")
        else:
            target_nodes = [nodes[0]]
            print(f"[工具组] 普通巡检，使用节点 {nodes[0]['ip']} ({nodes[0]['id']})")

        print(f"[工具组] 服务: {service} ({app_name})")
        print(f"[工具组] 时间: {start_time} ~ {end_time}")

        # 4. 逐节点拉取
        log_files = []
        for node in target_nodes:
            print(f"\n[工具组] 拉取节点 {node['ip']}...")
            fetch_start_ts = datetime.now()
            log_file = fetcher.fetch_logs(
                app_id=app_id,
                env_id=env_id,
                program_name=app_name,
                node_id=node['id'],
                start_time=start_time,
                end_time=end_time,
                log_type='all',
                output_dir=str(self.script_dir)
            )
            fetch_end_ts = datetime.now()
            self._last_fetch_meta = {
                'fetch_start': start_time,
                'fetch_end': end_time,
                'fetch_duration_s': int((fetch_end_ts - fetch_start_ts).total_seconds())
            }
            log_files.append(log_file)

        # 5. 多节点合并
        if len(log_files) == 1:
            return log_files[0]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        merged_file = str(self.script_dir / f"logs_{timestamp}_{app_name}_merged.log")
        print(f"\n[工具组] 合并 {len(log_files)} 个节点日志...")
        with open(merged_file, 'w', encoding='utf-8', errors='ignore') as out:
            for lf in sorted(log_files):
                with open(lf, 'r', encoding='utf-8', errors='ignore') as f:
                    out.write(f.read())
        print(f"[工具组] 合并完成: {merged_file}")
        return merged_file
    
    def analyze_logs(self, log_file: str, threshold: int = 1000) -> str:
        """
        分析日志
        返回 digest.json 文件路径
        """
        digest_file = log_file.replace('.log', '_digest.json')
        
        cmd = [
            sys.executable,
            str(self.script_dir / "preprocess.py"),
            log_file,
            "-o", digest_file,
            "-t", str(threshold)
        ]
        
        # 传入拉取时间范围和耗时
        fetch_meta = getattr(self, '_last_fetch_meta', {})
        if fetch_meta:
            cmd += ["--fetch-start", fetch_meta.get('fetch_start', '')]
            cmd += ["--fetch-end", fetch_meta.get('fetch_end', '')]
            cmd += ["--fetch-duration", str(fetch_meta.get('fetch_duration_s', 0))]
        
        print(f"[统计] 正在分析日志...")
        
        result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"日志分析失败:\n{result.stderr}")
        
        # 解析 digest 获取统计信息
        with open(digest_file, 'r', encoding='utf-8') as f:
            digest = json.load(f)
        
        stats = digest.get('summary', {})
        print(f"[成功] 分析完成:")
        print(f"   总日志数: {stats.get('total_lines', 0)}")
        print(f"   ERROR: {stats.get('error_count', 0)}")
        print(f"   WARN: {stats.get('warn_count', 0)}")
        print(f"   慢接口: {len(digest.get('slow_apis', []))}")
        
        return digest_file
    
    def generate_report(self, digest_file: str, hospital: str, 
                       service: str) -> str:
        """
        生成 HTML 报告
        返回报告文件路径
        """
        report_file = digest_file.replace('_digest.json', '_report.html')
        
        env = self.environments.get(hospital, {})
        hospital_name = env.get('name', hospital)
        
        # 使用新的报告生成器（支持中文分类和优化建议）
        cmd = [
            sys.executable,
            str(self.script_dir / "generate_html_report_v2.py"),
            digest_file,
            report_file,
        ]
        if hospital_name:
            cmd += ["--hospital", hospital_name]
        if service:
            cmd += ["--service", service]
        # 传入日志文件路径（用于完整链路日志展示）
        log_file = digest_file.replace('_digest.json', '.log')
        if Path(log_file).exists():
            cmd += ["--log-file", log_file]
            cmd += ["--service", service]
        
        print(f"[需求] 正在生成报告...")
        
        result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"报告生成失败:\n{result.stderr}")
        
        print(f"[成功] 报告生成完成: {report_file}")
        return report_file
    
    def push_to_feishu(self, report_file: str, digest_file: str, 
                       target_user: Optional[str] = None):
        """
        推送报告到飞书
        这个方法需要通过 OpenClaw 的 message 工具调用
        """
        # 读取 digest 获取摘要信息
        with open(digest_file, 'r', encoding='utf-8') as f:
            digest = json.load(f)
        
        stats = digest.get('summary', {})
        
        # 构建消息
        message = f"""[统计] 日志巡检报告

⏰ 时间范围: {stats.get('start_time', '未知')} ~ {stats.get('end_time', '未知')}
📈 总日志数: {stats.get('total_lines', 0)}
[失败] ERROR: {stats.get('error_count', 0)}
[警告] WARN: {stats.get('warn_count', 0)}
🐌 慢接口: {len(digest.get('slow_apis', []))}

📄 详细报告: {report_file}
"""
        
        print(f"\n{'='*50}")
        print("📤 报告摘要:")
        print(message)
        print(f"{'='*50}\n")
        
        # 注意: 实际推送需要通过 OpenClaw 的 message 工具
        # 这里只是打印消息，实际使用时需要集成 OpenClaw API
        print("[建议] 提示: 使用 OpenClaw message 工具推送到飞书")
        
        return message
    
    def run(self, query: str, push_to_feishu: bool = False, 
            target_user: Optional[str] = None,
            overrides: Optional[Dict] = None):
        """
        执行完整流程
        
        Args:
            query: 自然语言查询
            push_to_feishu: 是否推送到飞书
            target_user: 飞书用户 ID（可选）
        """
        print(f"\n{'='*60}")
        print(f"[启动] 日志巡检任务启动")
        print(f"{'='*60}\n")
        print(f"[需求] 需求: {query}\n")
        
        try:
            # 1. 解析需求
            print("[检测] 解析需求...")
            params = self.parse_natural_language(query)
            if overrides:
                params.update({k: v for k, v in overrides.items() if v is not None})
            print(f"   医院: {params['hospital']}")
            print(f"   服务: {params['service']}")
            if params.get('cluster'):
                print(f"   集群: {params['cluster']}")
            print(f"   时间: {params['start_time']} ~ {params['end_time']}")
            print(f"   级别: {params['level']}\n")
            
            if not params['hospital']:
                raise ValueError("无法识别医院名称，请在查询中包含医院名称")
            
            if not params['service']:
                raise ValueError("无法识别服务名称，请在查询中包含服务名称")
            
            # 2. 拉取日志（第一阶段：ERROR|业务处理耗时）
            log_file = self.fetch_logs(
                params['hospital'],
                params['service'],
                params['start_time'],
                params['end_time'],
                params['level'],
                params.get('cluster')
            )
            print()
            
            # 3. 第一阶段分析（生成代表 traces 列表）
            digest_file = self.analyze_logs(log_file)
            print()
            
            # 4. 第二阶段：拉取代表 traces 完整链路（仅 k8s 类型）
            env_type = self.environments.get(params['hospital'], {}).get('type', '')
            traces_file = digest_file.replace('_digest.json', '_digest_traces.json')
            if env_type == 'k8s' and Path(traces_file).exists():
                import json as _json
                with open(traces_file, 'r', encoding='utf-8') as f:
                    traces_data = _json.load(f)
                trace_count = traces_data.get('count', 0)
                if trace_count > 0:
                    print(f"[两阶段] 开始第二阶段：拉取 {trace_count} 个代表 traces 完整链路...")
                    stage2_cmd = [
                        sys.executable,
                        str(self.script_dir / "loki_fetcher.py"),
                        "--grafana", self._last_grafana_url,
                        "--datasource", str(self._last_datasource_id),
                        "--app", self._last_app_name,
                        "--start", params['start_time'],
                        "--end", params['end_time'],
                        "--output", log_file,
                        "--stage2-traces", traces_file,
                        "--time-window", "60",
                    ]
                    result2 = subprocess.run(stage2_cmd, stderr=subprocess.PIPE, text=True)
                    if result2.returncode == 0:
                        print(f"[两阶段] 第二阶段完成，重新分析...")
                        digest_file = self.analyze_logs(log_file)
                        print()
                    else:
                        print(f"[警告] 第二阶段拉取失败，使用第一阶段结果: {result2.stderr[:200]}")
                else:
                    print("[两阶段] 无代表 traces，跳过第二阶段")
            
            # 5. 生成报告
            report_file = self.generate_report(
                digest_file,
                params['hospital'],
                params['service']
            )
            print()
            
            # 5. 推送到飞书（可选）
            if push_to_feishu:
                self.push_to_feishu(report_file, digest_file, target_user)
            
            print(f"\n{'='*60}")
            print(f"[成功] 任务完成!")
            print(f"{'='*60}\n")
            print(f"📄 报告文件: {report_file}")
            print(f"[统计] 数据文件: {digest_file}")
            print(f"[需求] 日志文件: {log_file}\n")
            
            return {
                'success': True,
                'report_file': report_file,
                'digest_file': digest_file,
                'log_file': log_file
            }
            
        except Exception as e:
            print(f"\n[失败] 任务失败: {str(e)}\n")
            return {
                'success': False,
                'error': str(e)
            }


def main():
    parser = argparse.ArgumentParser(
        description='日志巡检统一入口脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 自然语言查询（单集群医院）
  python log_inspect_main.py "帮我分析乐山病区护士站今天上午8-10点的日志"
  
  # 自然语言查询（多集群医院 - 必须指定集群）
  python log_inspect_main.py "帮我分析桐乡病区护士站第二集群今天上午8-10点的日志"
  
  # 指定参数（多集群）
  python log_inspect_main.py \\
    --hospital 桐乡市卫生健康局 \\
    --service 病区护士站 \\
    --cluster 第二集群 \\
    --start "2026-03-03 08:00" \\
    --end "2026-03-03 10:00"
  
  # 推送到飞书
  python log_inspect_main.py "分析桐乡病区护士站第一集群昨天的日志" --push
        """
    )
    
    parser.add_argument('query', nargs='?', help='自然语言查询')
    parser.add_argument('--hospital', help='医院名称')
    parser.add_argument('--service', help='服务名称')
    parser.add_argument('--cluster', help='集群名称（多集群时必须指定）')
    parser.add_argument('--start', help='开始时间 (YYYY-MM-DD HH:MM)')
    parser.add_argument('--end', help='结束时间 (YYYY-MM-DD HH:MM)')
    parser.add_argument('--level', default='ERROR|业务处理耗时', help='日志级别过滤')
    parser.add_argument('--push', action='store_true', help='推送到飞书')
    parser.add_argument('--user', help='飞书用户 ID')
    parser.add_argument('--config', default='config/environments.json', 
                       help='配置文件路径')
    parser.add_argument('--stage', choices=['fetch', 'fetch2', 'analyze', 'report'],
                       help='只执行指定阶段（供分阶段调用）')
    parser.add_argument('--log-file', help='日志文件路径（analyze/fetch2 阶段使用）')
    parser.add_argument('--digest-file', help='digest 文件路径（report 阶段使用）')
    parser.add_argument('--traces-file', help='代表 traces 文件路径（fetch2 阶段使用）')
    parser.add_argument('--fetch-start', help='拉取开始时间（analyze 阶段使用）')
    parser.add_argument('--fetch-end', help='拉取结束时间（analyze 阶段使用）')
    parser.add_argument('--fetch-duration', help='拉取耗时秒数（analyze 阶段使用）')
    parser.add_argument('--grafana-url', help='Grafana URL（fetch2 阶段使用）')
    parser.add_argument('--datasource-id', help='数据源 ID（fetch2 阶段使用）')
    parser.add_argument('--app-name', help='应用名称（fetch2 阶段使用）')
    
    args = parser.parse_args()
    
    inspector = LogInspector(args.config)
    
    # 分阶段执行模式
    if args.stage == 'fetch':
        # 只拉取日志，输出日志文件路径和拉取元数据
        params = inspector.parse_natural_language(args.query or '')
        overrides = {
            'hospital': args.hospital, 'service': args.service,
            'cluster': args.cluster, 'start_time': args.start,
            'end_time': args.end, 'level': args.level if args.level else None,
        }
        params.update({k: v for k, v in overrides.items() if v is not None})
        log_file = inspector.fetch_logs(
            params['hospital'], params['service'],
            params['start_time'], params['end_time'],
            params['level'], params.get('cluster')
        )
        meta = getattr(inspector, '_last_fetch_meta', {})
        print(f"\nRESULT_LOG_FILE: {log_file}")
        print(f"RESULT_FETCH_START: {meta.get('fetch_start', params['start_time'])}")
        print(f"RESULT_FETCH_END: {meta.get('fetch_end', params['end_time'])}")
        print(f"RESULT_FETCH_DURATION: {meta.get('fetch_duration_s', 0)}")
        print(f"RESULT_GRAFANA_URL: {getattr(inspector, '_last_grafana_url', '')}")
        print(f"RESULT_DATASOURCE_ID: {getattr(inspector, '_last_datasource_id', '')}")
        print(f"RESULT_APP_NAME: {getattr(inspector, '_last_app_name', '')}")
        return

    elif args.stage == 'fetch2':
        # 第二阶段：拉取代表 traces 完整链路
        if not args.log_file or not args.traces_file:
            print("[失败] --stage fetch2 需要 --log-file 和 --traces-file 参数")
            sys.exit(1)
        if not args.grafana_url or not args.datasource_id or not args.app_name:
            print("[失败] --stage fetch2 需要 --grafana-url, --datasource-id, --app-name 参数")
            sys.exit(1)
        import json as _json
        with open(args.traces_file, 'r', encoding='utf-8') as f:
            traces_data = _json.load(f)
        trace_count = traces_data.get('count', 0)
        if trace_count == 0:
            print("[两阶段] 无代表 traces，跳过第二阶段")
            print(f"\nRESULT_LOG_FILE: {args.log_file}")
            return
        print(f"[两阶段] 拉取 {trace_count} 个代表 traces 完整链路...")
        stage2_cmd = [
            sys.executable,
            str(inspector.script_dir / "loki_fetcher.py"),
            "--grafana", args.grafana_url,
            "--datasource", str(args.datasource_id),
            "--app", args.app_name,
            "--start", args.start or '',
            "--end", args.end or '',
            "--output", args.log_file,
            "--stage2-traces", args.traces_file,
            "--time-window", "60",
        ]
        result2 = subprocess.run(stage2_cmd, stderr=subprocess.PIPE, text=True)
        if result2.returncode != 0:
            print(f"[警告] 第二阶段拉取失败: {result2.stderr[:200]}")
            sys.exit(1)
        print(f"\nRESULT_LOG_FILE: {args.log_file}")
        return

    elif args.stage == 'analyze':
        if not args.log_file:
            print("[失败] --stage analyze 需要 --log-file 参数")
            sys.exit(1)
        # 恢复 fetch 元数据（跨进程传递）
        if args.fetch_start or args.fetch_end or args.fetch_duration:
            inspector._last_fetch_meta = {
                'fetch_start': args.fetch_start or '',
                'fetch_end': args.fetch_end or '',
                'fetch_duration_s': int(args.fetch_duration or 0),
            }
        digest_file = inspector.analyze_logs(args.log_file)
        print(f"\nRESULT_DIGEST_FILE: {digest_file}")
        return

    elif args.stage == 'report':
        if not args.digest_file:
            print("[失败] --stage report 需要 --digest-file 参数")
            sys.exit(1)
        hospital = args.hospital or ''
        service = args.service or ''
        report_file = inspector.generate_report(args.digest_file, hospital, service)
        print(f"\nRESULT_REPORT_FILE: {report_file}")
        return

    # 如果提供了自然语言查询
    if args.query:
        overrides = {
            'hospital': args.hospital,
            'service': args.service,
            'cluster': args.cluster,
            'start_time': args.start,
            'end_time': args.end,
            'level': args.level if args.level else None,
        }
        inspector.run(args.query, args.push, args.user, overrides=overrides)
    
    # 如果提供了具体参数
    elif args.hospital and args.service and args.start and args.end:
        query_parts = [f"分析{args.hospital}{args.service}"]
        if args.cluster:
            query_parts.append(args.cluster)
        query_parts.append(f"{args.start}到{args.end}的日志")
        query = " ".join(query_parts)
        overrides = {
            'hospital': args.hospital,
            'service': args.service,
            'cluster': args.cluster,
            'start_time': args.start,
            'end_time': args.end,
            'level': args.level if args.level else None,
        }
        inspector.run(query, args.push, args.user, overrides=overrides)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
