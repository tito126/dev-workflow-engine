with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到启发式规则的位置，调整顺序
new_lines = []
sql_line = None
null_line = None

for i, line in enumerate(lines):
    if "('sql_error'," in line:
        sql_line = i
    elif "('null_pointer'," in line:
        null_line = i

# 如果找到了，且SQL在空指针之后，交换它们
if sql_line and null_line and sql_line > null_line:
    # 交换两行
    lines[sql_line], lines[null_line] = lines[null_line], lines[sql_line]
    print(f"交换了第 {null_line+1} 行和第 {sql_line+1} 行")
    
    with open(r'D:\nvm\v24.9.0\node_modules\openclaw\skills\log-inspect\preprocess.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("已调整SQL错误优先级")
else:
    print(f"sql_line={sql_line}, null_line={null_line}")
