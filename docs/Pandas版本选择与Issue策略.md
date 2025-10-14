## Pandas 历史版本选型与 Issue 回溯策略

### 被测版本
- pandas 1.0.3（目标被测版本）

### 回溯来源版本
- pandas 1.0.4、1.0.5 的 Fixed regressions / Bug fixes
- 补充：对应里程碑（milestone）下的已关闭 Issue/PR 列表，用以补齐 What’s New 未收录但确属该版本修复的条目

### 选型理由（为什么选择 1.0.3）
- 同线回溯严谨：1.0.3 → 1.0.4/1.0.5 多为回归/缺陷修复，语义稳定，便于严格证明“1.0.3 未包含修复、1.0.4/1.0.5 已包含修复”。
- 溯源链清晰：What’s New 中的 GH 编号可反查到具体 Issue/PR 与里程碑；结合 1.0.4/1.0.5 里程碑关闭项，足以筛选并核验 25 条问题。
- 能力对齐：补丁版修复多为具体代码问题（命名/异常/边界/类型/安全/复杂度等），便于映射到当前“静态检测/AI分析/动态类”的能力矩阵，并评估“可检测/可自动修复/需人工”。
- 降噪：避免跨到 1.1.0（功能增强/行为调整较多）或跨大版本（0.25.x→1.0.0）的 API/语义变化，把“设计变更”与“真实缺陷”混杂的风险降到最低。

### 结论与交付
- 交付一份包含 25 条条目的清单（5 简单 / 15 中等 / 5 困难）：
  - 每条均附 GitHub 链接（Issue 或 PR）、修复所含版本、是否回溯到更早分支的说明；
  - 标注与本系统能力的关系：是否可静态检测、是否 AI 可辅助、是否可自动修复、是否需要动态/运行时。
- 附带复现与验证指引：如何在 1.0.3 复现、如何用系统跑检测并与清单对齐。

### 候选问题清单（25 条，基于 1.0.4/1.0.5 What’s New 与对应 GH）

说明：以下条目均在 pandas 1.0.4/1.0.5 的 What’s New 中列出（Fixed regressions / Bug fixes），据此可回溯它们在 1.0.3 中未包含修复提交。链接统一指向 GitHub `issues/<id>`（PR 在 GitHub 也属 Issue 类型，可同链路访问）。

难度/可检测性标注：
- E=易，M=中，H=难；S=静态可检，A=AI辅助，D=需动态/运行时

1. GH33594（E/A）【子域：missing/categorical】1.0.4 修复：`Series.isna()/DataFrame.isna()` 在 `use_inf_as_na=True` 与 categorical 下异常
   - https://github.com/pandas-dev/pandas/issues/33594
2. GH32800（M/A）【子域：groupby/first-last】1.0.4 修复：`GroupBy.first/last` 未保留 object dtype 中的 None
   - https://github.com/pandas-dev/pandas/issues/32800
3. GH33256（M/A）【子域：reduction/EA】1.0.4 修复：`numeric_only=True` 与 ExtensionArrays 的 DataFrame 缩减回归
   - https://github.com/pandas-dev/pandas/issues/33256
4. GH33012（H/D）【子域：perf/memory】1.0.4 修复：`memory_usage(deep=True)` 在 object dtype 上性能回归
   - https://github.com/pandas-dev/pandas/issues/33012
5. GH33288（E/S）【子域：categorical/replace】1.0.4 修复：`Categorical.replace()` 当新值与替换值相等时错误置为 NaN
   - https://github.com/pandas-dev/pandas/issues/33288
6. GH33450（M/A）【子域：categorical/min-max】1.0.4 修复：仅含 NaN 的有序 Categorical 取 min/max 异常
   - https://github.com/pandas-dev/pandas/issues/33450
7. GH32194（M/A）【子域：groupby/agg + EA】1.0.4 修复：`DataFrameGroupBy.agg()` 字典输入丢失 EA dtypes
   - https://github.com/pandas-dev/pandas/issues/32194
8. GH32905（M/A）【子域：index/cftime/nearest】1.0.4 修复：与 xarray `CFTimeIndex` 最近索引兼容性
   - https://github.com/pandas-dev/pandas/issues/32905
9. GH32409（E/S）【子域：describe/type】1.0.4 修复：`DataFrame.describe()` TypeError: unhashable type: 'dict'
   - https://github.com/pandas-dev/pandas/issues/32409
10. GH32988（E/S）【子域：frame/replace-cast】1.0.4 修复：`DataFrame.replace()` 当替换项不在 values 中时列被错误 cast 为 object
    - https://github.com/pandas-dev/pandas/issues/32988
11. GH34010（M/A）【子域：groupby/periodindex】1.0.4 修复：`Series.groupby()` 在 `PeriodIndex` level 上 ValueError
    - https://github.com/pandas-dev/pandas/issues/34010
12. GH33433（M/A）【子域：groupby/rolling.apply】1.0.4 修复：`GroupBy.rolling.apply()` 忽略 `args/kwargs`
    - https://github.com/pandas-dev/pandas/issues/33433
13. GH33115（M/A）【子域：categorical/error-msg】1.0.4 修复：无序 Categorical 上 `np.min/np.max` 报错信息回归
    - https://github.com/pandas-dev/pandas/issues/33115
14. GH32395（M/A）【子域：index/tz-aware/loc】1.0.4 修复：`DataFrame.loc()/Series.loc()` 对 tz-aware datetime 值报错
    - https://github.com/pandas-dev/pandas/issues/32395
15. GH33071（M/A）【子域：groupby/nullable-bool】1.0.4 修复：`SeriesGroupBy.first/last/min/max` 在 nullable booleans 上返回 float
    - https://github.com/pandas-dev/pandas/issues/33071
16. GH30726（H/D）【子域：rolling/memory-leak】1.0.4 修复：`Rolling.min()/max()` 固定窗口多次调用内存增长
    - https://github.com/pandas-dev/pandas/issues/30726
17. GH27679（M/A）【子域：io/parquet/s3-write/permission】1.0.4 修复：`to_parquet()` 向私有 s3 写入无效凭据未正确抛 PermissionError
    - https://github.com/pandas-dev/pandas/issues/27679
18. GH32486（E/S）【子域：io/csv/s3】1.0.4 修复：`to_csv()` 写入无效 s3 bucket 静默失败
    - https://github.com/pandas-dev/pandas/issues/32486
19. GH26388（M/A）【子域：io/parquet/s3-read/dir】1.0.4 修复：`read_parquet()` 传入 s3 目录路径抛 FileNotFoundError
    - https://github.com/pandas-dev/pandas/issues/26388
20. GH27596（M/A）【子域：io/parquet/s3-partition-write】1.0.4 修复：`to_parquet()` 写分区 parquet 到 s3 抛 AttributeError
    - https://github.com/pandas-dev/pandas/issues/27596
21. GH33200（H/D）【子域：groupby/quantile-shift】1.0.4 修复：`GroupBy.quantile()` 在 by 轴含 NaN 时分位数偏移
    - https://github.com/pandas-dev/pandas/issues/33200
22. GH33569（H/D）【子域：groupby/quantile-shift】1.0.4 修复：同一场景（GroupBy 分位数偏移）的关联问题，在不同触发条件下导致结果偏移
    - https://github.com/pandas-dev/pandas/issues/33569
23. GH34467（H/D）【子域：io/parquet/file-like】1.0.5 修复：`read_parquet()` 读取 file-like 对象回归
    - https://github.com/pandas-dev/pandas/issues/34467
24. GH34626（M/A）【子域：io/s3/public-read】1.0.5 修复：读取公共 S3 bucket 回归
    - https://github.com/pandas-dev/pandas/issues/34626
25. GH34530（M/A）【子域：EA/replace/cross-dtype】1.0.5 修复：`replace()` 在 EA 上跨 dtype 替换时 AssertionError
    - https://github.com/pandas-dev/pandas/issues/34530

### 子域标签说明
- groupby/first-last：分组后的首/尾聚合行为
- groupby/quantile-shift：分组分位数计算在含 NaN/特定 by 条件下的结果偏移
- groupby/rolling.apply：分组滚动窗口 `apply` 的参数传递与执行
- categorical/replace：分类类型替换逻辑
- categorical/min-max：分类类型的极值计算
- reduction/EA：含扩展数组（EA）的聚合/缩减
- EA/replace/cross-dtype：EA 上跨 dtype 的替换与类型一致性
- io/parquet/s3-read/dir：Parquet 从 S3 目录读取
- io/parquet/s3-write/permission：Parquet 写 S3 权限/凭据处理
- io/parquet/s3-partition-write：Parquet 分区写入到 S3
- io/parquet/file-like：Parquet 从类文件对象读取
- io/csv/s3：CSV 与 S3 交互
- index/tz-aware/loc：带时区索引在 `loc` 下的行为
- index/cftime/nearest：CFTimeIndex 最近匹配
- describe/type：`DataFrame.describe` 的类型处理
- perf/memory：内存统计/性能回归
简单/中等/困难分类（5/15/5）：
- 简单（5）：#33594、#33288、#32409、#32988、#32486
- 中等（15）：#32800、#33256、#33450、#32194、#32905、#34010、#33433、#32395、#33071、#27679、#26388、#27596、#34626、#34530、#33115（可在后续核验中微调）
- 困难（5）：#30726、#33200、#33569、#33012、#34467

能力映射（概览）：
- S（静态可检，且多可自动修复）：#33288、#32409、#32988、#33115、#32486
- A（AI辅助判定/建议修复）：大多数行为/边界/类型一致性问题，如 #32800、#33256、#33012、#33450、#32194、#34010、#33433、#32395、#33071、#27679、#26388、#27596、#34467、#34626、#34530
- D（需动态/运行时验证）：窗口/分组统计类时序/内存/分位偏移等，如 #30726、#33200、#33569

注：后续将对每条进行“是否 backport、包含于哪些标签、在 1.0.3 的可复现性”逐条核验与补充说明。

### 复现与验证指引（草案）
1) 使用 `git` 检出 v1.0.3 与 v1.0.4/v1.0.5 标签，最小化复现对应 API 调用；
2) 在 v1.0.3 运行：观察异常/错误行为；在 v1.0.4/1.0.5 运行：验证修复；
3) 在本系统中：
   - 首测文件级：针对触发点最集中的文件（如 groupby/rolling/parquet I/O 等模块）上传分析；
   - 再测目录级：`pandas/core/`；
   - 产出报告后，用 `compare_pandas_bugs.py` 与本清单交叉对齐。

### 方法（执行步骤）
1) 从 1.0.4/1.0.5 的 What’s New 中提取“Fixed regressions/Bug fixes”的 GH 编号；
2) 反查到对应 GitHub Issue/PR 页面，确认里程碑与合入分支；
3) 在 1.0.4/1.0.5 的里程碑下补充抓取关闭的 Issue/PR，补足 What’s New 未列出的修复；
4) 核验是否 backport 到更早补丁；最终判定“1.0.3 是否未包含该修复提交”；
5) 筛选并分类为 5/15/5，并完成能力映射与修复可行性标注。

### 参考
- pandas 1.0.0 What’s New（含版本策略、GH 引用写法）
  - `https://pandas.pydata.org/pandas-docs/version/1.0.0/whatsnew/v1.0.0.html`


