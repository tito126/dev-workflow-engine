# 晋城 2026-04-15 slow_api trace 提取结果

- digest: `D:\现场支持\晋城\ms_all_digest.json.2026-04-15_traces.json`
- log: `D:\现场支持\晋城\ms_all.log.2026-04-15.54`
- slow_api trace 数量: **10**
- trace_id 清单: `C:\Users\pc\.openclaw\workspace\work-system\deliverables\log-inspect\jincheng-2026-04-15-slow-api-trace-ids.txt`
- 完整异常链路: `C:\Users\pc\.openclaw\workspace\work-system\deliverables\log-inspect\jincheng-2026-04-15-slow-api-full-chains.log`

## trace 概览

| trace_id | 首次时间 | 末次时间 | 命中日志行 | 续行堆栈 | WARN | ERROR | 主要慢接口 |
|---|---|---:|---:|---:|---:|---:|---|
| 0fb18dbda0ce42d081f1462d9083f9cc | 2026-04-15 10:22:12,850 | 2026-04-15 10:31:03,617 | 117 | 108 | 1 | 1 | 530768ms /api/v1/app_inpatient_encounter/patient_list/query/by_example |
| b54e0bf4c468483a82c72bf5153a34b1 | 2026-04-15 10:22:18,691 | 2026-04-15 10:31:04,668 | 485 | 516 | 1 | 2 | 525587ms /api/v1/nis/exec_order/check/by_exec_order_ids |
| 0f3cee3422a64ae6beeae9745fbbb3db | 2026-04-15 10:22:52,379 | 2026-04-15 10:31:06,364 | 565 | 131 | 2 | 1 | 493986ms /api/v1/nis/exec_order_plan/advance_apply/by_end_time |
| 60b7face4ef54be1903c29c89c9de5a6 | 2026-04-15 10:22:52,291 | 2026-04-15 10:28:41,844 | 8 | 0 | 1 | 0 | 375564ms /api/v1/mobile_nurse_app/exe_class_tree/query |
| 1fb099b5fcd645cd9fe35c533f78f38a | 2026-04-15 10:22:26,276 | 2026-04-15 10:28:40,970 | 41 | 256 | 1 | 2 | 374701ms /api/v1/app_inpatient_encounter/encounter_info/private/get/by_encounter_id |
| 57af47aa45a54692b72e1e6695f7b75b | 2026-04-15 10:22:52,598 | 2026-04-15 10:28:40,746 | 50 | 0 | 1 | 0 | 374486ms /api/v1/app_inpatient_encounter/inpat_banner_basics_expense/query/by_id |
| e2564e6b0b604cec984f101b5906c95a | 2026-04-15 10:22:52,379 | 2026-04-15 10:28:41,950 | 62 | 0 | 1 | 1 | 349572ms /api/v2/app_inpatient_encounter/encounter_bed_detail/query/by_id |
| 552483a4795f4a2eb9df1a2bd3038ba5 | 2026-04-15 10:23:43,113 | 2026-04-15 10:28:40,768 | 34 | 41 | 1 | 1 | 347488ms /api/v1/app_inpatient_encounter/inpat_basics_expense/query/by_encounter_id |
| 2102c74bf6b14211b0034fc7551a98de | 2026-04-15 10:22:18,694 | 2026-04-15 10:28:00,493 | 35 | 0 | 1 | 0 | 341808ms /api/v1/app_encounter_inpatient/new_inpat_bed_print/query/by_example |
| 61684b4b88874daeae7429c81a6de7ee | 2026-04-15 10:22:25,995 | 2026-04-15 10:28:05,850 | 148 | 0 | 1 | 0 | 339854ms /api/v2/nis/cli_order_doc/query/by_encounter_ids |

## slow_api 原始条目

- `0fb18dbda0ce42d081f1462d9083f9cc` | timestamp=`2026-04-15 10:31:03,617` | category=`None` | root_class=`None` | api_entry=`None`
- `b54e0bf4c468483a82c72bf5153a34b1` | timestamp=`2026-04-15 10:31:04,278` | category=`None` | root_class=`None` | api_entry=`None`
- `0f3cee3422a64ae6beeae9745fbbb3db` | timestamp=`2026-04-15 10:31:06,364` | category=`None` | root_class=`None` | api_entry=`None`
- `60b7face4ef54be1903c29c89c9de5a6` | timestamp=`2026-04-15 10:28:41,843` | category=`None` | root_class=`None` | api_entry=`None`
- `1fb099b5fcd645cd9fe35c533f78f38a` | timestamp=`2026-04-15 10:28:40,968` | category=`None` | root_class=`None` | api_entry=`None`
- `57af47aa45a54692b72e1e6695f7b75b` | timestamp=`2026-04-15 10:28:40,745` | category=`None` | root_class=`None` | api_entry=`None`
- `e2564e6b0b604cec984f101b5906c95a` | timestamp=`2026-04-15 10:28:41,950` | category=`None` | root_class=`None` | api_entry=`None`
- `552483a4795f4a2eb9df1a2bd3038ba5` | timestamp=`2026-04-15 10:28:40,767` | category=`None` | root_class=`None` | api_entry=`None`
- `2102c74bf6b14211b0034fc7551a98de` | timestamp=`2026-04-15 10:28:00,493` | category=`None` | root_class=`None` | api_entry=`None`
- `61684b4b88874daeae7429c81a6de7ee` | timestamp=`2026-04-15 10:28:05,848` | category=`None` | root_class=`None` | api_entry=`None`

## 说明

- 完整异常链路的提取规则为：保留所有包含目标 `trace_id` 的日志行，并自动续接其后不带新日志头的异常堆栈行。
- 若某条 trace 主要体现为慢链路而非抛异常，可能只有 trace 自身日志与耗时日志，没有额外 Java 堆栈续行。
