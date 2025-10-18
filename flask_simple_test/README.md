# Flask 2.0.0 简化测试项目

这个项目包含Flask 2.0.0中32个已知Issue的复现代码，避免循环导入问题。

## 文件说明

- `test_flask_simple.py` - 包含32个Issue的测试代码
- `run_tests.py` - 测试运行器
- `flask_app.py` - Flask Web应用（用于动态检测测试）

## 使用方法

1. 运行测试：
   ```bash
   python run_tests.py
   ```

2. 启动Flask Web应用（用于动态检测测试）：
   ```bash
   python flask_app.py
   ```

3. 使用检测系统分析：
   ```bash
   python start_api.py
   # 然后上传 flask_simple_test 目录
   # 记得启用"Web应用测试"选项
   ```

4. 运行对比分析：
   ```bash
   python compare_flask_bugs.py
   ```

## 包含的Issue

### S类（静态可检）- 8个
- #4024 - 顶层导出名类型检查
- #4020 - g对象类型提示
- #4040 - 早期Python类型修正
- #4044 - send_file类型改进
- #4026 - send_file类型改进
- #4295 - errorhandler类型注解
- #4037 - 蓝图URL前缀合并
- #4041 - 蓝图命名约束

### A类（AI辅助）- 18个
- #4019 - send_from_directory参数
- #4078 - Config.from_json回退
- #4060 - 装饰器工厂类型
- #4069 - 嵌套蓝图注册
- #1091 - 蓝图重复注册
- #4093 - teardown方法类型
- #4104 - before_request类型
- #4098 - 模板全局装饰器
- #4095 - errorhandler类型增强
- #4124 - 蓝图重复注册处理
- #4150 - static_folder PathLike
- #4157 - jsonify Decimal处理
- #4096 - CLI懒加载错误
- #4170 - CLI loader kwargs
- #4053 - URL匹配顺序
- #4112 - 异步视图支持
- #4229 - 回调顺序
- #4333 - 上下文边界

### D类（动态验证）- 6个
- #4053 - URL匹配顺序（运行时）
- #4112 - 异步视图（运行时）
- #4229 - 回调顺序（运行时）
- #4333 - 上下文边界（运行时）
- #4037 - 蓝图前缀合并（复杂）
- #4069 - 嵌套蓝图（复杂）

## 注意事项

这个项目避免了循环导入问题，专注于测试代码的逻辑和结构。
所有32个Issue都是基于官方文档中的已知问题。
