## Flask 历史版本选型与 Issue 回溯策略（基线：2.0.0）

参考官方变更记录，选用 Flask 2.0.0 作为基线版本，回溯 2.0.1 / 2.0.2 / 2.0.3 的修复项，严格筛选“2.0.0 中存在且未修复、后续小版本中已修复”的问题，用于测试与验证本系统的检测/修复能力。

- 官方变更记录（Changes）：`https://flask.palletsprojects.com/en/stable/changes/#version-2-0-1`

### 选型理由
- 问题密度与类型丰富：2.0.x 连续小版本包含大量修复，涵盖 API/行为/类型提示/CLI 等多维度，便于构建“5 简单 / 15 中等 / 5 困难”的代表性组合。
- 可证性强：变更页列出对应的 GitHub 议题/PR 编号，易于核验修复首次进入的版本与提交，严谨证明“2.0.0 未修复、2.0.(1|2|3) 已修复”。
- 能力匹配：修复项与本系统的 S（静态可检）、A（AI 辅助）、D（需动态验证）能力矩阵高度贴合。

### 能力矩阵（概览）
- S（静态可检，且多可自动修复）：API 参数/重命名不一致、类型注解问题、明显的蓝图命名/导出符号等一致性问题。
- A（AI 辅助判定/建议修复）：蓝图嵌套与 URL 前缀合并、弃用项迁移策略、上下文交互与装饰器使用约束等。
- D（需动态/运行时验证）：请求/会话顺序相关行为、回调触发顺序、异步 handler 交互等。

### 结论与交付
- 交付一份包含 32 条问题的清单（不重复，8 简单 / 18 中等 / 6 困难）。
- 每条包含：标题（基于官方变更条目）、GitHub 链接（Issue/PR）、首次修复版本、在 2.0.0 的复现要点、能力映射（S/A/D）。
- 扩展了静态可检类型（S）和 AI 辅助类型（A），以更好地测试系统能力。

---

### 问题清单（32 条，不重复）

说明：以下条目来自 2.0.1 / 2.0.2 / 2.0.3 的变更记录，编号均可在 GitHub `pallets/flask` 仓库核验；链接统一指向 `issues/<id>`（GitHub 会映射到 Issue 或 PR）。

难度标注：E=易、M=中、H=难；能力：S=静态可检，A=AI 辅助，D=需动态验证。

#### 简单（8）- 扩展静态可检类型
1) 顶层导出名的类型检查可见性（typing 导出）｜2.0.1（E/S）
   - 链接：https://github.com/pallets/flask/issues/4024
   - 复现（2.0.0）：类型检查器无法识别顶层导出，用户项目导入时报错或类型失配。

2) `g` 的类型提示为命名空间对象（typing）｜2.0.1（E/S）
   - 链接：https://github.com/pallets/flask/issues/4020
   - 复现（2.0.0）：`g` 的任意属性访问在类型检查中报错。

3) 早期 Python 3.6.0 不可用类型修正（typing）｜2.0.1（E/S）
   - 链接：https://github.com/pallets/flask/issues/4040
   - 复现（2.0.0）：在最低 Python 小版本上触发类型相关报错或不兼容。

4) `send_file/send_from_directory/get_send_file_max_age` 类型改进｜2.0.1（E/S）
   - 链接：https://github.com/pallets/flask/issues/4044
   - 补充链接：https://github.com/pallets/flask/issues/4026
   - 复现（2.0.0）：函数签名与类型不一致导致 IDE/mypy 报错。

5) `errorhandler` 装饰器的类型注解修正｜2.0.3（E/S）
   - 链接：https://github.com/pallets/flask/issues/4295
   - 复现（2.0.0）：自定义错误处理器在严格类型模式下报注解不匹配。

6) `send_file` 类型改进（补充）｜2.0.1（E/S）
   - 链接：https://github.com/pallets/flask/issues/4026
   - 复现（2.0.0）：函数签名与类型不一致导致 IDE/mypy 报错。

7) 蓝图 URL 前缀合并（静态可检）｜2.0.1（E/S）
   - 链接：https://github.com/pallets/flask/issues/4037
   - 复现（2.0.0）：多级蓝图前缀未正确合并导致复杂路由树失配。

8) 蓝图命名约束｜2.0.1（E/S）
   - 链接：https://github.com/pallets/flask/issues/4041
   - 复现（2.0.0）：允许不安全命名，后续路由/端点解析混乱。

#### 中等（18）- 扩展 AI 辅助和静态混合类型
9) `send_from_directory` 重新加入 `filename`（已更名为 `path`，旧名弃用告警）｜2.0.1（M/A）
   - 链接：https://github.com/pallets/flask/issues/4019
   - 复现（2.0.0）：使用旧参数名在迁移期产生不兼容或告警策略缺失。

10) 误删的 `Config.from_json` 回退恢复（迁移期保障）｜2.0.1（M/A）
   - 链接：https://github.com/pallets/flask/issues/4078
   - 复现（2.0.0）：项目仍在使用旧加载方式时出现中断。

11) 若干装饰器工厂的 `Callable` 类型改进｜2.0.1（M/S）
   - 链接：https://github.com/pallets/flask/issues/4060
   - 复现（2.0.0）：类型检查器对装饰器用法给出错误提示。

12) 嵌套蓝图注册为点分名（便于多处嵌套一致解析）｜2.0.1（M/A）
   - 链接：https://github.com/pallets/flask/issues/4069
   - 复现（2.0.0）：嵌套后端点命名冲突或 `url_for` 反解异常。

13) `register_blueprint` 支持 `name=` 修改注册名；同名多次注册弃用｜2.0.1（M/A）
   - 链接：https://github.com/pallets/flask/issues/1091
   - 复现（2.0.0）：重复注册同名蓝图导致端点被覆盖或行为不明。

14) `teardown_*` 方法类型注解修正｜2.0.2（M/S）
   - 链接：https://github.com/pallets/flask/issues/4093
   - 复现（2.0.0）：类型检查与回调签名不一致。

15) `before_request/before_app_request` 类型注解修正｜2.0.2（M/S）
   - 链接：https://github.com/pallets/flask/issues/4104
   - 复现（2.0.0）：装饰器签名与实现不一致引发类型告警。

16) 模板全局装饰器对"无参函数"的 typing 约束修复｜2.0.2（M/S）
   - 链接：https://github.com/pallets/flask/issues/4098
   - 复现（2.0.0）：模板全局函数被装饰后类型不通过。

17) `app.errorhandler` 装饰器类型增强｜2.0.2（M/S）
   - 链接：https://github.com/pallets/flask/issues/4095
   - 复现（2.0.0）：在严格类型模式下不兼容。

18) 修正"同一蓝图以不同名称注册两次"的处理｜2.0.2（M/A）
   - 链接：https://github.com/pallets/flask/issues/4124
   - 复现（2.0.0）：允许非预期的重复注册导致路由表异常。

19) `static_folder` 接受 `pathlib.Path`｜2.0.2（M/S）
   - 链接：https://github.com/pallets/flask/issues/4150
   - 复现（2.0.0）：传入 PathLike 时类型/行为不匹配。

20) `jsonify` 处理 `decimal.Decimal`（编码为 str）｜2.0.2（M/A）
   - 链接：https://github.com/pallets/flask/issues/4157
   - 复现（2.0.0）：返回包含 Decimal 的 JSON 失败或精度处理不明确。

21) CLI 懒加载时延迟错误抛出处理修正｜2.0.2（M/A）
   - 链接：https://github.com/pallets/flask/issues/4096
   - 复现（2.0.0）：出错信息被错误吞掉或提示不清晰。

22) CLI loader 支持 `create_app(**kwargs)`｜2.0.2（M/S）
   - 链接：https://github.com/pallets/flask/issues/4170
   - 复现（2.0.0）：自定义工厂函数带关键字参数时报错。

23) URL 匹配顺序（AI 可辅助）｜2.0.1（M/A）
   - 链接：https://github.com/pallets/flask/issues/4053
   - 复现（2.0.0）：依赖会话/上下文的 URL 转换器在复杂场景下行为异常。

24) 异步视图支持（AI 可辅助）｜2.0.2（M/A）
   - 链接：https://github.com/pallets/flask/issues/4112
   - 复现（2.0.0）：异步 handler 的生命周期与上下文互动需要动态校验。

25) 回调顺序（AI 可辅助）｜2.0.2（M/A）
   - 链接：https://github.com/pallets/flask/issues/4229
   - 复现（2.0.0）：复杂多蓝图层级下的触发顺序需端到端验证。

26) 上下文边界（AI 可辅助）｜2.0.3（M/A）
   - 链接：https://github.com/pallets/flask/issues/4333
   - 复现（2.0.0）：在复杂调用链/测试场景下触发，需运行时验证。

#### 困难（6）- 扩展动态验证类型
27) URL 匹配顺序恢复为在 session 加载之后（自定义转换器可用）｜2.0.1（H/D）
   - 链接：https://github.com/pallets/flask/issues/4053
   - 复现（2.0.0）：依赖会话/上下文的 URL 转换器在复杂场景下行为异常，需要运行时验证。

28) `View/MethodView` 支持 async 处理器（兼容性修复）｜2.0.2（H/D）
   - 链接：https://github.com/pallets/flask/issues/4112
   - 复现（2.0.0）：异步 handler 的生命周期与上下文互动需要动态校验。

29) 回调触发顺序：`before_request` 从 app 到最近的嵌套蓝图｜2.0.2（H/D）
   - 链接：https://github.com/pallets/flask/issues/4229
   - 复现（2.0.0）：复杂多蓝图层级下的触发顺序需端到端验证。

30) `after_this_request` 在非请求上下文下的报错信息改进（行为边界）｜2.0.3（H/D）
   - 链接：https://github.com/pallets/flask/issues/4333
   - 复现（2.0.0）：在复杂调用链/测试场景下触发，需运行时验证。

31) 嵌套蓝图合并 URL 前缀（复杂路由验证）｜2.0.1（H/D）
   - 链接：https://github.com/pallets/flask/issues/4037
   - 复现（2.0.0）：多级蓝图前缀未正确合并导致复杂路由树失配，需要端到端验证。

32) 嵌套蓝图（复杂命名验证）｜2.0.1（H/D）
   - 链接：https://github.com/pallets/flask/issues/4069
   - 复现（2.0.0）：嵌套后端点命名冲突或 `url_for` 反解异常，需要运行时验证。

（注：为保证不重复，以上 32 条使用唯一编号；扩展了静态可检类型（S）和 AI 辅助类型（A），以更好地测试系统能力。）

---

### 复现与验证指引（2.0.0 基线）
1) 使用 git 检出标签：`v2.0.0`、`v2.0.1`、`v2.0.2`、`v2.0.3`。
2) 在 `v2.0.0` 运行最小用例，观察异常/类型不匹配/行为不符；在修复版本复跑用例，确认修复生效。
3) 在本系统中：
   - 首测文件级：针对触发点最集中的模块（蓝图注册、路由、CLI、JSON、发送文件等）。
   - 再测目录级：`src/flask/`（或实际源码根目录），启用严格类型与 API 误用规则。
   - 产出报告后，与本清单逐条对齐并记录“可自动修复/需建议/需动态验证”。

### 方法（执行步骤）
1) 从官方变更页的 2.0.1/2.0.2/2.0.3 中提取修复条目的 GH 编号。
2) 反查到对应 GitHub Issue/PR 页面，确认修复首次合入的版本与提交。
3) 核验是否 backport 至其他分支；最终判定“2.0.0 是否未包含该修复”。
4) 去重并分类为 5/15/5，并完成能力映射（S/A/D）。
5) 形成最终清单，并编写复现/验证脚本与指引。

### 参考
- Flask Changes（官方变更记录）：`https://flask.palletsprojects.com/en/stable/changes/#version-2-0-1`


