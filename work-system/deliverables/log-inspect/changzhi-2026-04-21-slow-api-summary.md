# 长治 2026-04-21 slow_api trace 提取结果

- digest: `D:\现场支持\长治\ms_all_changzhi_9_digest_traces.json`
- log: `D:\现场支持\长治\ms_all.log.2026-04-21.9`
- slow_api trace 数量: **10**
- trace_id 清单: `C:\Users\pc\.openclaw\workspace\work-system\deliverables\log-inspect\changzhi-2026-04-21-slow-api-trace-ids.txt`
- 完整异常链路: `C:\Users\pc\.openclaw\workspace\work-system\deliverables\log-inspect\changzhi-2026-04-21-slow-api-full-chains.log`

## trace 概览

| trace_id | 首次时间 | 末次时间 | 命中日志行 | 续行堆栈 | WARN | ERROR | 主要慢接口 |
|---|---|---:|---:|---:|---:|---:|---|
| 9DE9C8B48F2C424F54BCF30D8136485F | 2026-04-21 10:15:38,123 | 2026-04-21 10:18:12,116 | 28 | 108 | 1 | 1 | 153993ms /api/v1/app_inpatient_encounter/patient_list/query/by_example |
| DB22DCD8E7804F46E594DF32801C3245 | 2026-04-21 10:15:54,132 | 2026-04-21 10:18:12,562 | 34 | 0 | 1 | 0 | 142293ms /api/v1/app_inpatient_encounter/encounter_info/private/get/by_encounter_id |
| 68A3489F3C8F699ED1B1EC9A0483C2EF | 2026-04-21 10:15:50,491 | 2026-04-21 10:18:12,565 | 24 | 0 | 1 | 0 | 142114ms /api/v1/app_inpatient_encounter/banner_person/query/by_id |
| 63D9731F635A67DB2F09ACE35ECB196F | 2026-04-21 10:15:50,441 | 2026-04-21 10:18:12,129 | 6 | 175 | 1 | 2 | 141860ms /api/v1/app_inpatient_encounter/inpat_banner_basics_expense/query/by_id |
| 1a7af34e336b4a51b7f617dbd969a44b | 2026-04-21 10:18:12,555 | 2026-04-21 10:18:12,558 | 3 | 0 | 1 | 0 | 115956ms /api/v1/mobile_nurse_app/inpat_detail/query/by_encounter_id |
| E173051D351FC83F7A570838ACC65CCF | 2026-04-21 10:16:18,072 | 2026-04-21 10:18:12,760 | 53 | 0 | 1 | 0 | 114690ms /api/v1/nis/cli_order_def/query/by_encounter_ids |
| aae98418cae24b07a356b1e56dc4980a | 2026-04-21 10:17:24,819 | 2026-04-21 10:18:12,630 | 33 | 0 | 1 | 0 | 114423ms /api/v1/encounter_inpatient/encounter_info/get/by_id |
| 7f5261ec2c1043fcad8667952ebbce5a | 2026-04-21 10:16:28,747 | 2026-04-21 10:18:12,571 | 50 | 0 | 1 | 0 | 103825ms /api/v1/mobile_nurse_app/specimen_info_list/query/by_example |
| 26d9272c9f2949108b753c98881a94b6 | 2026-04-21 10:16:28,769 | 2026-04-21 10:18:12,546 | 37 | 0 | 1 | 0 | 103778ms /api/v3/mobile_nurse_app/order_specimen_blood_in_band_first/query/by_barcode |
| 84cc9fa305cb43d0a5af4b1c4726c2c3 | 2026-04-21 10:16:28,846 | 2026-04-21 10:18:12,467 | 3 | 0 | 1 | 0 | 103698ms /api/v1/mobile_nurse_app/exe_class_tree/query |

## slow_api 原始条目

- `9DE9C8B48F2C424F54BCF30D8136485F` | timestamp=`2026-04-21 10:18:12,116` | category=`None` | root_class=`None` | api_entry=`None`
- `DB22DCD8E7804F46E594DF32801C3245` | timestamp=`2026-04-21 10:18:12,562` | category=`None` | root_class=`None` | api_entry=`None`
- `68A3489F3C8F699ED1B1EC9A0483C2EF` | timestamp=`2026-04-21 10:18:12,565` | category=`None` | root_class=`None` | api_entry=`None`
- `63D9731F635A67DB2F09ACE35ECB196F` | timestamp=`2026-04-21 10:18:12,129` | category=`None` | root_class=`None` | api_entry=`None`
- `1a7af34e336b4a51b7f617dbd969a44b` | timestamp=`2026-04-21 10:18:12,558` | category=`None` | root_class=`None` | api_entry=`None`
- `E173051D351FC83F7A570838ACC65CCF` | timestamp=`2026-04-21 10:18:12,760` | category=`None` | root_class=`None` | api_entry=`None`
- `aae98418cae24b07a356b1e56dc4980a` | timestamp=`2026-04-21 10:18:12,630` | category=`None` | root_class=`None` | api_entry=`None`
- `7f5261ec2c1043fcad8667952ebbce5a` | timestamp=`2026-04-21 10:18:12,571` | category=`None` | root_class=`None` | api_entry=`None`
- `26d9272c9f2949108b753c98881a94b6` | timestamp=`2026-04-21 10:18:12,546` | category=`None` | root_class=`None` | api_entry=`None`
- `84cc9fa305cb43d0a5af4b1c4726c2c3` | timestamp=`2026-04-21 10:18:12,467` | category=`None` | root_class=`None` | api_entry=`None`

## 说明

- 完整异常链路的提取规则为：保留所有包含目标 `trace_id` 的日志行，并自动续接其后不带新日志头的异常堆栈行。
- 若某条 trace 主要体现为慢链路而非抛异常，可能只有 trace 自身日志与耗时日志，没有额外 Java 堆栈续行。
