# 日志巡检工具 - 代码恢复脚本
# 恢复升级后丢失的所有修改

import re
import sys

print("开始恢复代码...")

# ===== 1. 恢复 preprocess.py 的四级分组功能 =====
print("\n[1/4] 恢复 preprocess.py...")

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\preprocess.py', encoding='utf-8') as f:
    content = f.read()

# 1a. 添加 extract_caller_service_from_thread 函数（在文件开头，import后面）
if 'extract_caller_service_from_thread' not in content:
    func_code = '''

def extract_caller_service_from_thread(thread: str) -> str:
    """从线程名提取调用方服务"""
    import re
    
    # 跨服务调用：winning-winex-xxx_Jetty-Worker
    service_match = re.search(r'^(winning-winex-[a-z0-9-]+)_Jetty-Worker', thread)
    if service_match:
        return service_match.group(1)
    
    # 本服务调用：Jetty-Worker_xxx
    if thread.startswith('Jetty-Worker_'):
        return 'SELF'
    
    # 异步任务：exe-xxx, enc-xxx
    if re.match(r'^(exe|enc)-\\d+$', thread):
        return 'ASYNC'
    
    # RPC调用：rpc-exec-xxx
    if thread.startswith('rpc-exec-'):
        return 'RPC'
    
    return 'UNKNOWN'

'''
    # 在第一个函数定义前插入
    idx = content.find('def ')
    if idx > 0:
        content = content[:idx] + func_code + content[idx:]
        print("  ✓ 添加 extract_caller_service_from_thread 函数")

# 1b. 修改 categorize_trace 函数，添加 caller_service 提取
# 这个比较复杂，需要找到函数并修改所有return语句
# 简化方案：检查是否已有caller_service字段
if 'caller_service' not in content or content.count("'caller_service':") < 5:
    print("  ⚠ categorize_trace 需要手动修改（添加 caller_service 到所有 return）")
    print("    建议：从旧版本复制整个 categorize_trace 函数")

# 1c. 修改 aggregate_errors 的分组键
old_key = "key = f\"{err['category']}:{err.get('root_class', 'N/A')}:{err.get('api_entry', 'N/A')}\""
new_key = "key = f\"{err['category']}:{err.get('root_class', 'N/A')}:{err.get('api_entry', 'N/A')}:{err.get('caller_service', 'UNKNOWN')}\""

if old_key in content:
    content = content.replace(old_key, new_key)
    print("  ✓ 修改 aggregate_errors 分组键为四级")

# 1d. 添加 representative_traces 支持
if 'representative_traces' not in content:
    # 在 process_file 开头读取代表trace列表
    old = '''def process_file(file_path: str, start_time: datetime = None, end_time: datetime = None) -> Dict:
    """处理单个日志文件"""
    stats = {'''
    
    new = '''def process_file(file_path: str, start_time: datetime = None, end_time: datetime = None) -> Dict:
    """处理单个日志文件"""
    
    # 读取代表trace列表（如果存在）
    representative_traces = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if 'REPRESENTATIVE_TRACES:' in first_line:
                traces_str = first_line.split('REPRESENTATIVE_TRACES:')[1].strip()
                representative_traces = set(traces_str.split(','))
    except:
        pass
    
    stats = {'''
    
    if old in content:
        content = content.replace(old, new)
        print("  ✓ 添加代表trace列表读取")

# 1e. 修改 aggregate_errors 调用，传入 representative_traces
old_call = "aggregated_errors = aggregate_errors(stats['error_samples'])"
new_call = "aggregated_errors = aggregate_errors(stats['error_samples'], stats.get('representative_traces', set()))"

if old_call in content:
    content = content.replace(old_call, new_call)
    print("  ✓ 修改 aggregate_errors 调用")

# 1f. 修改 aggregate_errors 函数签名
old_sig = "def aggregate_errors(error_samples: List[Dict]) -> List[Dict]:"
new_sig = "def aggregate_errors(error_samples: List[Dict], representative_traces: set = None) -> List[Dict]:"

if old_sig in content:
    content = content.replace(old_sig, new_sig)
    print("  ✓ 修改 aggregate_errors 函数签名")

# 1g. 在 aggregate_errors 中优先插入代表trace
# 这个需要找到添加samples的地方
old_add = '''        if len(error_groups[key]['samples']) < 3:
            error_groups[key]['samples'].append(err)'''

new_add = '''        # 优先添加代表trace，然后添加其他trace（最多3个）
        trace_id = err.get('trace_id')
        if representative_traces and trace_id and trace_id in representative_traces:
            # 如果是代表trace，插入到最前面
            error_groups[key]['samples'].insert(0, err)
            # 保持最多3个samples
            if len(error_groups[key]['samples']) > 3:
                error_groups[key]['samples'] = error_groups[key]['samples'][:3]
        elif len(error_groups[key]['samples']) < 3:
            error_groups[key]['samples'].append(err)'''

if old_add in content:
    content = content.replace(old_add, new_add)
    print("  ✓ 添加代表trace优先逻辑")

with open(r'C:\Users\pc\.openclaw\workspace\skills\log-inspect\preprocess.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("  ✓ preprocess.py 恢复完成")

print("\n由于修改过多，建议手动检查以下内容：")
print("  1. categorize_trace 函数的所有 return 是否包含 caller_service")
print("  2. process_file 中 error_line 是否传递了 caller_service 和 thread")
print("\n继续恢复其他文件...")
