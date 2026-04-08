#!/usr/bin/env python3
"""
分批并发扫描实现
用于处理大量文件的代码扫描，避免 token 超限

支持按规则分组的增量报告格式：
- 每批次扫描完成后，命中同规则的问题文件累加到"涉及文件"列表
- 报告格式参照 demo-markdown.md
- 报告命名规则：{仓库名称}_{时间}.{扩展名}

使用方式:
    from scripts.batch_scan import BatchScanner
    import datetime

    repo_name = "winning-dtc-Knowledge"
    git_url = "http://tfs2018-web.winning.com.cn:8080/tfs/WINNING-6.0/WiNEX_WXP/_git/winning-dtc-Knowledge"
    git_branch = "4.0.0-SNAPSHOT"
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    report_path = f"/tmp/{repo_name}_{timestamp}.md"

    scanner = BatchScanner(
        files=files_list,
        batch_size=100,
        max_concurrent=3,
        report_path=report_path,
        repo_name=repo_name,
        git_url=git_url,
        git_branch=git_branch
    )
    results = scanner.scan()
"""

from typing import List, Dict, Callable, Any, Set, Optional
from collections import defaultdict
import time
import json
import os
import datetime


class BatchScanner:
    """分批扫描器 - 支持按规则分组的增量报告"""

    def __init__(
        self,
        files: List[str],
        batch_size: int = 100,
        max_concurrent: int = 3,
        report_path: str = "/tmp/scan-report.md",
        max_retries: int = 3,
        repo_name: str = "code-scan",
        git_url: str = "",
        git_branch: str = ""
        ):
        """
        初始化分批扫描器

        Args:
            files: 待扫描的文件列表
            batch_size: 每批处理的文件数（默认100）
            max_concurrent: 批次内最大并发数（严格控制不超过3）
            report_path: 报告文件路径
            max_retries: 批次失败时最大重试次数（默认3）
            repo_name: 仓库名称（用于报告标题和文件名）
            git_url: Git 仓库地址（必含）
            git_branch: Git 扫描分支（必含）
        """
        self.files = files
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
        self.report_path = report_path
        self.repo_name = repo_name
        self.git_url = git_url
        self.git_branch = git_branch
        self.total_batches = (len(files) + batch_size - 1) // batch_size
        self.all_issues = []
        self.failed_batches = {}  # 追踪失败的批次 {batch_idx: (reason, retry_count)}
        self.completed_batches = []  # 已成功完成的批次

        # 按规则分组的问题统计 {rule_code: {file: {lines: Set[int], description: str, suggestion: str}}}
        self.issues_by_rule = defaultdict(lambda: defaultdict(lambda: {
            'lines': set(),
            'description': '',
            'suggestion': '',
            'severity': '',
            'category': ''
        }))

        # 规则元信息 {rule_code: {name: str, severity: str, category: str}}
        self.rule_metadata = {}

        # 统计信息
        self.start_time = None
        self.total_tokens = 0
        self.scanned_files_count = 0

    def _get_risk_level(self, severity: str) -> str:
        """根据严重程度返回风险等级"""
        severity_map = {
            '严重': '🔴 high',
            '警告': '🟡 medium'
        }
        return severity_map.get(severity, '🟡 medium')

    def _init_report_header(self):
        """初始化报告头部"""
        header = f"""# {self.repo_name} 代码扫描报告

## 📋 扫描概览

| 项目 | 值 |
|------|----|
| 仓库 | {self.repo_name} |
Git URL | {self.git_url} |
| 分支 | {self.git_branch} |
| 批次进度 | 0/{self.total_batches} 批 |
| 已扫描文件 | 0 / {len(self.files)} (0%) |
| 耗时 | 0 秒 |
| Token 消耗 | 0 |


## 问题统计

| 严重程度 | 数量 |
|----------|------|
| 严重 | 0 |
| 警告 | 0 |
| **总计** | **0** |


## 完整问题列表

> 扫描进行中，问题列表将逐步更新...

---

"""
        with open(self.report_path, 'w', encoding='utf-8') as f:
            f.write(header)

    def _update_scan_overview(self):
        """更新扫描概览部分"""
        if not self.start_time:
            self.start_time = time.time()

        elapsed = int(time.time() - self.start_time) if self.start_time else 0
        progress = (self.scanned_files_count / len(self.files) * 100) if self.files else 0

        overview = f"""## 📋 扫描概览

| 项目 | 值 |
|------|----|
| 仓库 | {self.repo_name} |
Git URL | {self.git_url} |
| 分支 | {self.git_branch} |
| 批次进度 | {len(self.completed_batches)}/{self.total_batches} 批 |
| 已扫描文件 | {self.scanned_files_count} / {len(self.files)} ({progress:.1f}%) |
| 耗时 | {elapsed} 秒 |
| Token 消耗 | {self.total_tokens:,} |

"""
        return overview

    def _update_issue_statistics(self):
        """更新问题统计部分"""
        critical = sum(1 for meta in self.rule_metadata.values() if meta.get('severity') == '严重')
        warning = sum(1 for meta in self.rule_metadata.values() if meta.get('severity') == '警告')
        total = len(self.rule_metadata)

        stats = f"""## 问题统计

| 严重程度 | 数量 |
|----------|------|
| 严重 | {critical} |
| 警告 | {warning} |
| **总计** | **{total}** |


"""
        return stats

    def _format_rule_section(self, rule_code: str) -> str:
        """格式化单个规则的问题条目"""
        meta = self.rule_metadata.get(rule_code, {})
        name = meta.get('name', rule_code)
        severity = meta.get('severity', '警告')
        category = meta.get('category', '未知')

        # 统计影响范围（所有行号的总数，而非文件数）
        files_data = self.issues_by_rule.get(rule_code, {})
        total_lines = sum(len(data['lines']) for data in files_data.values())

        # 构建涉及文件列表
        files_list = []
        for file_path, data in sorted(files_data.items()):
            lines = sorted(data['lines'])
            if lines:
                # 将连续的行号合并显示 (如: 第 10-15, 20, 25-30 行)
                line_groups = []
                start = lines[0]
                prev = lines[0]

                for line in lines[1:]:
                    if line == prev + 1:
                        prev = line
                    else:
                        if start == prev:
                            line_groups.append(str(start))
                        else:
                            line_groups.append(f"{start}-{prev}")
                        start = prev = line

                if start == prev:
                    line_groups.append(str(start))
                else:
                    line_groups.append(f"{start}-{prev}")

                lines_str = ', '.join(line_groups)
                files_list.append(f"- `{file_path}`: 第 {lines_str} 行")

        files_section = '\n'.join(files_list) if files_list else '- 暂无'

        # 获取问题描述和修复建议
        first_file = next(iter(files_data.values()), {}) if files_data else {}
        description = first_file.get('description', meta.get('description', ''))
        suggestion = first_file.get('suggestion', meta.get('suggestion', ''))

        section = f"""### {rule_code}

**风险等级**: {self._get_risk_level(severity)}

**问题类别**: {category}

**影响范围**: {total_lines} 处

**涉及文件**:
{files_section}

**修复步骤**:
1. 识别并定位所有触发 {rule_code} 规则的代码
2. 根据修复建议进行修改（见代码示例）
3. 添加必要的单元测试验证修复

**代码示例**:

✅ **修复建议**:
```
{suggestion if suggestion else description}
```

**原理说明**: {description}

---

"""
        return section

    def _format_issues_list(self):
        """格式化完整问题列表"""
        if not self.rule_metadata:
            return "> 扫描进行中，问题列表将逐步更新...\n\n"

        # 按严重程度排序: 严重 > 警告
        severity_order = {'严重': 0, '警告': 1}
        sorted_rules = sorted(
            self.rule_metadata.keys(),
            key=lambda r: severity_order.get(self.rule_metadata[r].get('severity', '警告'), 2)
        )

        sections = []
        for rule_code in sorted_rules:
            sections.append(self._format_rule_section(rule_code))

        return '\n'.join(sections)

    def _merge_batch_issues(self, batch_issues: List[Dict]):
        """
        合并批次扫描结果到按规则分组的数据结构

        每批次扫描完成后，命中同规则的问题文件累加到"涉及文件"列表
        """
        for issue in batch_issues:
            rule_code = issue.get('rule_code', '')
            file_path = issue.get('file', '')
            line = issue.get('line', 0)
            description = issue.get('description', '')
            suggestion = issue.get('suggestion', '')
            severity = issue.get('severity', '警告')
            category = issue.get('category', '未知')
            rule_name = issue.get('rule_name', '')

            if not rule_code or not file_path:
                continue

            # 更新规则元信息
            if rule_code not in self.rule_metadata:
                self.rule_metadata[rule_code] = {
                    'name': rule_name,
                    'severity': severity,
                    'category': category,
                    'description': description,
                    'suggestion': suggestion
                }

            # 累加文件行号
            self.issues_by_rule[rule_code][file_path]['lines'].add(line)

            # 更新描述和建议（使用第一个非空的）
            if description and not self.issues_by_rule[rule_code][file_path]['description']:
                self.issues_by_rule[rule_code][file_path]['description'] = description
            if suggestion and not self.issues_by_rule[rule_code][file_path]['suggestion']:
                self.issues_by_rule[rule_code][file_path]['suggestion'] = suggestion
            if not self.issues_by_rule[rule_code][file_path]['severity']:
                self.issues_by_rule[rule_code][file_path]['severity'] = severity
            if not self.issues_by_rule[rule_code][file_path]['category']:
                self.issues_by_rule[rule_code][file_path]['category'] = category

    def update_report_incremental(
        self,
        batch_idx: int,
        batch_files: List[str],
        batch_issues: List[Dict],
        is_retry: bool = False,
        retry_count: int = 0
    ):
        """
        增量更新报告文件（按规则分组格式）

        每批次完成后立即调用，命中同规则的问题文件累加到"涉及文件"列表
        """
        # 过滤有效问题并合并
        valid_issues = [i for i in batch_issues if not i.get('is_failure', False)]
        self._merge_batch_issues(valid_issues)
        self.scanned_files_count += len(batch_files)

        # 重建整个报告文件
        overview = self._update_scan_overview()
        stats = self._update_issue_statistics()
        issues_list = self._format_issues_list()

        report_content = f"""# {self.repo_name} 代码扫描报告

{overview}
{stats}
## 完整问题列表

{issues_list}
"""

        with open(self.report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        # 返回统计信息
        critical = sum(1 for meta in self.rule_metadata.values() if meta.get('severity') == '严重')
        warning = sum(1 for meta in self.rule_metadata.values() if meta.get('severity') == '警告')

        return {
            'total': len(self.rule_metadata),
            'critical': critical,
            'warning': warning
        }

    def scan(
        self,
        scan_func: Callable[[List[str]], List[Dict]],
        ask_user_func: Callable[[int, int], str] = None
    ) -> List[Dict]:
        """
        执行分批扫描（支持失败重试）

        Args:
            scan_func: 扫描函数，接收文件列表，返回问题列表
            ask_user_func: 用户询问函数，接收(当前批次,总批次)，返回用户选择

        Returns:
            所有批次的问题列表（包含重试成功的批次）
        """
        # 初始化报告
        self._init_report_header()
        self.start_time = time.time()

        for batch_idx in range(self.total_batches):
            # 获取当前批次的文件
            start_idx = batch_idx * self.batch_size
            end_idx = min(start_idx + self.batch_size, len(self.files))
            batch_files = self.files[start_idx:end_idx]

            # 检查是否是重试批次
            is_retry = batch_idx in self.failed_batches

            # 尝试扫描当前批次（支持重试）
            batch_issues = None
            retry_count = 0
            last_error = None

            while retry_count < self.max_retries:
                try:
                    # 执行扫描
                    batch_issues = scan_func(batch_files)
                    # 扫描成功，跳出重试循环
                    break

                except Exception as e:
                    retry_count += 1
                    last_error = str(e)
                    print(f"✗ 第 {batch_idx + 1} 批扫描失败（第 {retry_count} 次重试）: {e}")

                    # 如果达到最大重试次数，记录失败信息
                    if retry_count >= self.max_retries:
                        self.failed_batches[batch_idx] = {
                            'reason': last_error or '未知错误',
                            'retry_count': retry_count,
                            'status': 'failed'
                        }
                        print(f"✗ 第 {batch_idx + 1} 批已标记为失败，重试 {retry_count} 次后仍失败")

            if batch_issues is not None and len([i for i in batch_issues if not i.get('is_failure', False)]) >= 0:
                # 扫描成功：增量更新报告（按规则分组）
                valid_issues = [i for i in batch_issues if not i.get('is_failure', False)]
                self.all_issues.extend(valid_issues)
                self.completed_batches.append(batch_idx)

                # 增量更新报告
                stats = self.update_report_incremental(
                    batch_idx=batch_idx,
                    batch_files=batch_files,
                    batch_issues=valid_issues,
                    is_retry=is_retry,
                    retry_count=retry_count if is_retry else 0
                )

                print(f"✓ 第 {batch_idx + 1}/{self.total_batches} 批完成 - "
                      f"已扫描 {self.scanned_files_count} 个文件，"
                      f"发现 {stats['total']} 个规则问题（严重:{stats['critical']} 警告:{stats['warning']}）")

            else:
                # 批次彻底失败
                print(f"⚠️ 第 {batch_idx + 1} 批彻底失败，跳过此批次")
                # 仍然更新进度
                self.scanned_files_count += len(batch_files)

            # 询问用户是否继续下一批
            if batch_idx < self.total_batches - 1 and ask_user_func:
                user_choice = ask_user_func(batch_idx + 1, self.total_batches)
                if user_choice == "stop":
                    print(f"用户提前终止扫描，已完成 {len(self.completed_batches)}/{self.total_batches} 批")
                    break
                elif user_choice == "skip_failed":
                    continue

        return self.all_issues


def format_progress(
    batch_idx: int,
    total_batches: int,
    total_files: int,
    scanned_files: int,
    issues_count: int
) -> str:
    """
    格式化进度显示

    Returns:
        格式化的进度字符串
    """
    batch_progress = (batch_idx + 1) / total_batches * 100
    file_progress = scanned_files / total_files * 100

    return f"""
正在扫描 [分批模式]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

批次进度: {'%' * int(batch_progress // 5)}{' ' * (20 - int(batch_progress // 5))} {batch_idx + 1}/{total_batches} 批 ({batch_progress:.0f}%)
文件进度: {'%' * int(file_progress // 5)}{' ' * (20 - int(file_progress // 5))} {scanned_files}/{total_files} ({file_progress:.0f}%)
发现问题: {issues_count} 个规则

预估剩余: {total_batches - batch_idx - 1} 批
"""


def generate_report_path(repo_name: str, output_dir: str = "/tmp") -> tuple:
    """
    生成报告文件路径

    Args:
        repo_name: 仓库名称
        output_dir: 输出目录（默认 /tmp）

    Returns:
        (report_path_md, report_path_xlsx)
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    report_path_md = os.path.join(output_dir, f"{repo_name}_{timestamp}.md")
    report_path_xlsx = os.path.join(output_dir, f"{repo_name}_{timestamp}.xlsx")
    return report_path_md, report_path_xlsx


if __name__ == "__main__":
    # 示例用法
    import sys

    if len(sys.argv) < 2:
        print("用法: python batch_scan.py <文件数> [仓库名]")
        sys.exit(1)

    total_files = int(sys.argv[1])
    repo_name = sys.argv[2] if len(sys.argv) > 2 else "code-scan"
    batch_size = 100
    total_batches = (total_files + batch_size - 1) // batch_size

    print(f"""
分批扫描配置（按规则分组报告格式）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总文件数: {total_files}
批次大小: {batch_size}
总批次数: {total_batches} 批
报告格式: 按规则分组，支持增量更新
报告命名: {repo_name}_YYYYMMDDHHmm.md

预计耗时: 约 {total_batches * 2}-{total_batches * 3} 分钟
""")
