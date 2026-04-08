const pptxgen = require('D:/nvm/nodejs/node_modules/pptxgenjs');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'OpenClaw';
pptx.company = 'OpenClaw';
pptx.subject = '从消息流到工作流：AI 如何把零散协作变成持续推进';
pptx.title = '从消息流到工作流：AI 如何把零散协作变成持续推进';
pptx.lang = 'zh-CN';
pptx.theme = { headFontFace: 'Microsoft YaHei', bodyFontFace: 'Microsoft YaHei', lang: 'zh-CN' };

const C = { navy: '1F2A44', text: '1E2430', sub: '5F6B7A', line: 'C9D3E1', accent: '6E8FD8', accent2: 'DCE6FB', white: 'FFFFFF', light: 'F7F9FC', gold: 'F3B94E', pale: 'EAF1FF', pale2: 'EEF4FF' };
function bg(s, color = C.light) { s.background = { color }; }
function footer(s, n) { s.addText(String(n), { x: 12.55, y: 7.1, w: 0.25, h: 0.16, fontFace: 'Arial', fontSize: 10, color: C.sub, align: 'right', margin: 0 }); }
function header(s, title, kicker) {
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.68, line: { color: C.navy, transparency: 100 }, fill: { color: C.navy } });
  s.addText(kicker, { x: 0.6, y: 0.18, w: 3.4, h: 0.18, fontFace: 'Arial', fontSize: 12, bold: true, color: C.accent2, margin: 0 });
  s.addText(title, { x: 0.6, y: 0.94, w: 11.2, h: 0.42, fontFace: 'Microsoft YaHei', fontSize: 25, bold: true, color: C.text, margin: 0 });
  s.addShape(pptx.ShapeType.line, { x: 0.6, y: 1.5, w: 12.05, h: 0, line: { color: C.line, pt: 1.2 } });
}
function quote(s, text, subtext) {
  s.addShape(pptx.ShapeType.roundRect, { x: 0.85, y: 1.92, w: 11.65, h: 1.14, rectRadius: 0.06, line: { color: C.accent, transparency: 100 }, fill: { color: C.pale } });
  s.addText(text, { x: 1.1, y: 2.2, w: 11.0, h: 0.28, fontFace: 'Microsoft YaHei', fontSize: 22, bold: true, italic: true, color: C.navy, margin: 0 });
  if (subtext) s.addText(subtext, { x: 1.1, y: 2.6, w: 11.0, h: 0.18, fontFace: 'Microsoft YaHei', fontSize: 11, color: C.sub, margin: 0 });
}
function bullets(s, items, x, y, w, h, fs = 18, after = 12) {
  s.addText(items.map(t => ({ text: t, options: { bullet: { indent: 16 }, hanging: 3, marginLeft: 20 } })), { x, y, w, h, fontFace: 'Microsoft YaHei', fontSize: fs, color: C.text, margin: 0.03, paraSpaceAfterPt: after, breakLine: false, valign: 'top' });
}
function card(s, x, y, w, h, title, body, titleSize = 18, bodySize = 13, fill = C.white) {
  s.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.05, line: { color: C.line, pt: 1 }, fill: { color: fill } });
  s.addText(title, { x: x + 0.25, y: y + 0.24, w: w - 0.45, h: 0.24, fontFace: 'Microsoft YaHei', fontSize: titleSize, bold: true, color: C.navy, margin: 0 });
  s.addText(body, { x: x + 0.25, y: y + 0.66, w: w - 0.45, h: h - 0.86, fontFace: 'Microsoft YaHei', fontSize: bodySize, color: C.text, margin: 0.01, breakLine: false, valign: 'top' });
}
function miniTag(s, x, y, text) {
  s.addShape(pptx.ShapeType.roundRect, { x, y, w: 1.25, h: 0.32, rectRadius: 0.03, line: { color: C.accent, transparency: 100 }, fill: { color: C.accent } });
  s.addText(text, { x: x + 0.08, y: y + 0.07, w: 1.08, h: 0.12, fontFace: 'Arial', fontSize: 10, bold: true, color: C.white, align: 'center', margin: 0 });
}

function cover() {
  const s = pptx.addSlide(); bg(s, C.navy);
  miniTag(s, 0.8, 0.8, 'REAL PRACTICE');
  s.addText('从消息流到工作流', { x: 0.8, y: 1.55, w: 6.6, h: 0.55, fontFace: 'Microsoft YaHei', fontSize: 28, bold: true, color: C.white, margin: 0 });
  s.addText('AI 如何把零散协作变成持续推进', { x: 0.8, y: 2.28, w: 7.6, h: 0.55, fontFace: 'Microsoft YaHei', fontSize: 22, color: C.accent2, margin: 0 });
  s.addText('重点不是多一个工具，而是把聊天里的推进动作接住。', { x: 0.82, y: 3.3, w: 7.0, h: 0.3, fontFace: 'Microsoft YaHei', fontSize: 18, italic: true, color: 'D9E3F6', margin: 0 });
  s.addShape(pptx.ShapeType.line, { x: 7.0, y: 1.45, w: 0, h: 4.95, line: { color: '42557D', pt: 1.2 } });
  s.addText('这次汇报的主线', { x: 7.45, y: 2.0, w: 2.6, h: 0.22, fontFace: 'Microsoft YaHei', fontSize: 17, bold: true, color: C.white, margin: 0 });
  s.addText('先讲一个真实案例，再看它如何衍生出一套可复用的协作框架。', { x: 7.45, y: 2.42, w: 4.5, h: 0.62, fontFace: 'Microsoft YaHei', fontSize: 15, color: 'E3EBFC', margin: 0.01 });
  s.addText('这次刻意不去堆概念，也不去夸能力。重点只放在三件事：做了什么、已经沉淀了什么、后面准备怎么继续补。', { x: 7.45, y: 4.2, w: 4.45, h: 1.0, fontFace: 'Microsoft YaHei', fontSize: 15, color: 'E3EBFC', margin: 0.01 });
}
function s2() {
  const s = pptx.addSlide(); bg(s); header(s, '先从“日志猎人”这个专项说起', 'CASE FIRST');
  quote(s, '它一开始只是想做一个日志巡检工具，后来发现：真正有价值的，是它能把“发现、分析、推动、验证”接成闭环。');
  card(s, 0.88, 3.42, 5.75, 2.8, '它现在能做什么', '主动从日志中识别异常、慢接口、代表链路，并生成 HTML 报告。', 18, 14);
  card(s, 6.78, 3.42, 5.45, 2.8, '它现在最实际的价值', '还不是自动解决问题，而是把问题发现和问题表达做得更稳，让后面的专项更容易接住。', 18, 14, C.pale2);
  s.addText('先把边界说清楚，后面再讲它怎么反哺专项。', { x: 0.95, y: 6.48, w: 11.0, h: 0.22, fontFace: 'Microsoft YaHei', fontSize: 15, italic: true, color: C.sub, margin: 0 });
  footer(s, 2);
}
function s3() {
  const s = pptx.addSlide(); bg(s); header(s, '它怎么反哺专项：以“中江病区护士站节点 down 事件”为例', 'CASE STUDY');
  quote(s, '这个事件本来只是被动响应，但通过日志猎人 + Codex，我们拿到了一份可以继续推动整改的分析底稿。');
  card(s, 0.88, 3.42, 5.75, 2.8, '已经收口到的内容', '确认了目标接口与关键代码路径；\n识别出 3 段远程依赖串行执行、集成方式无缓存等核心问题；\n形成了第一版优化草案。', 17, 13);
  card(s, 6.78, 3.42, 5.45, 2.8, '后续计划', '补运行时分段耗时证据；\n确认现场到底走哪条分支；\n再决定是优先做止血优化，还是直接往中期治理推进。', 17, 13, C.pale2);
  s.addText('这次最重要的不是“已经解决完”，而是第一次把一个事故驱动的问题推进到了可文档化、可追踪、可继续落实的状态。对我们病区护士站研发部来说，这类案例也不只是一次问题处理，而是在性能优化、降本增效和系统稳定性这条主线上，逐步衍生出可继续推进的专项子任务。', { x: 0.95, y: 6.36, w: 11.0, h: 0.42, fontFace: 'Microsoft YaHei', fontSize: 13.5, bold: true, color: C.navy, margin: 0 });
  footer(s, 3);
}
function s4() {
  const s = pptx.addSlide(); bg(s); header(s, '这个专项逐步衍生出的协作框架', 'FRAMEWORK');
  quote(s, '一开始只是想写脚本拉日志，后来发现：如果不补一层协作承接，分析结果很容易停在“发个报告就完了”。');
  const layers = [ ['输入层', '消息流 / 临时想法 / 提醒 / 专项讨论', 2.0, 0.88, 'E8EEF9'], ['控制层', 'work-control：判断进哪个槽，是否追问，是否升级', 3.02, 0.96, 'DDE8FB'], ['运行层', 'work-system + executor + ACP/Codex：把判断变成持续执行', 4.18, 1.1, 'C9DAFA'], ['记忆层', 'memory_search + cognition：召回、复盘、迁移', 5.5, 0.94, 'B8CFF7'] ];
  layers.forEach(([title, body, y, h, color]) => { s.addShape(pptx.ShapeType.roundRect, { x: 1.0, y, w: 11.3, h, rectRadius: 0.04, line: { color: C.white, transparency: 100 }, fill: { color } }); s.addText(title, { x: 1.28, y: y + 0.18, w: 1.6, h: 0.22, fontFace: 'Microsoft YaHei', fontSize: 18, bold: true, color: C.navy, margin: 0 }); s.addText(body, { x: 3.0, y: y + 0.18, w: 8.8, h: 0.22, fontFace: 'Microsoft YaHei', fontSize: 14, color: C.text, margin: 0 }); });
  s.addText('这套框架不是先画出来的，而是在专项推进过程中逐步衍生、逐步长出来的。', { x: 1.02, y: 6.72, w: 10.8, h: 0.22, fontFace: 'Microsoft YaHei', fontSize: 15, italic: true, color: C.sub, margin: 0 });
  footer(s, 4);
}
function s5() {
  const s = pptx.addSlide(); bg(s); header(s, '为什么 `work-control` 要做成 skill', 'PART 01');
  quote(s, '模糊输入，不能直接进正式系统。');
  bullets(s, ['它解决的是“路由判断”，不是“记录存储”。','一句话过来，先判断是待办、专项、提醒，还是需要继续追问。','skill 适合承接意图识别、槽位判断、是否升级成专项等前置判断。','这样做的价值，是把后续系统的噪音和污染压在入口之前。'], 0.95, 3.45, 6.05, 2.8, 18, 12);
  s.addText('换成人话讲', { x: 7.35, y: 3.62, w: 2.0, h: 0.2, fontFace: 'Microsoft YaHei', fontSize: 17, bold: true, color: C.navy, margin: 0 });
  s.addText('在正式流程之前，先补一层“轻量分诊”。\n\n这层做得好，后面的人力投入才不会浪费在误分流、重复确认和低质量推进上。', { x: 7.35, y: 4.08, w: 4.8, h: 1.45, fontFace: 'Microsoft YaHei', fontSize: 15, color: C.text, margin: 0.01 });
  s.addShape(pptx.ShapeType.line, { x: 7.35, y: 3.95, w: 4.7, h: 0, line: { color: C.line, pt: 1 } });
  footer(s, 5);
}
function s6() {
  const s = pptx.addSlide(); bg(s); header(s, '为什么 `work-system` 不只是记录', 'PART 02');
  quote(s, '好系统不是记得多，而是能稳定推进。');
  card(s, 0.9, 3.48, 3.75, 2.35, 'Reminders', '解决“别忘”。\n把会被漏掉的事显性保住。', 18, 14);
  card(s, 4.82, 3.48, 3.75, 2.35, '今日聚焦', '解决“今天先抓什么”。\n把优先级抬头，而不是埋在消息里。', 18, 14);
  card(s, 8.74, 3.48, 3.75, 2.35, '每日总结', '解决“什么时候该提前有压力”。\n让临近节点更早被感知。', 18, 14, C.pale2);
  s.addText('同样都是工作信息，但它们解决的是不同时间尺度的问题。拆开之后，系统才既能记，又能推。', { x: 0.95, y: 6.27, w: 11.0, h: 0.22, fontFace: 'Microsoft YaHei', fontSize: 15, italic: true, color: C.sub, margin: 0 });
  footer(s, 6);
}
function s7() {
  const s = pptx.addSlide(); bg(s); header(s, '为什么需要 `executor`', 'PART 03');
  quote(s, '只有主会话，复杂任务很容易散。');
  card(s, 0.88, 3.46, 5.75, 2.72, '主会话擅长', '判断、取舍、补上下文、定优先级。\n\n它更像一个高带宽决策界面，适合做方向判断，但不适合承接所有复杂执行。', 18, 13);
  card(s, 6.78, 3.46, 5.45, 2.72, 'Executor 擅长', '把复杂任务接住，拆成动作，持续跑完。\n\n它让“想到”变成“能持续做到”，减少执行过程中的回落与断档。', 18, 13, C.pale2);
  s.addText('它不是多一个模块，而是在主会话和复杂执行之间，补一层真正的承接能力。', { x: 0.95, y: 6.48, w: 10.8, h: 0.22, fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: C.navy, margin: 0 });
  footer(s, 7);
}
function s8() {
  const s = pptx.addSlide(); bg(s); header(s, '为什么再往下要接 `ACP + Codex`', 'PART 04');
  quote(s, '复杂执行，不能只靠临时聊天。');
  card(s, 0.9, 3.45, 3.8, 2.45, '主会话', '先把问题说明白，补上下文，收口目标。', 18, 14);
  card(s, 4.77, 3.45, 3.8, 2.45, 'ACP', '把任务送进合适的执行环境，让复杂任务有地方真正展开。', 18, 14, C.pale2);
  card(s, 8.64, 3.45, 3.8, 2.45, 'Codex', '接住代码、文档、分析这些重执行内容，并把结果回写到专项里。', 18, 14);
  s.addText('它的价值，不只是“多用了一个工具”，而是把聊天里的判断推进成可执行、可落档、可复用的链路。', { x: 0.95, y: 6.34, w: 11.0, h: 0.22, fontFace: 'Microsoft YaHei', fontSize: 15, bold: true, color: C.navy, margin: 0 });
  footer(s, 8);
}
function s9() {
  const s = pptx.addSlide(); bg(s); header(s, '为什么长期记忆一定要有语义召回', 'MEMORY LAYER');
  quote(s, 'memory_search + cognition 解决的，不是“存没存下来”，而是“需要的时候，能不能把真正相关的内容找出来并接上今天的问题”。');
  card(s, 0.9, 3.42, 3.65, 2.65, 'memory_search', '负责把历史记录里最相关的片段先捞出来，让召回从“靠翻文件”变成“先有语义命中”。', 17, 13);
  card(s, 4.84, 3.42, 3.65, 2.65, 'gguf', '是这层语义召回的核心工具。它提供本地向量语义能力，让长期记忆具备“找得到、少漏、接得上”的基础条件。', 17, 13, C.pale2);
  card(s, 8.78, 3.42, 3.65, 2.65, 'cognition', '负责把召回出来的历史结论重新组织进当前判断里，让记忆不只是被找到，而是真正参与今天的分析和决策。', 17, 13);
  s.addText('这一层体现的不是“多用了一个模型文件”，而是已经开始把工具调用推进到记忆系统的底层能力建设。', { x: 0.95, y: 6.34, w: 11.0, h: 0.22, fontFace: 'Microsoft YaHei', fontSize: 15, bold: true, color: C.navy, margin: 0 });
  footer(s, 9);
}
function s10() {
  const s = pptx.addSlide(); bg(s); header(s, '如果你也想搭，从这四步开始', 'START SMALL');
  quote(s, '先搭顺序，再追求完整；先能稳定跑，再谈系统丰富。');
  const steps = [['统一入口', '不要让消息直接落正式台账，先有一层路由判断。'],['拆开分工', '把提醒、今日聚焦、每日总结分开，不要混成一团。'],['补执行层', '别把所有复杂任务都压在主会话里，给执行留承接层。'],['补记忆层', '最后再加长期记忆和复盘，让历史真正回到今天。']];
  steps.forEach((st, i) => { const x = 0.82 + i * 3.16; s.addShape(pptx.ShapeType.roundRect, { x, y: 4.2, w: 2.95, h: 1.9, rectRadius: 0.05, line: { color: i === 0 ? C.accent : C.line, pt: i === 0 ? 2 : 1 }, fill: { color: i % 2 === 0 ? C.white : C.pale2 } }); s.addShape(pptx.ShapeType.ellipse, { x: x + 0.18, y: 4.38, w: 0.42, h: 0.42, line: { color: C.accent, transparency: 100 }, fill: { color: C.accent } }); s.addText(String(i + 1), { x: x + 0.18, y: 4.41, w: 0.42, h: 0.14, fontFace: 'Arial', fontSize: 11, bold: true, color: C.white, align: 'center', margin: 0 }); s.addText(st[0], { x: x + 0.72, y: 4.36, w: 1.75, h: 0.2, fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: C.navy, margin: 0 }); s.addText(st[1], { x: x + 0.18, y: 4.92, w: 2.48, h: 0.72, fontFace: 'Microsoft YaHei', fontSize: 11.5, color: C.text, margin: 0.01 }); });
  footer(s, 10);
}
function ending() {
  const s = pptx.addSlide(); bg(s, C.navy);
  s.addText('重点不是让 AI 多回答一次，', { x: 1.0, y: 2.05, w: 9.6, h: 0.48, fontFace: 'Microsoft YaHei', fontSize: 26, bold: true, color: C.white, margin: 0 });
  s.addText('而是让协作少断一次。', { x: 1.0, y: 2.78, w: 8.0, h: 0.48, fontFace: 'Microsoft YaHei', fontSize: 26, bold: true, color: C.gold, margin: 0 });
  s.addText('从消息流到工作流，本质上是在给协作补“承接层”。', { x: 1.02, y: 4.02, w: 8.8, h: 0.28, fontFace: 'Microsoft YaHei', fontSize: 18, italic: true, color: 'DCE6FB', margin: 0 });
  s.addText('THANKS', { x: 1.0, y: 5.15, w: 2.4, h: 0.28, fontFace: 'Arial', fontSize: 20, bold: true, color: C.accent2, margin: 0 });
}

cover(); s2(); s3(); s4(); s5(); s6(); s7(); s8(); s9(); s10(); ending();
const out = 'C:/Users/pc/.openclaw/workspace/work-system/deliverables/从消息流到工作流：AI如何把零散协作变成持续推进-v7-案例优先版.pptx';
pptx.writeFile({ fileName: out }).then(() => console.log(out));
