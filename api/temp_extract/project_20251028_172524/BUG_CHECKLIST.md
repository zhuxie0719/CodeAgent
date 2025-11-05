# Flask 2.0.0 Bug检测清单

本文件列出了在`app.py`中可以复现的32个已知bug。

## Bug覆盖情况

### 静态可检测 (S) - 14个
- [x] Bug #1: g类型提示 (g.user_id, g.data) - Line 26-27
- [x] Bug #4: send_file类型改进 - Line 31-38
- [x] Bug #6: send_file类型改进 - Line 31-38
- [x] Bug #7: 蓝图URL前缀合并 - Line 46-47
- [x] Bug #8: 蓝图命名约束 - Line 81
- [x] Bug #11: 装饰器类型改进 - Line 157-165
- [x] Bug #14: teardown_request类型注解 - Line 158-160
- [x] Bug #15: before_request类型注解 - Line 162-164
- [x] Bug #16: 模板全局装饰器 - Line 171-174
- [x] Bug #17: errorhandler装饰器类型 - Line 176-179
- [x] Bug #19: static_folder Path支持 - Line 127-130
- [x] Bug #22: create_app工厂函数 - Line 181-185

### AI辅助可检测 (A) - 10个
- [x] Bug #9: send_from_directory filename参数 - Line 90-96
- [x] Bug #10: Config.from_json缺失 - Line 98-104
- [x] Bug #12: 嵌套蓝图 - Line 46-62
- [x] Bug #13: register_blueprint name参数 - Line 111-113
- [x] Bug #18: 重复注册蓝图 - Line 111-113
- [x] Bug #20: jsonify Decimal处理 - Line 132-140
- [x] Bug #23: URL匹配顺序 - Line 145-148
- [x] Bug #25: 回调触发顺序 - Line 180-204
- [x] Bug #26: 上下文边界 - Line 206-217

### 需动态验证 (D) - 6个
- [x] Bug #24: 异步handler支持 - Line 143-147
- [x] Bug #27: URL匹配顺序(运行时) - Line 145-148
- [x] Bug #28: 异步处理器 - Line 143-147
- [x] Bug #29: 回调触发顺序(运行时) - Line 180-204
- [x] Bug #30: after_this_request上下文 - Line 206-217
- [x] Bug #31: 嵌套蓝图复杂路由 - Line 46-62
- [x] Bug #32: 嵌套蓝图命名验证 - Line 46-62

### 无法直接复现 (8个)
- [ ] Bug #2: g类型提示为命名空间对象 (已在#1中测试)
- [ ] Bug #3: Python 3.6.0类型修正 (需要特定Python版本)
- [ ] Bug #5: errorhandler装饰器类型 (已在#17中测试)
- [ ] Bug #21: CLI懒加载延迟错误 (需要CLI测试)
- [ ] Bug #2-3: 类型相关 (IDE检查, 已在#1中体现)

## 测试路由映射

| Bug # | 路由 | 说明 |
|-------|------|------|
| #1 | `/bug1_g_type` | g类型提示问题 |
| #4, #6 | `/bug4_send_file_type` | send_file类型问题 |
| #7, #31 | `/parent` | 蓝图URL前缀合并 |
| #9 | `/bug9_send_from_directory` | send_from_directory参数 |
| #10 | `/bug10_config_json` | Config.from_json缺失 |
| #12, #32 | `/parent/child` | 嵌套蓝图问题 |
| #19 | `/bug19_static_folder` | static_folder Path支持 |
| #20 | `/bug20_jsonify_decimal` | jsonify Decimal处理 |
| #24, #28 | `/bug24_async` | 异步handler |
| #25, #29 | `/bug25_callback_order` | 回调触发顺序 |
| #26, #30 | `/bug26_context` | 上下文边界 |
| #5, #17 | `/unknown` | 404错误处理 |

## 检测建议

1. **静态检测**: 上传后先进行静态分析，查找类型问题、API使用不当
2. **动态检测**: 运行应用并访问各个路由，验证运行时行为
3. **AI辅助**: 分析复杂上下文和装饰器使用模式


