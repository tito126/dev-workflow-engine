const pptxgen = require('D:/nvm/nodejs/node_modules/pptxgenjs');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'OpenClaw';
pptx.company = 'OpenClaw';
pptx.subject = '下午 AI 分享：从消息流到工作流';
pptx.title = '从消息流到工作流：AI 如何把零散协作变成持续推进';
pptx.lang = 'zh-CN';
pptx.theme = { headFontFace: 'Microsoft YaHei', bodyFontFace: 'Microsoft YaHei', lang: 'zh-CN' };

const C = {
  navy: '1F2A44', text: '1E2430', sub: '5F6B7A', line: 'C9D3E1',
  accent: '6E8FD8', accent2: 'DCE6FB', white: 'FFFFFF', light: 'F7F9FC',
  gold: 'F3B94E', pale: 'EAF1FF', pale2: 'EEF4FF', mint: 'E8F4EE'
};

function bg(s, color = C.light) { s.background = { color }; }
function footer(s, n) {
  s.addText(String(n), { x: 12.55, y: 7.1, w: 0.25, h: 0.16, fontFace: 'Arial', fontSize: 10, color: C.sub, align: 'right', margin: 0 });
}
function header(s, title, kicker) {
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.68, line: { color: C.navy, transparency: 100 }, fill: { color: C.navy } });
  s.addText(kicker, { x: 0.6, y: 0.18, w: 4.2, h: 0.18, fontFace: 'Arial', fontSize: 12, bold: true, color: C.accent2, margin: 0 });
  s.addText(title, { x: 0.6, y: 0.94, w: 11.6, h: 0.42, fontFace: 'Microsoft YaHei', fontSize: 24, bold: true, color: C.text, margin: 0 });
  s.addShape(pptx.ShapeType.line, { x: 0.6, y: 1.5, w: 12.05, h: 0, line: { color: C.line, pt: 1.2 } });
}
function quote(s, text, subtext, h = 1.12) {
  s.addShape(pptx.ShapeType.roundRect, { x: 0.85, y: 1.92, w: 11.65, h, rectRadius: 0.06, line: { color: C.accent, transparency: 100 }, fill: { color: C.pale } });
  s.addText(text, { x: 1.1, y: 2.18, w: 11.0, h: 0.32, fontFace: 'Microsoft YaHei', fontSize: 21, bold: true, italic: true, color: C.navy, margin: 0 });
  if (subtext) s.addText(subtext, { x: 1.1, y: 2.62, w: 11.0, h: 0.18, fontFace: 'Microsoft YaHei', fontSize: 11, color: C.sub, margin: 0 });
}
function bullets(s, items, x, y, w, h, fs = 17, after = 11) {
  s.addText(items.map(t => ({ text: t, options: { bullet: { indent: 16 }, hanging: 3, marginLeft: 20 } })), { x, y, w, h, fontFace: 'Microsoft YaHei', fontSize: fs, color: C.text, margin: 0.03, paraSpaceAfterPt: after, breakLine: false, valign: 'top' });
}
function card(s, x, y, w, h, title, body, titleSize = 18, bodySize = 13, fill = C.white) {
  s.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.05, line: { color: C.line, pt: 1 }, fill: { color: fill } });
  s.addText(title, { x: x + 0.25, y: y + 0.22, w: w - 0.45, h: 0.24, fontFace: 'Microsoft YaHei', fontSize: titleSize, bold: true, color: C.navy, margin: 0 });
  s.addText(body, { x: x + 0.25, y: y + 0.62, w: w - 0.45, h: h - 0.8, fontFace: 'Microsoft YaHei', fontSize: bodySize, color: C.text, margin: 0.02, breakLine: false, valign: 'top' });
}
function miniTag(s, x, y, text, w = 1.8) {
  s.addShape(pptx.ShapeType.roundRect, { x, y, w, h: 0.32, rectRadius: 0.03, line: { color: C.accent, transparency: 100 }, fill: { color: C.accent } });
  s.addText(text, { x: x + 0.08, y: y + 0.07, w: w - 0.16, h: 0.12, fontFace: 'Arial', fontSize: 10, bold: true, color: C.white, align: 'center', margin: 0 });
}

function cover() {
  const s = pptx.addSlide(); bg(s, C.navy);
  miniTag(s, 0.8, 0.82, 'INTERNAL SHARE', 1.7);
  s.addText('从消息流到工作流', { x: 0.8, y: 1.56, w: 6.8, h: 0.55, fontFace: 'Microsoft YaHei', fontSize: 29, bold: true, color: C.white, margin: 0 });
  s.addText('AI 如何把零散协作变成持续推进', { x: 0.8, y: 2.3, w: 7.8, h: 0.55, fontFace: 'Microsoft YaHei', fontSize: 22, color: C.accent2, margin: 0 });
  s.addText('今天不重点讲模型能力，重点讲一条真实可复用的落地路径。', { x: 0.82, y: 3.32, w: 7.0, h: 0.28, fontFace: 'Microsoft YaHei', fontSize: 17.5, italic: true, color: 'D9E3F6', margin: 0 });
  s.addShape(pptx.ShapeType.line, { x: 6.95, y: 1.42, w: 0, h: 4.95, line: { color: '42557D', pt: 1.2 } });
  card(s, 7.35, 1.92, 4.9, 1.38, '今天我想讲的三件事', '一，日志猎人如何把 AI 第一次真正带进业务现场。\n二，为什么后来要继续补长期记忆和工作控制系统。', 17, 13, C.pale2);
  card(s, 7.35, 3.72, 4.9, 1.95, '第三部分', 'AI 不只是提升个人效率，也在改变协作方式和后续产品化路径。', 17, 15, C.white);
}

function s2() {
  const s = pptx.addSlide(); bg(s); header(s, '第一部分：先从“日志猎人”这个真实项目说起', 'PART 01 · CASE FIRST');
  quote(s, '我第一次深度落地 AI，不是从宏大框架开始的，而是从一个很具体的问题开始的：日志分析。');
  card(s, 0.88, 3.42, 3.8, 2.55, '起点', '最开始只是想做一个更高效的日志巡检工具，把异常、慢接口和代表链路先自动捞出来。', 18, 14);
  card(s, 4.78, 3.42, 3.8, 2.55, '变化', '越往下做越发现，难点不是“看懂一次日志”，而是怎么把一次分析继续接成定位、记录和后续推进。', 18, 13.5, C.pale2);
  card(s, 8.68, 3.42, 3.55, 2.55, '价值判断', 'AI 如果只停在单次回答，价值很快就会掉；只有接进工作流，才会越来越有复利。', 18, 13.5, C.white);
  s.addText('日志猎人给我的最大启发，不是“我第一次用上了 AI”，而是我第一次感受到：AI 也可以变成推进链路的一部分。', { x: 0.95, y: 6.34, w: 11.2, h: 0.32, fontFace: 'Microsoft YaHei', fontSize: 14.5, bold: true, color: C.navy, margin: 0 });
  footer(s, 2);
}

function s3() {
  const s = pptx.addSlide(); bg(s); header(s, '日志猎人的三个关键教训', 'PART 01 · LESSONS');
  quote(s, 'AI 项目最容易做得热闹，最难做得可复用。', null, 1.06);
  card(s, 0.88, 3.36, 3.7, 2.75, '教训 1', '不要一开始就追求大而全。\n先抓一个真实痛点，把“异常识别 + 报告整理 + 可继续分析”这条最小链路跑通。', 18, 13.2);
  card(s, 4.82, 3.36, 3.7, 2.75, '教训 2', '真正有价值的，不是某次回答多漂亮，而是结果能不能沉淀成后面还用得上的分析底稿。', 18, 13.2, C.pale2);
  card(s, 8.76, 3.36, 3.46, 2.75, '教训 3', '问题分析不是终点。\n能不能反哺专项推进，才是这类能力最后有没有业务价值的关键。', 18, 13.2);
  s.addText('如果只让我用一句话总结这段经历，我会说：日志猎人最有价值的，不是多查了一次日志，而是第一次把“发现问题、分析问题、推进问题”接成了一条链。', { x: 0.95, y: 6.36, w: 11.2, h: 0.34, fontFace: 'Microsoft YaHei', fontSize: 14, bold: true, color: C.navy, margin: 0 });
  footer(s, 3);
}

function s4() {
  const s = pptx.addSlide(); bg(s); header(s, '案例：中江病区护士站节点 down 事件，如何从事故分析变成专项底稿', 'PART 01 · CASE STUDY');
  quote(s, '这次比较不一样的地方，不是我怀疑哪里有问题，而是我把日志巡检、代码分析和专项记录真正接起来了。');
  card(s, 0.88, 3.42, 5.75, 2.8, '已经收口到的内容', '确认了目标接口和关键代码路径；\n识别出 3 段远程依赖串行执行、集成方式无缓存、通用查询链路过度取数等核心问题；\n形成了第一版优化草案。', 17, 12.6);
  card(s, 6.78, 3.42, 5.45, 2.8, '下一步怎么继续推', '补运行时分段耗时证据；\n确认现场到底走的是哪条分支；\n再决定优先做止血优化，还是直接往中期治理推进。', 17, 12.8, C.pale2);
  s.addText('这次最重要的不是“已经解决完”，而是第一次把一个事故驱动的问题推进到了可文档化、可追踪、可继续落实的状态。对护士站研发来说，这类案例也不只是一次问题处理，而是在性能优化、降本增效和系统稳定性主线上，逐步衍生出可继续推进的专项子任务。', { x: 0.95, y: 6.28, w: 11.3, h: 0.44, fontFace: 'Microsoft YaHei', fontSize: 13.2, bold: true, color: C.navy, margin: 0 });
  footer(s, 4);
}

function s5() {
  const s = pptx.addSlide(); bg(s); header(s, '第二部分：为什么后来没有停在一个工具上', 'PART 02 · SYSTEM THINKING');
  quote(s, '做完前面这个案例以后，我很快遇到第二个问题：分析结果如果还只是停留在聊天里，过几天还是会断。');
  card(s, 0.95, 3.48, 11.2, 2.5, '核心判断', '所以我后面没有继续只做“更强的工具”，而是开始补一套承接系统。\n我越来越把这件事理解成：不是给自己多加几个模块，而是在给协作过程补承接层。', 19, 15, C.pale2);
  s.addText('这一段可以拆成三层来看：入口治理、正式运行、长期记忆与认知沉淀。', { x: 0.98, y: 6.3, w: 10.8, h: 0.22, fontFace: 'Microsoft YaHei', fontSize: 15, italic: true, color: C.sub, margin: 0 });
  footer(s, 5);
}

function s6() {
  const s = pptx.addSlide(); bg(s); header(s, '第一层：`work-control` 解决的是入口治理，不是简单记录', 'PART 02 · WORK-CONTROL');
  quote(s, '一句话进来以后，先判断它到底是什么，这件事比直接记下来更重要。');
  bullets(s, [
    '它先判断：这是临时提醒、模糊需求、正式专项，还是需要继续追问的线索。',
    '它的价值不是“多记一条”，而是少把错误信息直接塞进正式系统。',
    '模糊输入如果不先分诊，后面的台账、专项、提醒系统很快就会被噪音污染。'
  ], 0.95, 3.42, 6.05, 2.85, 17, 11);
  card(s, 7.22, 3.56, 5.05, 2.28, '换成人话讲', '在正式流程之前，先补一层“轻量分诊”。\n\n这样后面的系统才比较干净，推进动作也更容易接得住。', 17, 13.5, C.white);
  footer(s, 6);
}

function s7() {
  const s = pptx.addSlide(); bg(s); header(s, '第二层：`work-system` 解决的是事情怎么持续跑下去', 'PART 02 · WORK-SYSTEM');
  quote(s, '好的工作系统，不是把事情都记下来，而是能稳定产出下一步。');
  card(s, 0.9, 3.48, 3.75, 2.35, 'Reminders', '负责“别忘”。\n把容易被漏掉的事显性保住。', 18, 14, C.white);
  card(s, 4.82, 3.48, 3.75, 2.35, '今日聚焦', '负责“今天先抓什么”。\n把优先级抬头，而不是埋在消息里。', 18, 14, C.pale2);
  card(s, 8.74, 3.48, 3.75, 2.35, '每日总结', '负责“什么时候该提前有压力”。\n让临近节点更早被感知。', 18, 14, C.white);
  s.addText('如果用更务实的话概括，这层想解决的是两件事：降低重复翻找和重复沟通的成本，以及提升任务可控、节奏可续、结果可回看的效率。', { x: 0.95, y: 6.26, w: 11.1, h: 0.32, fontFace: 'Microsoft YaHei', fontSize: 13.8, bold: true, color: C.navy, margin: 0 });
  footer(s, 7);
}

function s8() {
  const s = pptx.addSlide(); bg(s); header(s, '第三层：长期记忆与认知沉淀，解决的是“过一段时间还能不能接上”', 'PART 02 · MEMORY');
  quote(s, '长期记忆不是把东西存起来就够了，真正关键的是：需要的时候还能把相关内容捞回来。');
  card(s, 0.9, 3.45, 3.75, 2.4, '找得到', '换个说法也能命中，不靠死记关键词。', 18, 14, C.white);
  card(s, 4.8, 3.45, 3.75, 2.4, '少漏', '同一主题散在不同日期，也能一起捞出来。', 18, 14, C.pale2);
  card(s, 8.7, 3.45, 3.75, 2.4, '接得上', '先前判断能重新参与今天的问题分析。', 18, 14, C.white);
  s.addText('所以我现在把 `memory_search + cognition` 看成长期记忆真正有用的关键，不是“存着”，而是“能回来参与今天的判断”。', { x: 0.95, y: 6.3, w: 11.1, h: 0.28, fontFace: 'Microsoft YaHei', fontSize: 14.5, bold: true, color: C.navy, margin: 0 });
  footer(s, 8);
}

function s9() {
  const s = pptx.addSlide(); bg(s); header(s, '第三部分：AI 带来的，不只是提效，更是认知和组织方式的升级', 'PART 03 · COGNITION SHIFT');
  quote(s, '我后来越来越觉得，AI 带来的真正变化，不只是多了一个更聪明的助手，而是开始逼我重新思考：个人怎么工作、团队怎么协作、产品怎么积累能力。');
  card(s, 0.88, 3.42, 3.75, 2.78, '对个人', '它改变的不只是回答速度，而是做事颗粒度。\n我会更自然地去想：入口怎么治理，信息该落哪层，结果要不要沉淀成可复用产物。', 17, 13.2, C.white);
  card(s, 4.8, 3.42, 3.75, 2.78, '对团队', '它更大的价值不一定是替人做决定，而是减少协作中间断掉的次数。\n说过的话、分析过的问题、形成的判断，更容易被接住。', 17, 13.2, C.pale2);
  card(s, 8.72, 3.42, 3.5, 2.78, '对产品', '后续会把这些能力逐步封装成可复用的 skill 资产，再围绕 `nurse-station-*` 框架，用专项推进方式服务护士站系统的稳定和高效运行。', 17, 12.6, C.white);
  footer(s, 9);
}

function s10() {
  const s = pptx.addSlide(); bg(s); header(s, '后续落地规划：从个人实践，走向可复用的护士站能力资产', 'PART 03 · ROADMAP');
  quote(s, '后面我更关心的，不是继续靠个人临时发挥，而是把这些能力沉淀成团队能复用、专项能接住的资产。');
  card(s, 0.9, 3.45, 3.82, 2.5, '方向 1', '把问题定位、任务拆解、分析回写、验证闭环等能力继续沉淀成可复用 skill。', 18, 13.6, C.white);
  card(s, 4.78, 3.45, 3.82, 2.5, '方向 2', '围绕 `nurse-station-*` 框架，把专项分析、执行、验证逐步接成更稳定的推进链路。', 18, 13.2, C.pale2);
  card(s, 8.66, 3.45, 3.58, 2.5, '方向 3', '重点不是搭一个很大的 AI 平台，而是让真实高频问题有更稳定的承接方式。', 18, 13.2, C.white);
  s.addText('如果这套方法最后真有价值，我希望它带来的不只是个人效率更高，而是我们做事时更少断片、更少重复、更容易把一次判断变成持续推进。', { x: 0.95, y: 6.28, w: 11.2, h: 0.34, fontFace: 'Microsoft YaHei', fontSize: 14, bold: true, color: C.navy, margin: 0 });
  footer(s, 10);
}

function ending() {
  const s = pptx.addSlide(); bg(s, C.navy);
  s.addText('重点不是让 AI 多回答一次，', { x: 1.0, y: 2.05, w: 9.6, h: 0.48, fontFace: 'Microsoft YaHei', fontSize: 27, bold: true, color: C.white, margin: 0 });
  s.addText('而是让协作少断一次。', { x: 1.0, y: 2.8, w: 8.0, h: 0.48, fontFace: 'Microsoft YaHei', fontSize: 27, bold: true, color: C.gold, margin: 0 });
  s.addText('从“日志猎人”到长期记忆、工作控制，再到 nurse-station 能力框架，本质上都在补协作的承接层。', { x: 1.02, y: 4.02, w: 10.6, h: 0.34, fontFace: 'Microsoft YaHei', fontSize: 17.5, italic: true, color: 'DCE6FB', margin: 0 });
  s.addText('THANKS', { x: 1.0, y: 5.18, w: 2.4, h: 0.28, fontFace: 'Arial', fontSize: 20, bold: true, color: C.accent2, margin: 0 });
}

cover();
s2();
s3();
s4();
s5();
s6();
s7();
s8();
s9();
s10();
ending();

const out = 'C:/Users/pc/.openclaw/workspace/work-system/deliverables/从消息流到工作流：AI如何把零散协作变成持续推进-2026-04-09-部门分享版.pptx';
pptx.writeFile({ fileName: out }).then(() => console.log(out));
