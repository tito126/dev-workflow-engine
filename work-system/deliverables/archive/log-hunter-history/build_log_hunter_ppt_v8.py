import copy
import glob
import os
import shutil
import zipfile
import xml.etree.ElementTree as ET

BASE = r"C:\Users\pc\.openclaw\workspace\work-system\deliverables"
ASSETS = os.path.join(BASE, "ppt-assets")
TARGET = os.path.join(BASE, "log-hunter-ai-presentation-2026-03-21-v8.pptx")

ns = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}
for prefix, uri in ns.items():
    ET.register_namespace(prefix, uri)

files = [
    p for p in glob.glob(os.path.join(BASE, "*.pptx"))
    if not os.path.basename(p).startswith("~$") and os.path.abspath(p) != os.path.abspath(TARGET)
]
files.sort(key=os.path.getmtime)
source = files[-1]
shutil.copyfile(source, TARGET)

slide_texts = {
    4: [
        "01 项目背景与目标",
        "日志巡检要解决的，不只是\"有没有报错\"",
        "痛点背景",
        "医院现场日志量大、来源杂，很多问题并不是没有日志，而是日志太散、太多、太难看清。",
        "核心判断",
        "真正有价值的巡检，不是把 ERROR 拉出来，而是把问题从海量日志里快速识别出来。",
        "项目目标",
        "建立一套能稳定复用的日志巡检方案，覆盖发现问题、归类问题、定位问题三个关键动作。",
        "价值导向",
        "让日志从排查材料升级为行动依据，支撑异常治理、性能优化和日志规范改进。",
        "我们的目标不是单次排查提效，而是把日志巡检沉淀为一条稳定流程：既能看见问题，也能分清问题，还能继续追到关键链路。",
    ],
    5: [
        "02 技术方案与实现",
        "核心方案不是全量展开，而是分阶段识别与补全",
        "问题识别",
        "第一阶段先抓 ERROR 和业务处理耗时，快速识别异常类别和慢接口入口。",
        "链路补全",
        "第二阶段围绕代表 trace 回拉完整上下文，把 INFO 等关键链路补齐。",
        "设计思路",
        "不是一开始就全量展开，而是先锁定高价值问题，再补全最值得追的链路。",
        "方案价值",
        "这套两阶段分析策略兼顾分析效率与定位深度，更适合海量日志场景的工程化落地。",
    ],
    6: [
        "02 技术方案与实现 - 环境适配",
        "同一巡检目标，需要适配不同环境的数据链路",
        "统一入口能力",
        "用户以自然语言提出巡检需求后，系统先提取医院、服务、时间范围和分析目标，再自动判断进入哪条业务线。",
        "双业务线适配",
        "K8s 场景走 fetch -> analyze -> fetch2 -> re-analyze -> report；传统服务器走查节点、下载日志、过滤分析再出报告。",
        "成熟度体现",
        "两条路径取数方式不同，但最终都汇聚到统一分析框架；像桐乡先问集群、K8s 默认 ±60s 补链窗口，都是经过验证的稳定规则。",
    ],
    7: [
        "03 能力延展与应用价值",
        "当前能力边界",
        "当前已覆盖异常分析、慢接口分析、代表 trace 补链和 HTML 报告输出，能够支撑日常巡检与专题排查。",
        "能力扩展示例",
        "在传统服务器场景下，已支持通过 getServiceLogs(type=gc) 拉取 GC 日志，能力边界可从业务异常延展到 JVM 运行状态诊断。",
        "落地场景",
        "适用于日常巡检、异常复盘、性能排查和专题汇报等场景，既能服务现场排障，也能支撑阶段成果展示。",
        "应用价值",
        "巡检结果不仅用于发现问题，还能反向暴露日志埋点质量、性能瓶颈和治理重点，帮助团队形成持续优化抓手。",
        "巡检能力不止于异常分析，还要具备持续扩展空间。",
    ],
    8: [
        "总结展望",
        "04 总结与展望\n围绕阶段成果、方案价值和后续拓展做总结",
        "03",
        "02",
        "成果收获\n--\n形成跨环境可落地的日志巡检能力\n沉淀了分阶段分析与报告输出方法",
        "01",
        "阶段总结\n--\n从单次日志排查，走向可复用的巡检流程\n从经验驱动，走向规则化分析",
        "未来规划\n--\n继续增强问题发现和优化建议能力\n拓展更多日志类型与运行状态分析场景",
    ],
    9: [
        "成果展示 01",
        "报告首页：先建立整体问题画像；通过时间范围、日志质量和影响级别分布，帮助使用者在进入细节前快速判断问题规模、数据质量和处理优先级。",
    ],
    10: [
        "成果展示 02",
        "从异常归类到完整链路，报告不仅做统计，还给出代表 trace 和关键定位线索，减少开发与运维的二次翻日志成本。",
    ],
    11: [
        "未来规划",
        "1. 围绕巡检结果持续推动系统优化、日志规范治理和定位效率提升。\n2. 继续完善问题发现 - 问题归类 - 链路定位 - 优化建议 - 效果验证的闭环。\n3. 在更多医院、更多环境和更多日志类型中复制落地，包括 GC 日志等扩展场景。",
    ],
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
            rPr = ET.Element(f"{{{ns['a']}}}rPr")
            r.append(rPr)
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
    lines = text.split("\n")
    for line in lines:
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

for media_path, asset_path in media_replacements.items():
    with open(asset_path, "rb") as f:
        payload[media_path] = f.read()

with zipfile.ZipFile(TARGET, "w", zipfile.ZIP_DEFLATED) as zout:
    for name, data in payload.items():
        zout.writestr(name, data)

print(TARGET)
