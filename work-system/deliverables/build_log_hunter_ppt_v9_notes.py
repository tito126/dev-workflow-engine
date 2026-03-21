import copy
import glob
import os
import shutil
import zipfile
import xml.etree.ElementTree as ET

BASE = r"C:\Users\pc\.openclaw\workspace\work-system\deliverables"
ASSETS = os.path.join(BASE, "ppt-assets")
TARGET = os.path.join(BASE, "log-hunter-ai-presentation-2026-03-21-v9-notes.pptx")

ns = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}
for prefix, uri in ns.items():
    ET.register_namespace(prefix, uri)

source_candidates = [
    p for p in glob.glob(os.path.join(BASE, "*.pptx"))
    if "v7-notes" in os.path.basename(p) and not os.path.basename(p).startswith("~$")
]
if not source_candidates:
    raise RuntimeError("v7-notes source ppt not found")
source = source_candidates[0]
shutil.copyfile(source, TARGET)

slide_texts = {
    4: [
        "01 项目背景与目标",
        "从事后响应，走向更主动的日志巡检",
        "痛点背景",
        "系统运行中的很多问题发现仍偏事后响应，往往要到用户反馈、接口报错或现场排查时才被动介入。",
        "项目判断",
        "日志虽然很多，但多数时候还停留在“可查看”层面，没有稳定转化为异常定位、性能优化和系统改进的抓手。",
        "项目目标",
        "建立一套可复用的日志巡检能力，把问题发现、问题分析、优化建议和后续验证串成闭环。",
        "价值导向",
        "既支撑当前排障，也服务后续健壮性提升、性能优化、日志质量改进和经验沉淀。",
        "这个项目关注的不是单次排查效率，而是把日志从被动排查材料，逐步变成支撑持续优化和验证闭环的工程能力。",
    ],
    5: [
        "02 技术思路与实现",
        "先把日志用起来，再把日志用得更好",
        "稳定获取",
        "兼容 K8s 和传统服务器两类环境，先保证不同现场都能稳定拿到可分析的日志。",
        "结构化分析",
        "围绕异常、慢接口、代表 trace 和日志质量问题做分析，让日志从“原始文本”变成“问题画像”。",
        "结果输出",
        "将分析结果沉淀为 HTML 报告，让问题分布、定位线索和反哺建议更便于查看、复盘和沟通。",
        "持续优化",
        "项目的重点不只是展示一条技术路径，而是把巡检结果反向用于健壮性、性能和日志规范的持续改进。",
    ],
    6: [
        "02 技术思路与实现 - 持续优化方向",
        "巡检的价值，不止于定位问题，更在于持续优化",
        "健壮性提升",
        "通过异常归类、调用方识别和代表案例沉淀，更早暴露高频故障点与薄弱链路。",
        "性能提升",
        "通过慢接口分析、时间间隔观察和完整链路回看，为性能瓶颈定位和优化提供依据。",
        "质量增强",
        "通过日志质量分析和反哺建议，持续发现缺少入口、异常不清晰、分类不明确等日志设计问题。",
    ],
    7: [
        "03 验证闭环与应用价值",
        "阶段成果",
        "已形成日志获取、结构化分析、HTML 报告和典型案例沉淀等阶段能力，具备真实场景使用基础。",
        "验证闭环",
        "围绕“发现问题 -> 提出建议 -> 推动改进 -> 再次验证”逐步建立闭环，让巡检结果能够回到系统本身。",
        "应用价值",
        "既能服务日常巡检、异常复盘和性能排查，也能支撑汇报展示、经验沉淀和后续推广复用。",
        "发展前景",
        "后续可继续推广到更多服务、更多医院环境和更多治理场景，逐步形成统一的日志巡检与治理能力底座。",
        "从发现问题到验证改进，逐步形成闭环。",
    ],
    8: [
        "总结展望",
        "04 总结与展望\n围绕阶段成果、持续优化价值和后续验证闭环做总结",
        "03",
        "02",
        "成果收获\n--\n形成可落地的日志巡检能力\n沉淀了问题分析与报告表达方法",
        "01",
        "阶段总结\n--\n从被动排查走向更主动的巡检思路\n从单次处理走向持续优化意识",
        "未来规划\n--\n增强健壮性、性能和日志质量分析能力\n继续补齐建议落地后的验证闭环",
    ],
    9: [
        "成果展示 01",
        "报告首页先建立整体问题画像，通过时间范围、日志质量和影响级别分布，让使用者快速判断问题规模、数据质量和处理优先级。",
    ],
    10: [
        "成果展示 02",
        "报告不只停留在统计层面，还进一步给出异常明细、代表 trace 和完整链路线索，帮助定位问题并形成后续优化抓手。",
    ],
    11: [
        "未来规划",
        "1. 围绕健壮性、性能提升和日志质量分析增强继续深化能力。\n2. 将日志反哺建议与问题整改结合起来，逐步建立更清晰的验证闭环。\n3. 在更多医院、更多环境和更多日志类型中复制落地，并继续拓展 GC 日志等场景。",
    ],
}

notes_texts = {
    4: "这一页先把项目背景和目标讲稳。\n\n核心判断有两个：第一，系统运行中的很多问题发现仍偏事后响应，常常是用户反馈、接口报错或者现场排查时才介入；第二，日志虽然很多，但多数时候还停留在可查看层面，没有稳定转化为能持续使用的改进抓手。\n\n所以我们做这个项目，不只是为了把日志拉出来看，而是希望建立一套可复用的巡检能力，把问题发现、问题分析、优化建议和后续验证串起来，服务后续的健壮性提升、性能优化和日志质量改进。",
    5: "这一页不强调炫技，强调思路。\n\n我们把事情拆成四块：先稳定获取日志，再做结构化分析，再输出可复盘的结果，最后把结果继续反哺回系统优化。\n\n这里想表达的是，技术路径本身不是重点，重点是让日志真正被用起来，并且能持续产生改进价值。无论是 K8s 还是传统服务器，最终都要落到同一个目标：让日志不只用于看问题，还用于推动问题改进。",
    6: "这一页重点讲后续价值，而不是讲技术细节。\n\n项目做出来以后，最直接的作用当然是帮助定位问题，但更长期的价值在于持续优化。\n\n第一是健壮性提升，通过异常归类和高频问题沉淀，可以更早暴露薄弱链路；第二是性能提升，通过慢接口和完整链路分析，能为性能瓶颈定位提供依据；第三是日志质量增强，通过日志质量分析和反哺建议，推动日志本身写得更清楚、更可用。\n\n这页要让人感觉：我们做的不是一次性的排查工具，而是一套会持续带来改进收益的能力。",
    7: "这一页要把闭环讲出来。\n\n现在项目已经具备阶段成果，包括日志获取、结构化分析、报告输出和案例沉淀。但我们更看重的是，后续能不能把巡检结果重新带回系统里，形成发现问题、提出建议、推动改进、再次验证的闭环。\n\n如果这个闭环建立起来，日志巡检的意义就不只是做报告，而是会逐渐沉淀成一种稳定的工作方式：能复盘、能验证、能持续优化。",
    8: "总结页主要收三点：第一，已经形成了一套可落地的日志巡检能力；第二，项目的价值不只在于当前排障，而在于把工作方式从被动排查推向持续优化；第三，后续会继续补齐建议落地后的验证闭环，让项目更完整。",
    9: "这一页展示的是报告首页。重点不是界面，而是它能让使用者快速建立对本次巡检结果的整体判断：时间范围是什么、日志量大概多少、数据质量怎么样、哪些问题优先级更高。\n\n这也是后续做异常分析和优化判断的入口。",
    10: "这一页想说明，报告不是停留在统计层面。\n\n除了告诉我们有哪些问题，它还进一步把异常明细、代表 trace 和完整链路线索展示出来，帮助开发和运维继续往下定位。同时，日志反哺建议和慢接口分析，也能为后续优化提供明确抓手。",
    11: "未来规划重点有三块：一是继续增强健壮性、性能和日志质量分析能力；二是把日志反哺建议真正和整改动作连起来，建立验证闭环；三是在更多环境里复制落地，并拓展包括 GC 日志在内的更多分析场景。",
}

media_replacements = {
    "ppt/media/image21.png": os.path.join(ASSETS, "report-01-overview.png"),
    "ppt/media/image22.png": os.path.join(ASSETS, "report-04-details.png"),
    "ppt/media/image23.png": os.path.join(ASSETS, "report-03-stats.png"),
}


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

for slide_idx, texts in slide_texts.items():
    path = f"ppt/slides/slide{slide_idx}.xml"
    root = ET.fromstring(payload[path])
    shapes = []
    for sp in root.findall(".//p:sp", ns):
        if sp.find("p:txBody", ns) is not None and sp.findall(".//a:t", ns):
            shapes.append(sp)
    if len(shapes) != len(texts):
        raise RuntimeError(f"slide {slide_idx}: expected {len(shapes)} text shapes, got {len(texts)} replacements")
    for sp, text in zip(shapes, texts):
        set_shape_text(sp, text)
    payload[path] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

for slide_idx, notes_text in notes_texts.items():
    path = f"ppt/notesSlides/notesSlide{slide_idx}.xml"
    root = ET.fromstring(payload[path])
    note_shapes = []
    for sp in root.findall(".//p:sp", ns):
        if sp.find("p:txBody", ns) is not None and sp.findall(".//a:t", ns):
            note_shapes.append(sp)
    if len(note_shapes) < 2:
        raise RuntimeError(f"notes slide {slide_idx}: expected at least 2 text shapes")
    set_shape_text(note_shapes[1], notes_text)
    payload[path] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

for media_path, asset_path in media_replacements.items():
    with open(asset_path, "rb") as f:
        payload[media_path] = f.read()

with zipfile.ZipFile(TARGET, "w", zipfile.ZIP_DEFLATED) as zout:
    for name, data in payload.items():
        zout.writestr(name, data)

print(TARGET)
