# Flask 2.0.0 Bug测试

本项目用于测试bug检测agent对Flask 2.0.0版本中32个已知bug的检测能力。

## 文件说明

- `app.py` - Flask应用主文件，包含复现32个bug的测试用例
- `run_test.py` - 启动测试服务器
- `bug_test.py` - 测试套件，验证bug复现
- `setup.py` - 自动设置Flask 2.0.0环境
- `requirements.txt` - 依赖包版本要求
- `flask-2.0.0.zip` - Flask 2.0.0源码压缩包

## 使用方法

### 1. 设置环境（首次运行）

```bash
python setup.py
```

这将自动：
- 解压flask-2.0.0.zip
- 创建虚拟环境
- 安装Flask 2.0.0源码
- 安装兼容的werkzeug==2.0.0

### 2. 激活虚拟环境

Windows:
```cmd
activate.bat
```

Linux/Mac:
```bash
source activate.sh
```

### 3. 运行测试

启动Flask应用:
```bash
python run_test.py
```

在另一个终端运行测试套件:
```bash
python bug_test.py
```

### 4. 前端上传检测

将整个`flask_simple_test`文件夹打包成zip，通过前端上传进行静态和动态检测。

## 已知Bug列表

根据`docs/Flask版本选择与Issue策略.md`文档，共32个bug：

### 简单类型 (8个)
- Bug #1: g类型提示
- Bug #2-3: 类型相关修复
- Bug #4, #6: send_file类型问题
- Bug #5: errorhandler装饰器
- Bug #7: 蓝图URL前缀
- Bug #8: 蓝图命名约束

### 中等类型 (18个)
- Bug #9: send_from_directory filename参数
- Bug #10: Config.from_json缺失
- Bug #11-17: 装饰器类型问题
- Bug #18: 重复注册蓝图
- Bug #19: static_folder Path支持
- Bug #20: jsonify Decimal处理
- Bug #21-22: CLI相关问题
- Bug #23-26: URL匹配和上下文问题

### 困难类型 (6个)
- Bug #27: URL匹配顺序
- Bug #28: 异步处理器
- Bug #29: 回调触发顺序
- Bug #30: after_this_request上下文
- Bug #31-32: 嵌套蓝图复杂路由

## 检测能力映射

- **S (静态可检)**: Bug #1-8, #11, #14-16, #19, #22
- **A (AI辅助)**: Bug #9-10, #12-13, #18, #20-21, #23-26
- **D (动态验证)**: Bug #27-32

## 注意事项

1. 确保使用Python 3.7+（Flask 2.0.0要求）
2. werkzeug版本必须为2.0.0（与Flask 2.0.0匹配）
3. 部分bug需要运行时代码才能触发，静态检测可能无法完全识别


