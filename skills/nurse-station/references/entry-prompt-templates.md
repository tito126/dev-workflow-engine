# entry-prompt-templates — 标准 prompt

## 14.1 通用标准版（自用 / 同事通用）

```text
需求号：XXX

先用 `tfs2018-integration` 拉取需求信息，
然后进入 `nurse-station` 主流程处理。

要求：
1. 先读取并校验 `nurse-station-repo-routing.yaml`
2. 先扫描当前需求下已有任务，并结合目标 repo 选出本轮任务号；没有合适任务就先停下来提示
3. 输出本轮路由与代码基线摘要，至少包含：
   - 任务号
   - 目标 repo key
   - 实际扫描根 / 本地修改目录
   - 基线分支
   - 当前 commit
   - 任务分支 `feature/{taskId}`
4. 如果需求边界还不清，不要直接改码，先输出需求澄清 / 设计摘要供我确认
5. 只有在 YAML、任务号、代码基线、需求边界都明确后，才进入 locator / implementer
6. 实现后默认用 `acceptance.md` 收口，明确区分“代码完成 / 需求完成 / 效果已验证”
7. 如果本轮产生新规则、返工原因或流程缺口，把候选模式补到 `work-system/frameworks/nurse-station/pattern-ledger.md`
8. 所有任务级产物按 `work-system/deliverables/nurse-station/{taskId}-{date}/` 落地
```

## 14.2 先出设计文档版

```text
需求号：XXX

先用 `tfs2018-integration` 拉取需求信息，
然后进入 `nurse-station` 主流程处理。

这次先不要直接改码。

要求：
1. 先读取并校验 `nurse-station-repo-routing.yaml`
2. 先扫描当前需求下已有任务，并结合目标 repo 选出本轮任务号；没有合适任务就先停下来提示
3. 输出本轮路由与代码基线摘要
4. 先产出需求澄清 / 设计摘要，明确范围内、范围外、成功锚点和待确认问题
5. 等我确认后，再进入 locator / implementer
6. 后续实现完成时，默认输出 `acceptance.md`，不要把 verification / review-gate 拆成默认双文件
```

## 14.3 适合转发给同事的简化版

```text
需求号：XXX

先用 `tfs2018-integration` 获取需求，
再走 `nurse-station` 主流程。

先给我：
- 本轮选中的任务号
- 目标 repo key
- 实际扫描根 / 本地修改目录
- 基线分支和最新 commit
- 任务分支 `feature/{taskId}`
- 需求澄清结论

如果需求还不清，先出设计摘要，不要直接改代码。
确认后再继续开发。

实现完成后，默认给出：
- `implementation-result.md`
- `acceptance.md`

如果出现返工、新规则或流程缺口，再决定是否补 `retrospective.md`。
```

## 14.4 试跑期收口版（推荐本轮优化后优先使用）

```text
需求号：XXX

先用 `tfs2018-integration` 获取需求，
再走 `nurse-station` 主流程。

这次按“试跑 acceptance + 中央 pattern-ledger”执行。

要求：
1. 先读取并校验 `nurse-station-repo-routing.yaml`
2. 先确定本轮任务号、repo key、基线分支、本地修改目录，并输出路由摘要
3. 需求不清时先停在 brainstorming / planning，不直接改码
4. 实现完成后，默认输出 `acceptance.md`，明确：
   - 代码完成
   - 需求完成
   - 效果已验证
   - retro signals
5. 如果本轮出现返工、新规则、流程缺口、路由误判或手工补锅，把候选模式追加到中央 `pattern-ledger.md`
6. 只有在高风险或结论存在争议时，才额外进入 `review-gate.md`
7. 只有在出现结构性新信息时，才额外进入 `retrospective.md`
```
