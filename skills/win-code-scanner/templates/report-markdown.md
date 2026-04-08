# {{repo_name}} 代码扫描报告

## 📋 扫描概览

| 项目 | 值 |
|------|----|
| 仓库 | {{repo_name}} |
Git URL | {{git_url}} |
| 分支 | {{git_branch}} |
| 批次进度 | {{batch_progress}} |
| 已扫描文件 | {{scanned_files}} / {{total_files}} ({{progress}}%) |
| 耗时 | {{elapsed}} 秒 |
| Token 消耗 | {{tokens}} |


## 问题统计

| 严重程度 | 数量 |
|----------|------|
| 严重 | {{critical_count}} |
| 警告 | {{warning_count}} |
| **总计** | **{{total_count}}** |


## 完整问题列表

{{#if has_issues}}
{{#each issues_by_rule}}
### {{rule_code}}

**风险等级**: {{risk_level}}

**问题类别**: {{category}}

**影响范围**: {{impact_count}} 处

**涉及文件**:
{{#each files}}
- `{{file_path}}`: 第 {{lines}} 行
{{/each}}

**修复步骤**:
1. 识别并定位所有触发 {{rule_code}} 规则的代码
2. 根据修复建议进行修改（见代码示例）
3. 添加必要的单元测试验证修复

**代码示例**:

✅ **修复建议**:
```
{{suggestion}}
```

**原理说明**: {{description}}

---

{{/each}}
{{else}}
> 扫描进行中，问题列表将逐步更新...
{{/if}}
