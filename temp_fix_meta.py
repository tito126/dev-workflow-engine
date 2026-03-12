import re

# ===== 1. 修改 log_inspect_main.py =====
# 在 _fetch_from_loki 中记录拉取开始/结束时间，传给 analyze_logs
# 在 analyze_logs 中接收并传给 preprocess.py

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\log_inspect_main.py', encoding='utf-8') as f:
    content = f.read()

# 1a. 在 subprocess.run(cmd, capture_output=True...) 前后加时间记录
old = '''            print(f"[检测] 正在拉取日志...")
            print(f"   医院: {env.get('name', '未知')}")
            print(f"   集群: {cluster_name}")
            print(f"   服务: {service} ({app_name})")
            print(f"   时间: {start_time} ~ {end_time}")
            print(f"   级别: {level}")
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)'''

new = '''            print(f"[检测] 正在拉取日志...")
            print(f"   医院: {env.get('name', '未知')}")
            print(f"   集群: {cluster_name}")
            print(f"   服务: {service} ({app_name})")
            print(f"   时间: {start_time} ~ {end_time}")
            print(f"   级别: {level}")
            
            fetch_start_ts = datetime.now()
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)'''

content = content.replace(old, new)

# 1b. 在成功后记录结束时间，存到 self._last_fetch_meta
old = '''                if output_file.exists() and output_file.stat().st_size > 0:
                    print(f"[成功] 日志拉取完成: {output_file}")
                    log_files.append(str(output_file))'''

new = '''                if output_file.exists() and output_file.stat().st_size > 0:
                    fetch_end_ts = datetime.now()
                    fetch_duration_s = int((fetch_end_ts - fetch_start_ts).total_seconds())
                    self._last_fetch_meta = {
                        'fetch_start': start_time,
                        'fetch_end': end_time,
                        'fetch_duration_s': fetch_duration_s
                    }
                    print(f"[成功] 日志拉取完成: {output_file}")
                    log_files.append(str(output_file))'''

content = content.replace(old, new)

# 1c. 在 analyze_logs 中传入 fetch_meta 参数
old = '''    def analyze_logs(self, log_file: str, threshold: int = 1000) -> str:
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
        ]'''

new = '''    def analyze_logs(self, log_file: str, threshold: int = 1000) -> str:
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
            cmd += ["--fetch-duration", str(fetch_meta.get('fetch_duration_s', 0))]'''

content = content.replace(old, new)

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\log_inspect_main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("log_inspect_main.py 修改完成")

# ===== 2. 修改 preprocess.py =====
# 添加 --fetch-start/--fetch-end/--fetch-duration 参数，写入 meta

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\preprocess.py', encoding='utf-8') as f:
    content = f.read()

# 找到 argparse 的 add_argument 部分，在 -t 后面加新参数
old = '''    parser.add_argument('-t', '--threshold', type=int, default=1000,
                        help='慢接口阈值（毫秒）')'''

new = '''    parser.add_argument('-t', '--threshold', type=int, default=1000,
                        help='慢接口阈值（毫秒）')
    parser.add_argument('--fetch-start', type=str, default='',
                        help='日志拉取开始时间')
    parser.add_argument('--fetch-end', type=str, default='',
                        help='日志拉取结束时间')
    parser.add_argument('--fetch-duration', type=int, default=0,
                        help='日志拉取耗时（秒）')'''

content = content.replace(old, new)

# 找到 meta 写入的地方，加入 fetch 信息
old = '''        'meta': {
            'generated_at': datetime.now().isoformat(),
            'files_processed': [str(input_file)],
            'time_range': {
                'start': args.start if hasattr(args, 'start') else None,
                'end': args.end if hasattr(args, 'end') else None
            },
            'slow_threshold_ms': args.threshold,'''

new = '''        'meta': {
            'generated_at': datetime.now().isoformat(),
            'files_processed': [str(input_file)],
            'time_range': {
                'start': args.start if hasattr(args, 'start') else None,
                'end': args.end if hasattr(args, 'end') else None
            },
            'fetch_range': {
                'start': args.fetch_start if args.fetch_start else None,
                'end': args.fetch_end if args.fetch_end else None,
                'duration_s': args.fetch_duration if args.fetch_duration else None
            },
            'slow_threshold_ms': args.threshold,'''

if old in content:
    content = content.replace(old, new)
    print("preprocess.py meta 修改成功")
else:
    # 尝试找到 meta 写入的另一种形式
    print("未找到精确匹配，搜索 meta 写入位置...")
    idx = content.find("'generated_at': datetime.now().isoformat()")
    if idx > 0:
        print(f"找到 generated_at 在位置 {idx}")
        print(content[idx-200:idx+300])

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\preprocess.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("preprocess.py 修改完成")
