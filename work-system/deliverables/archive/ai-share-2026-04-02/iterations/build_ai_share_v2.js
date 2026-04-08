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
  blue: '3E5C99',
  ice: 'EAF0FA',
  text: '1E2430',
  sub: '5F6B7A',
  line: 'C9D3E1',
  accent: '6E8FD8',
  accent2: 'DCE6FB',
  white: 'FFFFFF',
  light: 'F7F9FC',
  gold: 'F3B94E'
};

function addBg(slide, color = C.light) {
  slide.background = { color };
}

function addHeaderBand(slide, title, kicker) {
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.7, line: { color: C.navy, transparency: 100 }, fill: { color: C.navy } });
  slide.addText(kicker || '', {
    x: 0.6, y: 0.18, w: 2.5, h: 0.2,
    fontFace: 'Microsoft YaHei', fontSize: 12, bold: true, color: C.accent2,
    margin: 0
  });
  slide.addText(title, {
    x: 0.6, y: 0.95, w: 9.6, h: 0.45,
    fontFace: 'Microsoft YaHei', fontSize: 26, bold: true, color: C.text,
    margin: 0
  });
  slide.addShape(pptx.ShapeType.line, { x: 0.6, y: 1.52, w: 12.1, h: 0, line: { color: C.line, pt: 1.2 } });
}

function addFooter(slide, page) {
  slide.addText(String(page), {
    x: 12.55, y: 7.1, w: 0.3, h: 0.2,
    fontFace: 'Arial', fontSize: 10, color: C.sub, align: 'right', margin: 0
  });
}

function addBulletList(slide, items, opts = {}) {
  const x = opts.x ?? 0.9;
  const y = opts.y ?? 1.9;
  const w = opts.w ?? 5.6;
  const h = opts.h ?? 4.8;
  const fs = opts.fontSize ?? 20;
  const color = opts.color ?? C.text;
  const bulletIndent = opts.bulletIndent ?? 16;
  const marginLeft = opts.marginLeft ?? 20;
  const paras = [];
  items.forEach((item) => {
    if (typeof item === 'string') {
      paras.push({ text: item, options: { bullet: { indent: bulletIndent }, hanging: 3, marginLeft } });
    } else {
      paras.push(item);
    }
  });
  slide.addText(paras, {
    x, y, w, h,
    fontFace: 'Microsoft YaHei', fontSize: fs, color,
    breakLine: false, margin: 0.03,
    paraSpaceAfterPt: opts.paraSpaceAfterPt ?? 14,
    valign: 'top'
  });
}

function addQuote(slide, text, subtext) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.85, y: 1.95, w: 11.6, h: 1.2,
    rectRadius: 0.08,
    line: { color: C.accent, transparency: 100 },
    fill: { color: C.accent2 }
  });
  slide.addText(text, {
    x: 1.1, y: 2.22, w: 11.1, h: 0.32,
    fontFace: 'Microsoft YaHei', fontSize: 22, bold: true, italic: true, color: C.navy,
    margin: 0, align: 'left'
  });
  if (subtext) {
    slide.addText(subtext, {
      x: 1.1, y: 2.63, w: 11.0, h: 0.24,
      fontFace: 'Microsoft YaHei', fontSize: 11, color: C.sub,
      margin: 0
    });
  }
}

function addTwoColCards(slide, leftTitle, leftBody, rightTitle, rightBody) {
  const y = 3.45;
  const boxH = 2.8;
  const leftX = 0.85;
  const rightX = 6.75;
  [
    [leftX, leftTitle, leftBody],
    [rightX, rightTitle, rightBody]
  ].forEach(([x, title, body]) => {
    slide.addShape(pptx.ShapeType.roundRect, {
      x, y, w: 5.7, h: boxH,
      rectRadius: 0.05,
      line: { color: C.line, pt: 1 },
      fill: { color: C.white }
    });
    slide.addText(title, {
      x: x + 0.28, y: y + 0.25, w: 5.0, h: 0.28,
      fontFace: 'Microsoft YaHei', fontSize: 18, bold: true, color: C.navy,
      margin: 0
    });
    slide.addText(body, {
      x: x + 0.28, y: y + 0.68, w: 5.05, h: 1.75,
      fontFace: 'Microsoft YaHei', fontSize: 13, color: C.text,
      breakLine: false, margin: 0.01, valign: 'top'
    });
  });
}

function addStepRow(slide, steps) {
  const startX = 0.8;
  const y = 4.2;
  const cardW = 2.95;
  const gap = 0.22;
  steps.forEach((step, idx) => {
    const x = startX + idx * (cardW + gap);
    slide.addShape(pptx.ShapeType.roundRect, {
      x, y, w: cardW, h: 1.9,
      rectRadius: 0.05,
      line: { color: idx === 0 ? C.accent : C.line, pt: idx === 0 ? 2 : 1 },
      fill: { color: C.white }
    });
    slide.addShape(pptx.ShapeType.ellipse, {
      x: x + 0.18, y: y + 0.18, w: 0.42, h: 0.42,
      line: { color: C.accent, transparency: 100 }, fill: { color: C.accent }
    });
    slide.addText(String(idx + 1), {
      x: x + 0.18, y: y + 0.21, w: 0.42, h: 0.16,
      fontFace: 'Arial', fontSize: 11, bold: true, color: C.white, align: 'center', margin: 0
    });
    slide.addText(step.title, {
      x: x + 0.7, y: y + 0.18, w: 1.95, h: 0.22,
      fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: C.navy, margin: 0
    });
    slide.addText(step.body, {
      x: x + 0.18, y: y + 0.72, w: 2.5, h: 0.8,
      fontFace: 'Microsoft YaHei', fontSize: 11.5, color: C.text, margin: 0.01
    });
  });
}

function addLayerDiagram(slide) {
  const layers = [
    { y: 2.0, h: 0.9, color: 'E8EEF9', title: '输入层', body: '消息流 / 临时想法 / 提醒 / 专项讨论' },
    { y: 3.05, h: 1.0, color: 'DDE8FB', title: '控制层', body: 'work-control：判断进哪个槽，是否追问，是否升级' },
    { y: 4.25, h: 1.15, color: 'C9DAFA', title: '运行层', body: 'work-system + executor + ACP/Codex：把判断变成持续执行' },
    { y: 5.6, h: 0.95, color: 'B8CFF7', title: '记忆层', body: 'memory_search + cognition：召回、复盘、迁移' }
  ];
  layers.forEach((layer) => {
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 1.0, y: layer.y, w: 11.3, h: layer.h,
      rectRadius: 0.04,
      line: { color: C.white, transparency: 100 },
      fill: { color: layer.color }
    });
    slide.addText(layer.title, {
      x: 1.3, y: layer.y + 0.18, w: 1.5, h: 0.22,
      fontFace: 'Microsoft YaHei', fontSize: 18, bold: true, color: C.navy, margin: 0
    });
    slide.addText(layer.body, {
      x: 3.0, y: layer.y + 0.18, w: 8.7, h: 0.26,
      fontFace: 'Microsoft YaHei', fontSize: 14, color: C.text, margin: 0
    });
  });
}

function cover() {
  const slide = pptx.addSlide();
  addBg(slide, C.navy);
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 7.5, line: { color: C.navy, transparency: 100 }, fill: { color: C.navy } });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.72, y: 0.78, w: 4.7, h: 0.42,
    rectRadius: 0.04, line: { color: C.accent, transparency: 100 }, fill: { color: C.accent }
  });
  slide.addText('一线真实协作实践拆解', {
    x: 0.96, y: 0.88, w: 4.2, h: 0.16,
    fontFace: 'Microsoft YaHei', fontSize: 12, bold: true, color: C.white, margin: 0
  });
  slide.addText('从消息流到工作流', {
    x: 0.8, y: 1.6, w: 6.8, h: 0.65,
    fontFace: 'Microsoft YaHei', fontSize: 28, bold: true, color: C.white, margin: 0
  });
  slide.addText('AI 如何把零散协作变成持续推进', {
    x: 0.8, y: 2.38, w: 7.7, h: 0.65,
    fontFace: 'Microsoft YaHei', fontSize: 22, color: C.accent2, margin: 0
  });
  slide.addText('重点不是多一个工具，而是把聊天里的推进动作接住。', {
    x: 0.82, y: 3.4, w: 6.8, h: 0.34,
    fontFace: 'Microsoft YaHei', fontSize: 18, italic: true, color: 'D9E3F6', margin: 0
  });
  const cards = [
    ['消息', '零散输入'],
    ['判断', '分类与取舍'],
    ['执行', '专项承接'],
    ['记忆', '召回与迁移']
  ];
  cards.forEach((card, idx) => {
    const x = 0.86 + idx * 1.45;
    slide.addShape(pptx.ShapeType.roundRect, {
      x, y: 5.2, w: 1.25, h: 1.05,
      rectRadius: 0.04,
      line: { color: '5D729E', pt: 1 },
      fill: { color: '243252' }
    });
    slide.addText(card[0], {
      x: x + 0.18, y: 5.45, w: 0.9, h: 0.2,
      fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: C.white, align: 'center', margin: 0
    });
    slide.addText(card[1], {
      x: x + 0.08, y: 5.82, w: 1.1, h: 0.16,
      fontFace: 'Microsoft YaHei', fontSize: 9.5, color: 'C9D6EF', align: 'center', margin: 0
    });
  });
  slide.addShape(pptx.ShapeType.line, { x: 6.9, y: 1.45, w: 0, h: 4.8, line: { color: '42557D', pt: 1.3 } });
  slide.addText('适合讲给还不熟悉 OpenClaw 的同事：\n先讲问题，再讲分层，再讲为什么值得这样搭。', {
    x: 7.35, y: 2.05, w: 4.95, h: 1.35,
    fontFace: 'Microsoft YaHei', fontSize: 16, color: C.white, breakLine: false, margin: 0.02
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 7.35, y: 4.35, w: 4.9, h: 1.4,
    rectRadius: 0.05,
    line: { color: C.gold, pt: 1.2 }, fill: { color: '243252' }
  });
  slide.addText('分享主线', {
    x: 7.65, y: 4.62, w: 1.2, h: 0.2,
    fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: C.gold, margin: 0
  });
  slide.addText('为什么会散 → 为什么这样分层 → 如果你也想搭，该从哪一步开始', {
    x: 7.65, y: 4.98, w: 4.2, h: 0.46,
    fontFace: 'Microsoft YaHei', fontSize: 13, color: 'DDE6F8', margin: 0.01
  });
}

function slide2() {
  const slide = pptx.addSlide();
  addBg(slide);
  addHeaderBand(slide, '先别看工具，先看问题本身', 'WHY THIS MATTERS');
  addQuote(slide, '多数协作卡住，不是没人说，而是说过就散了。');
  addTwoColCards(
    slide,
    '典型断点',
    [
      '1. 信息留在聊天里，后面没人接。',
      '2. 优先级没有显性化，今天先抓什么不清楚。',
      '3. 临近节点才感到压力，准备总是偏晚。'
    ].join('\n'),
    '真正要解决的事',
    '不是让 AI 多回答一次，而是让消息里的判断、提醒、执行和复盘都有地方承接。'
  );
  addFooter(slide, 2);
}

function slide3() {
  const slide = pptx.addSlide();
  addBg(slide);
  addHeaderBand(slide, '我的做法：把协作拆成四层', 'SYSTEM MAP');
  addLayerDiagram(slide);
  slide.addText('不是堆模块，而是让每层只干一类事。这样系统才不容易互相污染。', {
    x: 1.0, y: 6.75, w: 10.2, h: 0.28,
    fontFace: 'Microsoft YaHei', fontSize: 16, color: C.sub, italic: true, margin: 0
  });
  addFooter(slide, 3);
}

function slide4() {
  const slide = pptx.addSlide();
  addBg(slide);
  addHeaderBand(slide, '为什么 `work-control` 要做成 skill', 'PART 01');
  addQuote(slide, '模糊输入，不能直接进正式系统。');
  addBulletList(slide, [
    '它解决的是“路由判断”，不是“记录存储”。',
    '一句话过来，先判断是待办、专项、提醒，还是需要继续追问。',
    '适合放在 skill：因为 skill 的本质就是把非结构化输入接成结构化入口。',
    '这样做的好处，是后面的系统不会被模糊信息直接污染。'
  ], { x: 0.95, y: 3.55, w: 6.0, h: 2.7, fontSize: 18, paraSpaceAfterPt: 12 });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 7.35, y: 3.62, w: 4.9, h: 2.35,
    rectRadius: 0.05, line: { color: C.line, pt: 1 }, fill: { color: C.white }
  });
  slide.addText('它最该回答的不是“存哪儿”，而是：', {
    x: 7.65, y: 3.92, w: 4.1, h: 0.25,
    fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: C.navy, margin: 0
  });
  addBulletList(slide, [
    '这句话属于什么类型？',
    '要不要追问补全？',
    '值不值得升级成专项？'
  ], { x: 7.65, y: 4.38, w: 3.8, h: 1.2, fontSize: 14, paraSpaceAfterPt: 10 });
  addFooter(slide, 4);
}

function slide5() {
  const slide = pptx.addSlide();
  addBg(slide);
  addHeaderBand(slide, '为什么 `work-system` 不只是记录', 'PART 02');
  addQuote(slide, '好系统不是记得多，而是能稳定推进。');
  const cards = [
    ['Reminders', '解决“别忘”', '把会被漏掉的事显性保住。'],
    ['今日聚焦', '解决“今天先抓什么”', '把优先级抬头，而不是埋在消息里。'],
    ['每日总结', '解决“什么时候该提前有压力”', '让临近节点更早被感知，而不是最后一天才想起。']
  ];
  cards.forEach((card, idx) => {
    const x = 0.92 + idx * 4.05;
    slide.addShape(pptx.ShapeType.roundRect, {
      x, y: 3.45, w: 3.65, h: 2.35,
      rectRadius: 0.05, line: { color: C.line, pt: 1 }, fill: { color: C.white }
    });
    slide.addText(card[0], {
      x: x + 0.22, y: 3.73, w: 1.8, h: 0.22,
      fontFace: 'Arial', fontSize: 15, bold: true, color: C.accent, margin: 0
    });
    slide.addText(card[1], {
      x: x + 0.22, y: 4.13, w: 3.0, h: 0.28,
      fontFace: 'Microsoft YaHei', fontSize: 18, bold: true, color: C.navy, margin: 0
    });
    slide.addText(card[2], {
      x: x + 0.22, y: 4.68, w: 3.05, h: 0.72,
      fontFace: 'Microsoft YaHei', fontSize: 13, color: C.text, margin: 0.01
    });
  });
  slide.addText('同样都是工作信息，但它们解决的是不同时间尺度的问题，所以必须拆开。', {
    x: 0.95, y: 6.32, w: 10.8, h: 0.24,
    fontFace: 'Microsoft YaHei', fontSize: 15, color: C.sub, italic: true, margin: 0
  });
  addFooter(slide, 5);
}

function slide6() {
  const slide = pptx.addSlide();
  addBg(slide);
  addHeaderBand(slide, '为什么需要 `executor` 这一层', 'PART 03');
  addQuote(slide, '只有主会话，复杂任务很容易散。');
  addTwoColCards(
    slide,
    '主会话擅长',
    '判断、取舍、补上下文、定优先级。\n\n它更像一个高带宽决策界面。',
    'Executor 擅长',
    '把复杂任务接住，拆成动作，持续跑完。\n\n它让“想到”变成“能持续做到”。'
  );
  slide.addText('所以 executor 不是多一个模块，而是专门补“执行承接层”。', {
    x: 0.9, y: 6.5, w: 10.2, h: 0.24,
    fontFace: 'Microsoft YaHei', fontSize: 16, bold: true, color: C.navy, margin: 0
  });
  addFooter(slide, 6);
}

function slide7() {
  const slide = pptx.addSlide();
  addBg(slide);
  addHeaderBand(slide, '为什么再往下要接 `ACP + Codex`', 'PART 04');
  addQuote(slide, '复杂执行，不能只靠临时聊天。');
  addBulletList(slide, [
    '主会话可以先把问题整理成更专业的执行提示。',
    'Codex 适合接代码、文档、专项推进等高复杂度执行。',
    '它产出的不只是“一次性答案”，还可以回收到专项进度与后续协作里。',
    '所以它的价值，不只是更会写代码，而是更适合承接复杂执行。'
  ], { x: 0.95, y: 3.45, w: 6.2, h: 2.7, fontSize: 18, paraSpaceAfterPt: 12 });
  slide.addShape(pptx.ShapeType.chevron, {
    x: 7.2, y: 3.65, w: 4.55, h: 1.9,
    line: { color: C.accent, pt: 1 }, fill: { color: 'EAF1FF' }
  });
  slide.addText('主会话\n梳理问题', {
    x: 7.42, y: 4.15, w: 1.05, h: 0.62,
    fontFace: 'Microsoft YaHei', fontSize: 15, bold: true, color: C.navy, align: 'center', margin: 0
  });
  slide.addText('→', {
    x: 8.73, y: 4.18, w: 0.45, h: 0.25,
    fontFace: 'Arial', fontSize: 18, bold: true, color: C.accent, align: 'center', margin: 0
  });
  slide.addText('Codex\n执行与产出', {
    x: 9.08, y: 4.15, w: 1.2, h: 0.62,
    fontFace: 'Microsoft YaHei', fontSize: 15, bold: true, color: C.navy, align: 'center', margin: 0
  });
  slide.addText('→', {
    x: 10.48, y: 4.18, w: 0.45, h: 0.25,
    fontFace: 'Arial', fontSize: 18, bold: true, color: C.accent, align: 'center', margin: 0
  });
  slide.addText('专项系统\n回收沉淀', {
    x: 10.8, y: 4.15, w: 1.2, h: 0.62,
    fontFace: 'Microsoft YaHei', fontSize: 15, bold: true, color: C.navy, align: 'center', margin: 0
  });
  addFooter(slide, 7);
}

function slide8() {
  const slide = pptx.addSlide();
  addBg(slide);
  addHeaderBand(slide, '为什么长期记忆一定要有语义召回', 'MEMORY');
  addQuote(slide, '协作真正的门槛，不是记录，而是以后还能接上。');
  const xs = [0.92, 4.35, 7.78];
  ['找得到', '少漏', '接得上'].forEach((title, idx) => {
    slide.addShape(pptx.ShapeType.roundRect, {
      x: xs[idx], y: 3.48, w: 2.85, h: 1.9,
      rectRadius: 0.05, line: { color: C.line, pt: 1 }, fill: { color: C.white }
    });
    slide.addText(title, {
      x: xs[idx] + 0.22, y: 3.82, w: 2.2, h: 0.26,
      fontFace: 'Microsoft YaHei', fontSize: 22, bold: true, color: C.navy, align: 'center', margin: 0
    });
    const desc = [
      '换个说法也能把相关记忆捞出来。',
      '同一主题散落在多天记录里，也不容易漏掉。',
      '先前决策和今天问题之间，能恢复连续性。'
    ][idx];
    slide.addText(desc, {
      x: xs[idx] + 0.18, y: 4.34, w: 2.42, h: 0.62,
      fontFace: 'Microsoft YaHei', fontSize: 12, color: C.text, align: 'center', margin: 0.01
    });
  });
  slide.addText('GGUF / cognition 在这里不是技术名词堆砌，而是让历史经验真的参与今天的判断。', {
    x: 0.95, y: 6.18, w: 10.8, h: 0.28,
    fontFace: 'Microsoft YaHei', fontSize: 15, color: C.sub, italic: true, margin: 0
  });
  addFooter(slide, 8);
}

function slide9() {
  const slide = pptx.addSlide();
  addBg(slide);
  addHeaderBand(slide, '如果你也想搭，从这四步开始', 'START SMALL');
  addQuote(slide, '先搭顺序，再追求完整；先能稳定跑，再谈系统丰富。');
  addStepRow(slide, [
    { title: '统一入口', body: '不要让消息直接落正式台账，先有一层路由判断。' },
    { title: '拆开分工', body: '把提醒、今日聚焦、每日总结分开，不要混成一团。' },
    { title: '补执行层', body: '别把所有复杂任务都压在主对话里，给执行留承接层。' },
    { title: '补记忆层', body: '最后再加长期记忆和复盘，让历史能回到今天。' }
  ]);
  addFooter(slide, 9);
}

function closing() {
  const slide = pptx.addSlide();
  addBg(slide, C.navy);
  slide.addText('重点不是让 AI 多回答一次，', {
    x: 1.0, y: 2.0, w: 9.8, h: 0.55,
    fontFace: 'Microsoft YaHei', fontSize: 26, bold: true, color: C.white, margin: 0
  });
  slide.addText('而是让协作少断一次。', {
    x: 1.0, y: 2.75, w: 8.2, h: 0.55,
    fontFace: 'Microsoft YaHei', fontSize: 26, bold: true, color: C.gold, margin: 0
  });
  slide.addText('从消息流到工作流，本质上是在给协作补“承接层”。', {
    x: 1.02, y: 4.0, w: 8.8, h: 0.35,
    fontFace: 'Microsoft YaHei', fontSize: 18, color: 'DCE6FB', italic: true, margin: 0
  });
  slide.addShape(pptx.ShapeType.line, { x: 1.0, y: 4.8, w: 5.0, h: 0, line: { color: '4C638F', pt: 1.3 } });
  slide.addText('THANKS', {
    x: 1.0, y: 5.15, w: 2.4, h: 0.32,
    fontFace: 'Arial', fontSize: 20, bold: true, color: C.accent2, margin: 0
  });
  slide.addText('适合收在“方法可复用、路径可落地”这个感觉上。', {
    x: 1.0, y: 5.56, w: 5.8, h: 0.22,
    fontFace: 'Microsoft YaHei', fontSize: 12, color: 'BFD0EE', margin: 0
  });
}

cover();
slide2();
slide3();
slide4();
slide5();
slide6();
slide7();
slide8();
slide9();
closing();

const out = 'C:/Users/pc/.openclaw/workspace/work-system/deliverables/从消息流到工作流：AI如何把零散协作变成持续推进-v2.pptx';
pptx.writeFile({ fileName: out }).then(() => console.log(out));
