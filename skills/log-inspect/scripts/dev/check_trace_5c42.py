import json, sys
target = '5C425EBBF16E33C947734860E33A2161'

with open('logs_20260313_183656_第二集群_digest.json', encoding='utf-8') as f:
    digest = json.load(f)

with open('logs_20260313_183656_第二集群_digest_traces.json', encoding='utf-8') as f:
    traces = json.load(f)

# 在 traces 文件里找
found_in_traces = False
for t in traces.get('traces', []):
    if target.lower() in t.get('trace_id', '').lower():
        print(f"traces文件中找到: type={t.get('type')}, trace_id={t.get('trace_id')}")
        found_in_traces = True
        break
if not found_in_traces:
    print("traces文件中未找到该trace")

# 统计日志文件里这个trace有多少条
count = 0
with open('logs_20260313_183656_第二集群.log', encoding='utf-8', errors='ignore') as f:
    for line in f:
        if target.lower() in line.lower():
            count += 1
print(f"日志文件中包含该trace的行数: {count}")
