import copy
import os
import shutil
import zipfile
import xml.etree.ElementTree as ET

BASE = r"C:\Users\pc\.openclaw\workspace\work-system\deliverables"
TEMPLATE = r"D:\飞书\download\异常信息提示培训.pptx"
TARGET = os.path.join(BASE, "ai-workflow-share-2026-04-01-v1.pptx")
OUTLINE = os.path.join(BASE, "ai-workflow-share-2026-04-01-v1-outline.md")

ns = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
for prefix, uri in ns.items():
    ET.register_namespace(prefix, uri)

slides = {
    1: {
        "title": "从消息流到工作流",
        "body": [
            "AI 如何把零散协作变成持续推进",
            "第别",
            "2026-04-02",
        ],
    },
    2: {
        "title": "为什么要做这件事",
        "body": [
            "很多工作天然发生在聊天里：需求、提醒、会议结论、专项推进、经验教训",
            "但消息流的问题也很明显：容易散、容易断、第二天不容易无损接上",
            "真正缺的不是更会聊天的 AI，而是能把聊天信息接成持续推进工作流的机制",
        ],
    },
    3: {
        "title": "整体结构：四层协作链路",
        "body": [
            "work-control：入口层 / 路由层，决定信息怎么进",
            "work-system：执行层 / 运行层，决定事情怎么跑",
            "executor：执行承接层，决定复杂任务怎么被稳定执行",
            "cognition-system：反思层 / 规则层，决定以后怎么跑得更准",
        ],
    },
    4: {
        "title": "第一层：work-control",
        "body": [
            "负责把聊天里的信息接住、分流、归类、追问",
            "判断一句话是临时事项、专项、提醒，还是需要进一步澄清",
            "核心价值：把消息正确送到该去的地方，避免一上来就混乱入库",
        ],
    },
    5: {
        "title": "第二层：work-system",
        "body": [
            "承接 Daily Focus、Daily Summary、项目档案、里程碑、风险、交付物",
            "让事情不再只停留在“聊过了”，而是能今天推进、明天续上、以后回看",
            "核心价值：把零散协作变成可追踪、可持续的工作流",
        ],
    },
    6: {
        "title": "第三层：executor + ACP + Codex",
        "body": [
            "主会话负责判断和收口，不直接陷入所有执行细节",
            "executor 负责把已收口的问题，转成可持续处理的执行任务",
            "当任务进入事故驱动、多模块代码追踪、需要结构化产出时，再通过 ACP 连到 Codex",
            "核心价值：让复杂任务有明确入口、执行链路和结果出口",
        ],
    },
    7: {
        "title": "第四层：记忆与认知",
        "body": [
            "memory_search + 本地 gguf 向量模型：负责跨天、跨主题把相关上下文重新找回来",
            "它解决的不是“搜文件更快”，而是“找得到、少漏、接得上”",
            "cognition-system 不记录感想，而是沉淀可复用的判断规则、易错点和迁移经验",
        ],
    },
    8: {
        "title": "案例：日志猎人如何跑起来",
        "body": [
            "日志猎人不只是一个日志巡检项目，而是已经长出主专项 + 子任务扩展 + 回写沉淀",
            "围绕中江病区护士站节点 down，问题被挂回专项并拆成事故驱动分析任务",
            "主会话收口目标，executor 承接执行，ACP 连接 Codex 做多模块源码追踪",
            "最后形成正式分析报告和项目更新，而不是停留在聊天记录里",
        ],
    },
    9: {
        "title": "这套机制带来的真实变化",
        "body": [
            "任务不那么容易断片，第二天更容易续上",
            "复杂问题能从“临时聊聊”变成“可接力的正式产物”",
            "经验和教训不只服务当前任务，还能反哺后续专项和协作判断",
            "AI 的角色从回答问题，开始进入收口、承接、执行、回写、复盘的完整链路",
        ],
    },
    10: {
        "title": "边界与教训",
        "body": [
            "不是所有任务都值得 agent 化，简单任务直接在主会话完成更轻",
            "executor / Codex 适合事故驱动、多模块上下文、需要形成方案草案的任务",
            "升级和维护过程踩过坑：workspace 污染、升级覆盖、回写不及时都会导致断片",
            "真正重要的不是接了多少工具，而是有没有形成稳定可复用的协作规则",
        ],
    },
    11: {
        "title": "总结",
        "body": [
            "这不是一组零散功能，而是一条从输入、承接、执行、回写、记忆到反思的协作链路",
            "work-control 管信息怎么进，work-system 管事情怎么跑",
            "executor 管复杂任务怎么被稳定执行，cognition-system 管以后怎么跑得更准",
            "AI 真正的价值，不只是回答问题，而是开始进入协作结构本身",
        ],
    },
}

notes = {
    1: "大家好，今天这次分享我想讲的，不是 AI 又多会了什么，而是我怎么把 AI 从聊天工具，慢慢变成一个能承接工作推进的协作系统。",
    2: "我们平时很多工作其实都发生在聊天里。需求确认、专项推进、会议结论、临时提醒、经验教训，都会经过消息流。但消息流天然容易散、容易断、第二天不容易无损接上。所以真正缺的不是更会聊天的 AI，而是能把聊天信息接成持续推进工作流的机制。",
    3: "后来这套东西逐步长成了四层。第一层是 work-control，管入口和路由；第二层是 work-system，管正式承接和推进；第三层是 executor，负责复杂任务的执行承接；第四层是 cognition-system，负责把协作里验证过的规律沉淀成规则。这样它就不是一堆功能，而是一条完整链路。",
    4: "先说 work-control。它解决的是聊天里的信息怎么进。不是所有一句话都应该直接记成项目，也不是所有提醒都值得立刻升级成专项。work-control 的作用，就是做接入、分流、归类和必要追问，把消息正确送到该去的地方。",
    5: "只有路由还不够，信息被接住后还要真的跑起来。所以又有了 work-system。它承接 Daily Focus、Daily Summary、项目档案、里程碑、风险和交付物。它最大的价值，是让事情不再只停留在“聊过了”，而是可以今天推进、明天续上、以后回看。",
    6: "但当任务进入复杂执行阶段，比如事故驱动分析、多模块代码追踪、需要结构化产出时，主会话不适合直接陷进所有细节。这时 executor 的作用就出来了。主会话负责判断和收口，executor 负责把目标转成可持续处理的执行任务，必要时再通过 ACP 连到 Codex 做深度分析。这样复杂任务就有了稳定的入口、执行链路和结果出口。",
    7: "再往后，我们发现光有记录和执行还不够。历史信息虽然存下来了，但不一定捞得对。所以又补了记忆和认知这层。memory_search 加上本地 gguf 向量模型，重点不是炫模型，而是让系统做到找得到、少漏、接得上。cognition-system 则进一步沉淀哪些做法经常有效、哪些地方容易踩坑，让以后做事更准。",
    8: "这里我用日志猎人举一个真实案例。它一开始只是日志巡检项目，后来开始长出主专项、子任务扩展和回写沉淀。比如围绕中江病区护士站节点 down，这个问题没有停留在聊天里，而是被挂回专项、拆成分析任务，再通过 executor 承接、ACP 连 Codex 做多模块源码追踪，最后形成正式分析报告和项目更新。这就把整条链路跑通了。",
    9: "这套机制带来的变化，并不是抽象的“效率更高”。更具体的是：任务不那么容易断片，复杂问题能从临时讨论变成可接力的正式产物，经验和教训也不只服务当前任务，而是能反哺后续专项和协作判断。AI 的角色，也从回答问题，开始进入收口、承接、执行、回写和复盘的完整链路。",
    10: "当然，这套机制也有边界和教训。不是所有任务都值得 agent 化，简单任务直接在主会话里完成反而更轻。executor 和 Codex 更适合事故驱动、多模块上下文、需要形成方案草案的任务。升级和维护过程里我们也踩过坑，比如 workspace 污染、升级覆盖、回写不及时导致第二天断片。这些都提醒我们，真正重要的不是工具多，而是规则稳。",
    11: "最后我想收成一句话：这不是一组零散功能，而是一条从输入、承接、执行、回写、记忆到反思的协作链路。work-control 管信息怎么进，work-system 管事情怎么跑，executor 管复杂任务怎么被稳定执行，cognition-system 管以后怎么跑得更准。AI 真正的价值，不只是回答问题，而是开始进入协作结构本身。",
}

outline_md = """# AI 分享 PPT v1 提纲

## 主题
从消息流到工作流：AI 如何把零散协作变成持续推进

## 页面结构
1. 封面
2. 为什么要做这件事
3. 整体结构：四层协作链路
4. 第一层：work-control
5. 第二层：work-system
6. 第三层：executor + ACP + Codex
7. 第四层：记忆与认知
8. 案例：日志猎人如何跑起来
9. 这套机制带来的真实变化
10. 边界与教训
11. 总结
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
    for p in paragraphs:
        tx_body.remove(p)
    for line in lines:
        tx_body.append(build_paragraph(template_p, line))


def iter_text_shapes(root):
    for sp in root.findall('.//p:sp', ns):
        if sp.find('p:txBody', ns) is not None:
            yield sp


shutil.copyfile(TEMPLATE, TARGET)
with zipfile.ZipFile(TARGET, 'r') as zin:
    payload = {name: zin.read(name) for name in zin.namelist()}

for slide_idx, content in slides.items():
    path = f"ppt/slides/slide{slide_idx}.xml"
    root = ET.fromstring(payload[path])
    text_shapes = list(iter_text_shapes(root))
    if len(text_shapes) >= 1:
        set_shape_text(text_shapes[0], [content['title']])
    if len(text_shapes) >= 2:
        set_shape_text(text_shapes[1], content['body'])
    payload[path] = ET.tostring(root, encoding='utf-8', xml_declaration=True)

notes_path = "ppt/notesSlides/notesSlide1.xml"
if notes_path in payload:
    root = ET.fromstring(payload[notes_path])
    text_shapes = [sp for sp in root.findall('.//p:sp', ns) if sp.find('p:txBody', ns) is not None and sp.findall('.//a:t', ns)]
    if len(text_shapes) >= 2:
        set_shape_text(text_shapes[1], [notes.get(1, '')])
    payload[notes_path] = ET.tostring(root, encoding='utf-8', xml_declaration=True)

with zipfile.ZipFile(TARGET, 'w', zipfile.ZIP_DEFLATED) as zout:
    for name, data in payload.items():
        zout.writestr(name, data)

with open(OUTLINE, 'w', encoding='utf-8') as f:
    f.write(outline_md)

print(TARGET)
print(OUTLINE)
