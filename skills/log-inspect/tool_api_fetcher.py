#!/usr/bin/env python3
"""
工具组 API 日志拉取器
用于从传统服务器环境通过工具组 API 获取日志
"""

import os
import sys
import json
import requests
import zipfile
import gzip
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List


class ToolAPIFetcher:
    """工具组 API 日志拉取器"""
    
    def __init__(self, api_base_url: str):
        """
        初始化
        
        Args:
            api_base_url: API 基础 URL (例如: http://172.16.9.87:8089)
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def get_nodes(self, code: str, app_id: str) -> List[Dict]:
        """
        查询服务节点列表
        GET /api/v1/wincode/faultlocation/getServicesByCodeOrAppid
        
        Returns:
            节点列表，每项含 id, ip, port, name, code, appid
        """
        url = f"{self.api_base_url}/api/v1/wincode/faultlocation/getServicesByCodeOrAppid"
        try:
            r = self.session.get(url, params={"code": code, "appid": app_id}, timeout=15)
            r.encoding = "utf-8"
            r.raise_for_status()
            result = r.json()
            if result.get("success") and result.get("data"):
                return result["data"]
            print(f"[警告] getServicesByCodeOrAppid 返回异常: {result.get('message')}")
            return []
        except requests.exceptions.RequestException as e:
            print(f"[失败] 查询节点列表失败: {e}")
            return []

    def fetch_logs(self, app_id: str, env_id: str, program_name: str,
                   node_id: str, start_time: str, end_time: Optional[str] = None,
                   log_type: str = "all", output_dir: str = ".") -> str:
        """
        拉取日志
        
        Args:
            app_id: 应用 ID
            env_id: 环境 ID
            program_name: 程序名称（code）
            node_id: 节点 ID
            start_time: 开始时间 (YYYY-MM-DD HH:MM:SS)
            end_time: 结束时间 (YYYY-MM-DD HH:MM:SS)
            log_type: 日志类型，默认 all（后续可扩展 gc）
            output_dir: 输出目录
        
        Returns:
            合并后的日志文件路径
        """
        print(f"[工具组] 正在从工具组 API 拉取日志...")
        print(f"   节点 ID: {node_id}")
        print(f"   程序名称: {program_name}")
        print(f"   时间: {start_time} ~ {end_time}")
        print(f"   类型: {log_type}")
        
        download_url = self._get_download_url(app_id, env_id, program_name, node_id, start_time, log_type=log_type)
        
        if not download_url:
            raise RuntimeError("获取下载地址失败")
        
        print(f"[成功] 获取下载地址成功")
        
        # 2. 下载日志压缩包
        zip_file = self._download_logs(download_url, output_dir)
        print(f"[成功] 日志下载完成: {zip_file}")
        
        # 3. 解压日志文件
        log_files = self._extract_logs(zip_file, output_dir)
        print(f"[成功] 日志解压完成，共 {len(log_files)} 个文件")
        
        # 4. 合并日志文件（如果有多个节点）
        merged_file = self._merge_logs(log_files, output_dir, program_name)
        print(f"[成功] 日志合并完成: {merged_file}")
        
        # 5. 清理临时文件
        self._cleanup(zip_file, log_files)
        
        return merged_file
    
    def _get_download_url(self, app_id: str, env_id: str, program_name: str,
                          node_id: str, start_time: str, end_time: Optional[str] = None,
                          log_type: str = "all") -> Optional[str]:
        """
        调用 getServiceLogs 获取下载地址
        工具组已修复 endTime 问题，按开始/结束时间拉取指定时间窗日志
        """
        api_url = f"{self.api_base_url}/api/v1/wincode/faultlocation/getServiceLogs"
        
        payload = {
            "appId": app_id,
            "envId": env_id,
            "programName": program_name,
            "nodeId": node_id,
            "startTime": start_time,
            "type": log_type,
        }
        if end_time:
            payload["endTime"] = end_time
        
        try:
            response = self.session.post(api_url, json=payload, timeout=30)
            response.raise_for_status()
            
            if not response.content:
                print(f"[失败] getServiceLogs 返回空响应，可能该时间段无日志或 envId 不匹配")
                return None
            
            result = response.json()
            
            if result.get('success') and result.get('data'):
                download_path = result['data']
                # 如果返回的已经包含主机地址，直接使用
                if download_path.startswith('http'):
                    download_url = download_path
                # 如果返回的包含主机但没有协议，添加协议
                elif ':' in download_path and '/' in download_path:
                    download_url = f"http://{download_path}"
                # 如果是纯相对路径，拼接完整 URL
                else:
                    download_url = f"{self.api_base_url}/{download_path}"
                return download_url
            else:
                error_msg = result.get('message', '未知错误')
                print(f"[失败] API 调用失败: {error_msg}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"[失败] API 请求异常: {str(e)}")
            return None
    
    def _download_logs(self, download_url: str, output_dir: str) -> str:
        """
        下载日志压缩包
        
        Returns:
            下载的文件路径
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成临时文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_file = output_dir / f"logs_{timestamp}.zip"
        
        try:
            print(f"[检测] 正在下载日志文件...")
            response = self.session.get(download_url, stream=True, timeout=300)
            response.raise_for_status()
            
            # 获取文件大小
            total_size = int(response.headers.get('content-length', 0))
            
            # 下载文件
            with open(zip_file, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r[检测] 下载进度: {progress:.1f}%", end='')
            
            print()  # 换行
            return str(zip_file)
            
        except requests.exceptions.RequestException as e:
            print(f"[失败] 下载失败: {str(e)}")
            raise
    
    def _extract_logs(self, zip_file: str, output_dir: str) -> List[str]:
        """
        解压日志文件
        
        Returns:
            解压后的日志文件路径列表
        """
        output_dir = Path(output_dir)
        extract_dir = output_dir / "extracted_logs"
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        log_files = []
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # 查找所有日志文件（包括 .log 和 .gz）
            for file_path in extract_dir.rglob('*'):
                if file_path.is_file():
                    if file_path.suffix == '.log':
                        log_files.append(str(file_path))
                    elif file_path.suffix == '.gz':
                        # 解压 .gz 文件
                        decompressed = self._decompress_gz(file_path)
                        if decompressed:
                            log_files.append(decompressed)
            
            return log_files
            
        except Exception as e:
            print(f"[失败] 解压失败: {str(e)}")
            raise
    
    def _decompress_gz(self, gz_file: Path) -> Optional[str]:
        """
        解压 .gz 文件
        
        Returns:
            解压后的文件路径
        """
        try:
            output_file = gz_file.with_suffix('')  # 移除 .gz 后缀
            
            with gzip.open(gz_file, 'rb') as f_in:
                with open(output_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            return str(output_file)
            
        except Exception as e:
            print(f"[警告]  解压 {gz_file.name} 失败: {str(e)}")
            return None
    
    def _merge_logs(self, log_files: List[str], output_dir: str, 
                    program_name: str) -> str:
        """
        合并多个日志文件
        
        Returns:
            合并后的日志文件路径
        """
        if not log_files:
            raise ValueError("没有日志文件可合并")
        
        # 如果只有一个文件，移出 extracted_logs 目录再返回
        if len(log_files) == 1:
            src = Path(log_files[0])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dst = Path(output_dir) / f"logs_{timestamp}_{program_name}.log"
            shutil.move(str(src), str(dst))
            return str(dst)
        
        # 生成合并后的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        merged_file = Path(output_dir) / f"logs_{timestamp}_{program_name}.log"
        
        print(f"[检测] 正在合并 {len(log_files)} 个日志文件...")
        
        try:
            with open(merged_file, 'w', encoding='utf-8', errors='ignore') as outfile:
                for log_file in sorted(log_files):
                    print(f"   - {Path(log_file).name}")
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as infile:
                        outfile.write(infile.read())
                        outfile.write('\n')  # 确保文件之间有换行
            
            return str(merged_file)
            
        except Exception as e:
            print(f"[失败] 合并失败: {str(e)}")
            raise
    
    def _cleanup(self, zip_file: str, log_files: List[str]):
        """
        清理临时文件
        """
        try:
            # 删除 zip 文件
            if os.path.exists(zip_file):
                os.remove(zip_file)
            
            # 删除解压目录
            if log_files:
                extract_dir = Path(log_files[0]).parent
                if extract_dir.exists() and extract_dir.name == "extracted_logs":
                    shutil.rmtree(extract_dir)
            
            print(f"[成功] 临时文件清理完成")
            
        except Exception as e:
            print(f"[警告]  清理临时文件失败: {str(e)}")


def main():
    """测试入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='工具组 API 日志拉取器')
    parser.add_argument('--api-url', required=True, help='API 基础 URL')
    parser.add_argument('--app-id', required=True, help='应用 ID')
    parser.add_argument('--env-id', required=True, help='环境 ID')
    parser.add_argument('--program', required=True, help='程序名称')
    parser.add_argument('--node-id', required=True, help='节点 ID')
    parser.add_argument('--start-time', required=True, help='开始时间')
    parser.add_argument('--end-time', required=True, help='结束时间')
    parser.add_argument('--log-type', default='all', help='日志类型 (all/gc)')
    parser.add_argument('--output', default='.', help='输出目录')
    
    args = parser.parse_args()
    
    fetcher = ToolAPIFetcher(args.api_url)
    
    try:
        log_file = fetcher.fetch_logs(
            args.app_id,
            args.env_id,
            args.program,
            args.node_id,
            args.start_time,
            args.end_time,
            args.log_type,
            args.output
        )
        
        print(f"\n[成功] 日志拉取成功: {log_file}")
        
    except Exception as e:
        print(f"\n[失败] 日志拉取失败: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
