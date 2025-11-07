# Flask安全测试项目

这是一个用于动态和静态安全测试的小型Flask项目，包含3个典型的安全缺陷。

## 项目结构

- `app.py` - Flask主应用文件，包含3个安全缺陷
- `app_after.py` - 修复后的安全版本（用于对比）
- `vulnerable.py` - 额外的漏洞测试文件，包含4个安全缺陷
- `requirements.txt` - 项目依赖
- `README.md` - 项目说明文档

## 安装和运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行应用：
```bash
# 运行主应用（端口5000）
python app.py

# 运行额外漏洞测试文件（端口5001）
python vulnerable.py
```

3. 访问应用：
- 主应用: `http://localhost:5000`
- 漏洞测试: `http://localhost:5001`

## 包含的安全缺陷

### 缺陷1: SQL注入漏洞 (`/search`)
- **位置**: `app.py` 第18行
- **问题**: 直接使用字符串拼接将用户输入插入SQL查询
- **测试方法**: 
  - 访问: `http://localhost:5000/search?q=admin`
  - SQL注入: `http://localhost:5000/search?q=' OR '1'='1`
  - 或: `http://localhost:5000/search?q=' UNION SELECT null,null,null--`

### 缺陷2: XSS跨站脚本攻击 (`/comment`)
- **位置**: `app.py` 第32行
- **问题**: 未对用户输入进行转义，直接渲染到HTML
- **测试方法**: 
  - 访问: `http://localhost:5000/comment`
  - 在评论框中输入: `<script>alert('XSS')</script>`
  - 或: `<img src=x onerror=alert('XSS')>`

### 缺陷3: 服务器端模板注入 SSTI (`/template`)
- **位置**: `app.py` 第55行
- **问题**: 允许用户控制模板内容，未进行过滤
- **测试方法**: 
  - 访问: `http://localhost:5000/template`
  - 在模板框中输入: `{{ config }}`
  - 或: `{{ ''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read() }}`
  - 或: `{{ self.__init__.__globals__.__builtins__.__import__('os').popen('whoami').read() }}`

## vulnerable.py 中的额外缺陷

### 缺陷1: 路径遍历漏洞 (`/file`)
- **位置**: `vulnerable.py` 第11行
- **问题**: 直接使用用户输入构建文件路径，未进行路径验证和限制
- **测试方法**: 
  - 路径遍历: `http://localhost:5001/file?name=../../etc/passwd` (Linux)
  - 或: `http://localhost:5001/file?name=../../windows/win.ini` (Windows)
  - 或: `http://localhost:5001/file?name=../../app.py`

### 缺陷2: 命令注入漏洞 (`/ping`)
- **位置**: `vulnerable.py` 第20行
- **问题**: 直接拼接用户输入到系统命令中，使用shell=True执行
- **测试方法**: 
  - 命令注入: `http://localhost:5001/ping?host=127.0.0.1 && whoami`
  - 或: `http://localhost:5001/ping?host=127.0.0.1 | dir` (Windows)
  - 或: `http://localhost:5001/ping?host=127.0.0.1; cat /etc/passwd` (Linux)

### 缺陷3: 不安全的反序列化漏洞 (`/data`)
- **位置**: `vulnerable.py` 第30行
- **问题**: 直接反序列化用户提供的数据，可能导致任意代码执行
- **测试方法**: 
  - 使用pickle序列化恶意对象进行攻击
  - 需要构造特定的payload来执行代码

### 缺陷4: 敏感信息泄露 (`/admin`)
- **位置**: `vulnerable.py` 第40行
- **问题**: 错误信息中泄露了系统路径、配置信息等敏感数据
- **测试方法**: 
  - 访问: `http://localhost:5001/admin?username=test&password=wrong`
  - 查看错误响应中的系统信息

## 安全建议

这些缺陷仅用于安全测试和教育目的。在生产环境中应该：

1. **防止SQL注入**: 使用参数化查询或ORM
2. **防止XSS**: 对所有用户输入进行转义（Flask的Jinja2默认会转义，但使用`render_template_string`时需注意）
3. **防止SSTI**: 严格限制模板内容，不允许用户控制模板结构
4. **防止路径遍历**: 验证和规范化文件路径，使用白名单限制可访问的文件
5. **防止命令注入**: 避免使用shell=True，使用参数列表而非字符串命令，或使用更安全的API
6. **防止反序列化攻击**: 避免反序列化不可信的数据，使用JSON等安全格式
7. **防止信息泄露**: 不要在错误信息中暴露系统路径、配置等敏感信息

## 注意事项

⚠️ **警告**: 此项目仅用于安全测试和学习目的，请勿在生产环境中使用！

