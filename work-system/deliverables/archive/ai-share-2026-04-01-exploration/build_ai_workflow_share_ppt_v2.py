import copy
import os
import shutil
import zipfile
import xml.etree.ElementTree as ET

BASE = r"C:\Users\pc\.openclaw\workspace\work-system\deliverables"
TEMPLATE = r"D:\飞书\download\异常信息提示培训.pptx"
TARGET = os.path.join(BASE, "ai-workflow-share-2026-04-01-v2.pptx")
OUTLINE = os.path.join(BASE, "ai-workflow-share-2026-04-01-v2-notes.md")

ns = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}
for prefix, uri in ns.items():
    ET.register_namespace(prefix, uri)

slides = {
    1: [
        "从消息流到工作流",
        "AI 如何把零散协作变成持续推进",
        "分享人：第别",
        "2026年4月",
        "卫宁健康",
    ],
    2: [
        "目录",
        "为什么不是只做聊天 AI",
        "01",
        "四层协作链路怎么搭起来",
        "02",
        "日志猎人案例怎么把链路跑通",
        "03",
        "边界、教训与下一步",
        "04",
    ],
    3: [
        "目录",
        "为什么不是只做聊天 AI",
        "01",
        "问题不是 AI 会不会答",
        "1",
    ],
    4: [
        "我们真正遇到的问题，不是 AI 回答得够不够聪明，而是很多工作天然发生在聊天里：需求确认、专项推进、提醒、会议结论、经验教训都会经过消息流。消息流的问题也很明显——容易散、容易断、第二天不容易无损接上。",
        "总览",
        "为什么不是只做聊天 AI",
        "原问题",
    ],
    5: [
        "四层协作链路说明",
        "结构",
        "为什么不是只做聊天 AI",
        "1.work-control：入口层 / 路由层，决定信息怎么进\n2.work-system：执行层 / 运行层，决定事情怎么跑\n3.executor：执行承接层，复杂任务再通过 ACP 连到 Codex\n4.memory + cognition：负责把历史找回来、把规则沉淀下来",
        "全景图",
    ],
    6: [
        "目录",
        "四层协作链路怎么搭起来",
        "02",
        "从接信息到可持续推进",
        "2",
    ],
    7: [
        "第一层：work-control   - 信息怎么进",
        "路由",
        "四层协作链路怎么搭起来",
        "1. 先判断一句话是临时事项、专项、提醒，还是需要补追问\n2. 避免一上来就把模糊信息硬塞进系统\n3. 核心作用：把聊天里的有效输入正确送到该去的地方",
    ],
    8: [
        "第二层：work-system  - 事情怎么跑",
        "运行",
        "四层协作链路怎么搭起来",
        "1. 承接 Daily Focus、Daily Summary、项目档案、风险、里程碑、交付物\n2. 让事情不再只停留在“聊过了”，而是能今天推进、明天续上、以后回看\n3. 核心作用：把零散协作变成可追踪、可持续的工作流",
    ],
    9: [
        "第三层：executor + ACP + Codex  - 复杂任务怎么被稳定执行",
        "执行",
        "四层协作链路怎么搭起来",
        "1. 主会话负责判断和收口，不直接陷进所有执行细节\n2. executor 负责把问题转成可持续处理的执行任务\n3. 事故驱动、多模块代码追踪、需要结构化结论时，再通过 ACP 连 Codex\n4. 结果必须回写共享区，否则第二天容易断片",
    ],
    10: [
        "第四层：memory_search + gguf + cognition-system",
        "记忆",
        "四层协作链路怎么搭起来",
        "1. 记忆检索解决的不是“搜文件更快”，而是找得到、少漏、接得上\n2. 本地 gguf 向量模型支撑长期记忆的语义召回\n3. cognition-system 不记感想，沉淀的是可复用的判断规则、教训和迁移经验",
    ],
    11: [
        "谢谢观看",
    ],
}

notes_md = """# AI 分享 v2 备注

## 建议讲法
- 先用“聊天里的工作信息为什么会散”开场
- 再讲四层协作链路，而不是功能清单
- `executor` 要明确讲成执行承接层，不只是又一个 agent
- `gguf` 要讲成记忆召回底座，不要讲成炫技术点
- `日志猎人` 适合在现场口头展开，特别是中江事故驱动案例

## 这版 PPT 特点
- 完全沿用模板样式
- 先做内容导向的首版排布
- 页数与模板一致，便于后续继续替换和精修
"""


def build_paragraph(template_p, text):
    p = copy.deepcopy(template_p)
    for child in list(p):
        if child.tag != f"{{{ns['a']}}}pPr":
            p.remove(child)
    if text:
        runs = template_p.findall("a:r", ns)
        if runs:
            run_template = runs[0]
            r = ET.Element(f"{{{ns['a']}}}r")
            rPr = run_template.find("a:rPr", ns)
            if rPr is not None:
                r.append(copy.deepcopy(rPr))
            t = ET.Element(f"{{{ns['a']}}}t")
            t.text = text
            r.append(t)
            p.append(r)
        else:
            r = ET.Element(f"{{{ns['a']}}}r")
            r.append(ET.Element(f"{{{ns['a']}}}rPr"))
            t = ET.Element(f"{{{ns['a']}}}t")
            t.text = text
            r.append(t)
            p.append(r)
    end = template_p.find("a:endParaRPr", ns)
    if end is not None:
        p.append(copy.deepcopy(end))
    return p


def set_shape_text(sp, lines):
    tx_body = sp.find("p:txBody", ns)
    paragraphs = tx_body.findall("a:p", ns)
    template_p = paragraphs[0]
    for paragraph in paragraphs:
        tx_body.remove(paragraph)
    for line in lines:
        tx_body.append(build_paragraph(template_p, line))


def iter_text_shapes(root):
    for sp in root.findall('.//p:sp', ns):
        if sp.find('p:txBody', ns) is not None:
            yield sp


shutil.copyfile(TEMPLATE, TARGET)
with zipfile.ZipFile(TARGET, 'r') as zin:
    payload = {name: zin.read(name) for name in zin.namelist()}

for idx, lines in slides.items():
    path = f"ppt/slides/slide{idx}.xml"
    root = ET.fromstring(payload[path])
    text_shapes = list(iter_text_shapes(root))
    for shape, text in zip(text_shapes, lines):
        set_shape_text(shape, text.split("\n"))
    payload[path] = ET.tostring(root, encoding='utf-8', xml_declaration=True)

with zipfile.ZipFile(TARGET, 'w', zipfile.ZIP_DEFLATED) as zout:
    for name, data in payload.items():
        zout.writestr(name, data)

with open(OUTLINE, 'w', encoding='utf-8') as f:
    f.write(notes_md)

print(TARGET)
print(OUTLINE)
