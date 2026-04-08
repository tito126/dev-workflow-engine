import copy
import os
import shutil
import zipfile
import xml.etree.ElementTree as ET

BASE = r"C:\Users\pc\.openclaw\workspace\work-system\deliverables"
TEMPLATE = r"E:\winning-code\ai\WiN学院-病区护士站_v1.pptx"
TARGET = os.path.join(BASE, "ai-workflow-share-win-template-2026-04-01-v1.pptx")
NOTES = os.path.join(BASE, "ai-workflow-share-win-template-2026-04-01-v1-notes.md")

ns = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}
for prefix, uri in ns.items():
    ET.register_namespace(prefix, uri)

slides = {
    1: [
        "2026.04.02",
        "从消息流到工作流",
        "AI / 协作系统实践分享  第别",
    ],
    2: [
        "W\ni\nN\n学\n院",
        "从消息流到工作流\nAI 如何把零散协作变成持续推进\n01 为什么不是只做聊天 AI\n02 四层协作链路如何跑起来\n03 日志猎人案例、教训与边界",
    ],
    3: [
        "问题重构",
        "PART 01",
    ],
    4: [
        "很多工作天然发生在聊天里：需求确认、专项推进、提醒、会议结论、经验教训都会经过消息流。\n\n真正的问题不是 AI 会不会答，而是消息流天然容易散、容易断、第二天不容易无损接上。\n\n所以我们要解决的，不是让 AI 更会聊天，而是让聊天里的信息能够被接住、被推进、被回写、被复用。",
    ],
    5: [
        "协作链路",
        "PART 02",
    ],
    6: [
        "这套机制后来逐步长成四层。\n\n第一层是 work-control：负责把聊天里的信息接住、分流、归类、追问，决定信息怎么进。\n\n第二层是 work-system：承接 Daily Focus、Daily Summary、项目档案、风险、里程碑和交付物，决定事情怎么跑。\n\n第三层是 executor：主会话负责判断和收口，复杂任务再交给 executor 承接，需要时通过 ACP 连到 Codex 做深度执行，决定复杂任务怎么被稳定处理。\n\n第四层是 memory_search + gguf + cognition-system：一层负责把历史上下文重新找回来，做到找得到、少漏、接得上；另一层负责把协作中的规律、教训和迁移经验沉淀为规则，让以后做得更准。",
    ],
    7: [
        "案例与反思",
        "PART 03",
    ],
    8: [
        "日志猎人是这套链路开始跑起来的最好案例。\n\n它一开始只是日志巡检项目，后来开始长出主专项、子任务扩展和共享回写。比如围绕中江病区护士站节点 down，并没有停留在“看看代码”，而是先由主会话收口目标，再由 executor 承接，再通过 ACP 连到 Codex 做多模块源码追踪，最后产出正式分析报告并回写专项。\n\n这套机制带来的变化，不是抽象的“效率更高”，而是任务不那么容易断片，复杂问题能从临时讨论变成可接力的正式产物。\n\n当然它也有边界：不是所有任务都值得 agent 化；简单任务直接在主会话完成更轻。升级过程中踩过 workspace 污染、升级覆盖、回写不及时等坑，也让我们更清楚：真正重要的不是工具多，而是协作规则稳。",
    ],
    9: [
        "谢谢聆听",
    ],
}

notes_md = """# WiN 模板版 PPT 备注

## 页面对应
1. 封面
2. 目录
3. Part 01 扉页
4. 原问题页
5. Part 02 扉页
6. 四层协作链路页
7. Part 03 扉页
8. 日志猎人案例 + 教训边界页
9. 结束页

## 使用建议
- 这版更像正式分享版式，章节感比上一版强
- 第 6 页和第 8 页是信息密度最高的两页，现场讲的时候要靠口播节奏拆开
- 如果后续需要，可以继续做 v2：拆分第 6 / 8 页为更多案例页或结构图页
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
    if not paragraphs:
        return
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

with open(NOTES, 'w', encoding='utf-8') as f:
    f.write(notes_md)

print(TARGET)
print(NOTES)
