import copy
import os
import shutil
import zipfile
import xml.etree.ElementTree as ET

BASE = r"C:\Users\pc\.openclaw\workspace\work-system\deliverables"
SOURCE = os.path.join(BASE, "log-hunter-ai-presentation-2026-03-21-v10-notes.pptx")
TARGET = os.path.join(BASE, "log-hunter-ai-presentation-2026-03-21-v11-notes.pptx")
SCRIPT_OUT = os.path.join(BASE, "log-hunter-ai-presentation-2026-03-21-v11-speech.md")

ns = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}
for prefix, uri in ns.items():
    ET.register_namespace(prefix, uri)

if not os.path.exists(SOURCE):
    raise RuntimeError("v10-notes source ppt not found")
shutil.copyfile(SOURCE, TARGET)

notes_texts = {
    1: "大家好，我是第别，今天由我代表日志猎人团队做这次汇报。接下来我会用大约 15 分钟，向大家介绍我们在日志巡检和分析方向上的一些实践与思考。",
    3: "下面我正式开始介绍这个项目。\n\n我们做日志猎人的出发点，并不是单纯想做一个查日志的小工具，而是希望解决一个更实际的问题：系统运行中的很多问题发现仍偏事后响应，很多时候要等到用户反馈、接口报错或者现场排查时，团队才被动介入。\n\n所以我们希望把日志从一种事后排障材料，逐步变成主动发现问题、支撑持续优化和治理闭环的抓手。接下来我会从项目背景、技术思路、成果价值和后续规划四个部分展开。",
    4: "这一页我想先把项目背景和目标讲清楚。\n\n我们在实际工作里观察到，系统运行中的很多问题发现仍偏事后响应。也就是说，日志虽然一直在产生，但很多时候并没有真正转化成可以提前发现风险、持续推动优化的抓手。\n\n所以我们做这个项目，不只是为了把日志拉出来看，而是希望建立一套可复用的日志巡检能力，把问题发现、问题分析、优化建议和后续验证串起来，真正去支撑系统健壮性提升、性能优化和日志质量改进。",
    5: "这一页我不想把重点放在炫技术上，而是想讲清楚我们的整体思路。\n\n我们把这件事拆成四步：先稳定获取日志，再做结构化分析，再把结果输出成可复盘的内容，最后再把这些结果反过来用于系统优化。\n\n也就是说，技术路径本身不是最终目的，真正重要的是让日志从原始文本变成可以持续创造价值的输入。无论是 K8s 还是传统服务器，最终都要服务同一个目标，就是让日志不仅能看问题，还能推动问题改进。",
    6: "如果说上一页讲的是主线，这一页讲的就是能力边界。\n\n在持续优化这条主线之外，我们也在逐步补齐更完整的智能分析能力。比如，现在已经支持自然语言发起巡检需求，可以降低使用门槛；在传统服务器场景下，也可以扩展到 GC 日志分析，让能力边界从业务异常继续延展到 JVM 运行状态诊断。\n\n另外，通过代表 trace、完整链路和结构化聚合，我们不仅能把结果说明白，也为后续更智能的分析和自动处理预留了空间。",
    7: "这一页我想重点讲我理解的验证闭环。\n\n我们希望这个项目后续不只是停留在发现问题、提出建议、再次验证，而是进一步做到：基于报告结果，由 AI 辅助生成修复方向、整改建议，甚至帮助形成更可执行的修复方案，然后再回到日志和结果层面验证效果。\n\n如果这个闭环能够逐步建立起来，那日志巡检就不只是一个分析工具，而会变成连接发现、分析、修复和验证的一套工作机制。",
    8: "这里我做一个阶段性总结。\n\n到当前阶段，我们已经形成了一套可落地的日志巡检能力；但更重要的是，这个项目推动的其实是一种工作方式的变化，也就是从过去更偏被动排查，逐步走向持续优化和治理闭环。\n\n后续我们会继续增强对系统稳定性和性能问题的分析能力，持续改进日志质量，同时把建议落地后的验证环节补得更完整。",
    9: "这一页展示的是报告首页。\n\n我想强调的重点不是界面本身，而是它能够让使用者在很短时间内建立对本次巡检结果的整体判断。比如时间范围、日志量、数据质量、影响级别分布，这些信息都会直接影响后续的异常分析和优化判断。\n\n所以这页的作用，是帮助我们先快速看清整体问题画像。",
    10: "这一页我建议把它理解成行动层结果页。\n\n报告并不是只停留在统计层面，而是进一步给出异常明细、代表 trace、完整链路线索，以及慢接口分析等更贴近定位和优化的内容。\n\n也就是说，这一页想证明的是：报告结果已经不只是展示材料，而是可以继续拿去做问题定位和后续优化的输入。",
    11: "最后讲一下未来规划。\n\n后续我们会继续围绕三个方向推进：第一，继续提升对系统稳定性问题和性能问题的分析能力，同时持续改进日志质量；第二，把日志反哺建议和整改动作更紧密地连接起来，逐步建立更清晰的验证闭环；第三，在更多环境和更多日志类型中复制这套能力，并继续拓展包括 GC 日志在内的更多分析场景。",
}

speech_md = """# 日志猎人答辩稿（可直接照读版）

## 开场

### P1 封面
大家好，我是第别，今天由我代表日志猎人团队做这次汇报。接下来我会用大约 15 分钟，向大家介绍我们在日志巡检和分析方向上的一些实践与思考。

### P2 团队介绍
这一页我简单介绍一下团队。我们团队的分工覆盖了项目统筹、能力设计、开发实现、联调验证和场景支撑，确保这个项目不是停留在想法层面，而是能真正落到现场使用和答辩展示。

### P3 项目介绍与议程
下面我正式开始介绍这个项目。

我们做日志猎人的出发点，并不是单纯想做一个查日志的小工具，而是希望解决一个更实际的问题：系统运行中的很多问题发现仍偏事后响应，很多时候要等到用户反馈、接口报错或者现场排查时，团队才被动介入。

所以我们希望把日志从一种事后排障材料，逐步变成主动发现问题、支撑持续优化和治理闭环的抓手。接下来我会从项目背景、技术思路、成果价值和后续规划四个部分展开。

## 主体

### P4 项目背景与目标
这一页我想先把项目背景和目标讲清楚。

我们在实际工作里观察到，系统运行中的很多问题发现仍偏事后响应。也就是说，日志虽然一直在产生，但很多时候并没有真正转化成可以提前发现风险、持续推动优化的抓手。

所以我们做这个项目，不只是为了把日志拉出来看，而是希望建立一套可复用的日志巡检能力，把问题发现、问题分析、优化建议和后续验证串起来，真正去支撑系统健壮性提升、性能优化和日志质量改进。

### P5 技术思路与实现
这一页我不想把重点放在炫技术上，而是想讲清楚我们的整体思路。

我们把这件事拆成四步：先稳定获取日志，再做结构化分析，再把结果输出成可复盘的内容，最后再把这些结果反过来用于系统优化。

也就是说，技术路径本身不是最终目的，真正重要的是让日志从原始文本变成可以持续创造价值的输入。无论是 K8s 还是传统服务器，最终都要服务同一个目标，就是让日志不仅能看问题，还能推动问题改进。

### P6 能力深化
如果说上一页讲的是主线，这一页讲的就是能力边界。

在持续优化这条主线之外，我们也在逐步补齐更完整的智能分析能力。比如，现在已经支持自然语言发起巡检需求，可以降低使用门槛；在传统服务器场景下，也可以扩展到 GC 日志分析，让能力边界从业务异常继续延展到 JVM 运行状态诊断。

另外，通过代表 trace、完整链路和结构化聚合，我们不仅能把结果说明白，也为后续更智能的分析和自动处理预留了空间。

### P7 验证闭环与应用价值
这一页我想重点讲我理解的验证闭环。

我们希望这个项目后续不只是停留在发现问题、提出建议、再次验证，而是进一步做到：基于报告结果，由 AI 辅助生成修复方向、整改建议，甚至帮助形成更可执行的修复方案，然后再回到日志和结果层面验证效果。

如果这个闭环能够逐步建立起来，那日志巡检就不只是一个分析工具，而会变成连接发现、分析、修复和验证的一套工作机制。

### P8 总结展望
这里我做一个阶段性总结。

到当前阶段，我们已经形成了一套可落地的日志巡检能力；但更重要的是，这个项目推动的其实是一种工作方式的变化，也就是从过去更偏被动排查，逐步走向持续优化和治理闭环。

后续我们会继续增强对系统稳定性和性能问题的分析能力，持续改进日志质量，同时把建议落地后的验证环节补得更完整。

## 成果展示

### P9 成果展示 01
这一页展示的是报告首页。

我想强调的重点不是界面本身，而是它能够让使用者在很短时间内建立对本次巡检结果的整体判断。比如时间范围、日志量、数据质量、影响级别分布，这些信息都会直接影响后续的异常分析和优化判断。

所以这页的作用，是帮助我们先快速看清整体问题画像。

### P10 成果展示 02
这一页我建议把它理解成行动层结果页。

报告并不是只停留在统计层面，而是进一步给出异常明细、代表 trace、完整链路线索，以及慢接口分析等更贴近定位和优化的内容。

也就是说，这一页想证明的是：报告结果已经不只是展示材料，而是可以继续拿去做问题定位和后续优化的输入。

### P11 未来规划
最后讲一下未来规划。

后续我们会继续围绕三个方向推进：第一，继续提升对系统稳定性问题和性能问题的分析能力，同时持续改进日志质量；第二，把日志反哺建议和整改动作更紧密地连接起来，逐步建立更清晰的验证闭环；第三，在更多环境和更多日志类型中复制这套能力，并继续拓展包括 GC 日志在内的更多分析场景。

## 结尾

### P12 Q&A
我的汇报就到这里。我们希望把日志猎人从一个项目能力，逐步推进成更通用的日志巡检与治理能力。谢谢大家，欢迎各位老师批评指正。
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


def set_shape_text(sp, text):
    tx_body = sp.find("p:txBody", ns)
    paragraphs = tx_body.findall("a:p", ns)
    template_p = paragraphs[0]
    for p in paragraphs:
        tx_body.remove(p)
    for line in text.split("\n"):
        tx_body.append(build_paragraph(template_p, line))


with zipfile.ZipFile(TARGET, "r") as zin:
    payload = {name: zin.read(name) for name in zin.namelist()}

for slide_idx, notes_text in notes_texts.items():
    path = f"ppt/notesSlides/notesSlide{slide_idx}.xml"
    root = ET.fromstring(payload[path])
    shapes = [sp for sp in root.findall('.//p:sp', ns) if sp.find('p:txBody', ns) is not None and sp.findall('.//a:t', ns)]
    if len(shapes) < 2:
        raise RuntimeError(f"notes slide {slide_idx}: expected note body")
    set_shape_text(shapes[1], notes_text)
    payload[path] = ET.tostring(root, encoding='utf-8', xml_declaration=True)

with zipfile.ZipFile(TARGET, 'w', zipfile.ZIP_DEFLATED) as zout:
    for name, data in payload.items():
        zout.writestr(name, data)

with open(SCRIPT_OUT, 'w', encoding='utf-8') as f:
    f.write(speech_md)

print(TARGET)
print(SCRIPT_OUT)
