const pptxgen = require('D:/nvm/nodejs/node_modules/pptxgenjs');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'OpenClaw';
pptx.company = 'OpenClaw';
pptx.subject = '从消息流到工作流：AI 如何把零散协作变成持续推进';
pptx.title = '从消息流到工作流：AI 如何把零散协作变成持续推进';
pptx.lang = 'zh-CN';
pptx.theme = {
  headFontFace: 'Microsoft YaHei',
  bodyFontFace: 'Microsoft YaHei',
  lang: 'zh-CN'
};

const C = {
  navy: '1F2A44',
  text: '1E2430',
  sub: '5F6B7A',
  line: 'C9D3E1',
  accent: '6E8FD8',
  accent2: 'DCE6FB',
  white: 'FFFFFF',
  light: 'F7F9FC',
  gold: 'F3B94E',
  pale: 'EAF1FF'
};

function bg(slide, color = C.light) { slide.background = { color }; }
function footer(slide, n) {
  slide.addText(String(n), { x: 12.55, y: 7.1, w: 0.25, h: 0.16, fontFace: 'Arial', fontSize: 10, color: C.sub, align: 'right', margin: 0 });
}
function header(slide, title, kicker) {
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.68, line: { color: C.navy, transparency: 100 }, fill: { color: C.navy } });
  slide.addText(kicker, { x: 0.6, y: 0.18, w: 3, h: 0.18, fontFace: 'Arial', fontSize: 12, bold: true, color: C.accent2, margin: 0 });
  slide.addText(title, { x: 0.6, y: 0.94, w: 10.8, h: 0.42, fontFace: 'Microsoft YaHei', fontSize: 25, bold: true, color: C.text, margin: 0 });
  slide.addShape(pptx.ShapeType.line, { x: 0.6, y: 1.5, w: 12.05, h: 0, line: { color: C.line, pt: 1.2 } });
}
function quote(slide, text, subtext) {
  slide.addShape(pptx.ShapeType.roundRect, { x: 0.85, y: 1.92, w: 11.65, h: 1.14, rectRadius: 0.06, line: { color: C.accent, transparency: 100 }, fill: { color: C.pale } });
  slide.addText(text, { x: 1.1, y: 2.2, w: 11.0, h: 0.28, fontFace: 'Microsoft YaHei', fontSize: 22, bold: true, italic: true, color: C.navy, margin: 0 });
  if (subtext) slide.addText(subtext, { x: 1.1, y: 2.6, w: 11.0, h: 0.18, fontFace: 'Microsoft YaHei', fontSize: 11, color: C.sub, margin: 0 });
}
function bullets(slide, items, x, y, w, h, fs = 18, after = 12) {
  slide.addText(items.map(t => ({ text: t, options: { bullet: { indent: 16 }, hanging: 3, marginLeft: 20 } })), {
    x, y, w, h, fontFace: 'Microsoft YaHei', fontSize: fs, color: C.text, margin: 0.03, paraSpaceAfterPt: after, breakLine: false, valign: 'top'
  });
}
function card(slide, x, y, w, h, title, body, titleSize = 18, bodySize = 13) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.05, line: { color: C.line, pt: 1 }, fill: { color: C.white } });
  slide.addText(title, { x: x + 0.25, y: y + 0.24, w: w - 0.45, h: 0.24, fontFace: 'Microsoft YaHei', fontSize: titleSize, bold: true, color: C.navy, margin: 0 });
  slide.addText(body, { x: x + 0.25, y: y + 0.66, w: w - 0.45, h: h - 0.86, fontFace: 'Microsoft YaHei', fontSize: bodySize, color: C.text, margin: 0.01, breakLine: false, valign: 'top' });
}

function cover() {
  const s = pptx.addSlide();
  bg(s, C.navy);
  s.addShape(pptx.ShapeType.roundRect, { x: 0.72, y: 0.78, w: 5.0, h: 0.42, rectRadius: 0.04, line: { color: C.accent, transparency: 100 }, fill: { color: C.accent } });
  s.addText('真实协作实践 · 面向管理视角表达', { x: 0.98, y: 0.88, w: 4.5, h: 0.14, fontFace: 'Microsoft YaHei', fontSize: 12, bold: true, color: C.white, margin: 0 });
  s.addText('从消息流到工作流', { x: 0.8, y: 1.62, w: 6.6, h: 0.55, fontFace: 'Microsoft YaHei', fontSize: 28, bold: true, color: C.white, margin: 0 });
  s.addText('AI 如何把零散协作变成持续推进', { x: 0.8, y: 2.34, w: 7.6, h: 0.55, fontFace: 'Microsoft YaHei', fontSize: 22, color: C.accent2, margin: 0 });
  s.addText('重点不是多一个工具，而是把聊天里的推进动作接住。', { x: 0.82, y: 3.38, w: 6.8, h: 0.3, fontFace: 'Microsoft YaHei', fontSize: 18, italic: true, color: 'D9E3F6', margin: 0 });
  s.addShape(pptx.ShapeType.line, { x: 6.95, y: 1.45, w: 0, h: 4.8, line: { color: '42557D', pt: 1.3 } });
  card(s, 7.35, 2.0, 4.9, 1.3, '这次汇报的重点', '不展开讲“AI 有多聪明”，而是聚焦：它如何把零散协作转成可持续执行，并带来更可感知的管理收益。', 17, 13);
  card(s, 7.35, 3.75, 4.9, 1.95, '管理层更关心什么', '效率是否提升\n风险能否前置\n重复成本是否下降\n决策有没有更清晰的依据', 17, 15);
}

function s2() {
  const s = pptx.addSlide();
  bg(s); header(s, '先别看工具，先看问题本身', 'WHY THIS MATTERS');
  quote(s, '多数协作卡住，不是没人说，而是说过就散了。');
  card(s, 0.88, 3.45, 5.75, 2.7, '常见断点', '1. 信息留在聊天里，后面没人接。\n2. 优先级没有显性化，今天先抓什么不清楚。\n3. 临近节点才感到压力，准备总是偏晚。');
  card(s, 6.78, 3.45, 5.45, 2.7, '管理视角下，这意味着什么', '表面上看是信息分散，本质上会进一步放大执行波动、协同摩擦和管理盲区。\n\n真正要解决的，不是“AI 会不会答”，而是“协作能不能被持续承接”。');
  footer(s, 2);
}

function s3() {
  const s = pptx.addSlide();
  bg(s); header(s, '我的做法：把协作拆成四层', 'SYSTEM MAP');
  const layers = [
    ['输入层', '消息流 / 临时想法 / 提醒 / 专项讨论', 2.0, 0.88, 'E8EEF9'],
    ['控制层', 'work-control：判断进哪个槽，是否追问，是否升级', 3.02, 0.96, 'DDE8FB'],
    ['运行层', 'work-system + executor + ACP/Codex：把判断变成持续执行', 4.18, 1.1, 'C9DAFA'],
    ['记忆层', 'memory_search + cognition：召回、复盘、迁移', 5.5, 0.94, 'B8CFF7']
  ];
  layers.forEach(([title, body, y, h, color]) => {
    s.addShape(pptx.ShapeType.roundRect, { x: 1.0, y, w: 11.3, h, rectRadius: 0.04, line: { color: C.white, transparency: 100 }, fill: { color } });
    s.addText(title, { x: 1.28, y: y + 0.18, w: 1.6, h: 0.22, fontFace: 'Microsoft YaHei', fontSize: 18, bold: true, color: C.navy, margin: 0 });
    s.addText(body, { x: 3.0, y: y + 0.18, w: 8.8, h: 0.22, fontFace: 'Microsoft YaHei', fontSize: 14, color: C.text, margin: 0 });
  });
  s.addText('不是堆模块，而是让每层只干一类事；这样才更容易控制复杂度，也更容易解释投入产出。', { x: 1.02, y: 6.72, w: 10.8, h: 0.22, fontFace: 'Microsoft YaHei', fontSize: 15, italic: true, color: C.sub, margin: 0 });
  footer(s, 3);
}

function s4() {
  const s = pptx.addSlide();
  bg(s); header(s, '为什么 `work-control` 要做成 skill', 'PART 01');
  quote(s, '模糊输入，不能直接进正式系统。');
  bullets(s, [
    '它解决的是“路由判断”，不是“记录存储”。',
    '一句话过来，先判断是待办、专项、提醒，还是需要继续追问。',
    'skill 适合承接意图识别、槽位判断、是否升级成专项等前置判断。',
    '这样做的价值，是把后续系统的噪音和污染压在入口之前。'
  ], 0.95, 3.45, 6.05, 2.8, 18, 12);
  card(s, 7.28, 3.55, 5.0, 2.25, '管理层可以把它理解为', '在正式流程之前，先补一层“轻量分诊”。\n\n这层做得好，后面的人力投入才不会浪费在误分流、重复确认和低质量推进上。', 17, 13);
  footer(s, 4);
}

function s5() {
  const s = pptx.addSlide();
  bg(s); header(s, '为什么 `work-system` 不只是记录', 'PART 02');
  quote(s, '好系统不是记得多，而是能稳定推进。');
  card(s, 0.9, 3.48, 3.75, 2.35, 'Reminders', '解决“别忘”。\n把会被漏掉的事显性保住。', 18, 14);
  card(s, 4.82, 3.48, 3.75, 2.35, '今日聚焦', '解决“今天先抓什么”。\n把优先级抬头，而不是埋在消息里。', 18, 14);
  card(s, 8.74, 3.48, 3.75, 2.35, '每日总结', '解决“什么时候该提前有压力”。\n让临近节点更早被感知。', 18, 14);
  s.addText('同样都是工作信息，但它们解决的是不同时间尺度的问题。拆开之后，系统才既能记，又能推。', { x: 0.95, y: 6.27, w: 11.0, h: 0.22, fontFace: 'Microsoft YaHei', fontSize: 15, italic: true, color: C.sub, margin: 0 });
  footer(s, 5);
}

function s6() {
  const s = pptx.addSlide();
  bg(s); header(s, '为什么需要 `executor` 这一层', 'PART 03');
  quote(s, '只有主会话，复杂任务很容易散。');
  card(s, 0.88, 3.46, 5.75, 2.72, '主会话擅长', '判断、取舍、补上下文、定优先级。\n\n它更像一个高带宽决策界面，适合做方向判断，但不适合承接所有复杂执行。', 18, 13);
  card(s, 6.78, 3.46, 5.45, 2.72, 'Executor 擅长', '把复杂任务接住，拆成动作，持续跑完。\n\n它让“想到”变成“能持续做到”，减少执行过程中的回落与断档。', 18, 13);
  s.addText('它不是多一个模块，而是在主会话和复杂执行之间，补一层真正的承接能力。', { x: 0.95, y: 6.48, w: 10.8, h: 0.22, fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: C.navy, margin: 0 });
  footer(s, 6);
}

function s7() {
  const s = pptx.addSlide();
  bg(s); header(s, '为什么再往下要接 `ACP + Codex`', 'PART 04');
  quote(s, '复杂执行，不能只靠临时聊天。');
  bullets(s, [
    '主会话可以先把问题整理成更专业的执行提示。',
    'Codex 更适合接代码、文档、专项推进等高复杂度执行。',
    '它产出的不只是一次性答案，还可以回收到专项进度和后续协作里。',
    '所以它的价值，不只是“更会写代码”，而是更适合承接复杂执行。'
  ], 0.95, 3.42, 6.2, 2.8, 18, 12);
  card(s, 7.28, 3.58, 5.0, 2.18, '对管理层的实际意义', '把专家经验、执行动作和过程产出更稳定地沉淀下来。\n\n这会让复杂任务的推进更可复用，也更便于后续追踪和复盘。', 17, 13);
  footer(s, 7);
}

function s8() {
  const s = pptx.addSlide();
  bg(s); header(s, '“日志猎人”案例：AI 价值不只在分析，更在治理闭环', 'CASE STUDY');
  quote(s, '这个案例最有价值的，不是多查了一次日志，而是把“发现问题—分析问题—推动改进”接成了闭环。');
  card(s, 0.88, 3.42, 3.75, 2.78, '已实现的实战价值', '已能从日志中主动识别 ERROR、慢接口和代表链路，并生成可读报告，支撑问题发现、排查和复盘。', 17, 13);
  card(s, 4.78, 3.42, 3.75, 2.78, '对管理层更重要的启示', '价值不只是“技术同学更方便”，而是让风险暴露更前、排查路径更短、优化动作更容易被组织吸收。', 17, 13);
  card(s, 8.68, 3.42, 3.75, 2.78, '当前表达边界', '这不是说已经自动解决了所有问题，而是已经把“主动巡检与持续治理”的基础链路搭起来了。', 17, 13);
  footer(s, 8);
}

function s9() {
  const s = pptx.addSlide();
  bg(s); header(s, '从“日志猎人”能看到的四类管理收益', 'MANAGEMENT VALUE');
  quote(s, '不夸大能力，但可以清楚看到：当协作被接住后，收益会从个人效率扩展到组织管理。');
  const items = [
    ['效率提升', '把问题发现、代表链路补齐、结果整理这些高重复动作标准化，减少人工反复翻找与口头对齐。'],
    ['风险前置', '从被动等故障、等反馈，转向更早暴露异常信号与性能问题，管理动作能更早介入。'],
    ['成本优化', '减少重复排查、重复沟通、重复解释的隐性成本，让同样的人力投入产出更多有效动作。'],
    ['决策支撑', '把零散现象转成更结构化的信息，为后续优先级判断、专项投入和治理方向提供依据。']
  ];
  items.forEach((it, i) => {
    const x = i < 2 ? 0.9 + i * 6.0 : 0.9 + (i - 2) * 6.0;
    const y = i < 2 ? 3.45 : 5.3;
    card(s, x, y, 5.5, 1.45, it[0], it[1], 17, 12.5);
  });
  footer(s, 9);
}

function s10() {
  const s = pptx.addSlide();
  bg(s); header(s, '如果你也想搭，从这四步开始', 'START SMALL');
  quote(s, '先搭顺序，再追求完整；先能稳定跑，再谈系统丰富。');
  const steps = [
    ['统一入口', '不要让消息直接落正式台账，先有一层路由判断。'],
    ['拆开分工', '把提醒、今日聚焦、每日总结分开，不要混成一团。'],
    ['补执行层', '别把所有复杂任务都压在主对话里，给执行留承接层。'],
    ['补记忆层', '最后再加长期记忆和复盘，让历史真正回到今天。']
  ];
  steps.forEach((st, i) => {
    const x = 0.82 + i * 3.16;
    s.addShape(pptx.ShapeType.roundRect, { x, y: 4.2, w: 2.95, h: 1.9, rectRadius: 0.05, line: { color: i === 0 ? C.accent : C.line, pt: i === 0 ? 2 : 1 }, fill: { color: C.white } });
    s.addShape(pptx.ShapeType.ellipse, { x: x + 0.18, y: 4.38, w: 0.42, h: 0.42, line: { color: C.accent, transparency: 100 }, fill: { color: C.accent } });
    s.addText(String(i + 1), { x: x + 0.18, y: 4.41, w: 0.42, h: 0.14, fontFace: 'Arial', fontSize: 11, bold: true, color: C.white, align: 'center', margin: 0 });
    s.addText(st[0], { x: x + 0.72, y: 4.36, w: 1.75, h: 0.2, fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: C.navy, margin: 0 });
    s.addText(st[1], { x: x + 0.18, y: 4.92, w: 2.48, h: 0.72, fontFace: 'Microsoft YaHei', fontSize: 11.5, color: C.text, margin: 0.01 });
  });
  footer(s, 10);
}

function ending() {
  const s = pptx.addSlide();
  bg(s, C.navy);
  s.addText('重点不是让 AI 多回答一次，', { x: 1.0, y: 2.05, w: 9.6, h: 0.48, fontFace: 'Microsoft YaHei', fontSize: 26, bold: true, color: C.white, margin: 0 });
  s.addText('而是让协作少断一次。', { x: 1.0, y: 2.78, w: 8.0, h: 0.48, fontFace: 'Microsoft YaHei', fontSize: 26, bold: true, color: C.gold, margin: 0 });
  s.addText('从消息流到工作流，本质上是在给协作补“承接层”。', { x: 1.02, y: 4.02, w: 8.8, h: 0.28, fontFace: 'Microsoft YaHei', fontSize: 18, italic: true, color: 'DCE6FB', margin: 0 });
  s.addText('THANKS', { x: 1.0, y: 5.15, w: 2.4, h: 0.28, fontFace: 'Arial', fontSize: 20, bold: true, color: C.accent2, margin: 0 });
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

const out = 'C:/Users/pc/.openclaw/workspace/work-system/deliverables/从消息流到工作流：AI如何把零散协作变成持续推进-v3-领导层版.pptx';
pptx.writeFile({ fileName: out }).then(() => console.log(out));
