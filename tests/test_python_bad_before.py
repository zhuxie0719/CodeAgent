# test_python_bad.py - 有问题的Python代码示例
import os
import sys
import unused_module  # 未使用的导入

# 硬编码的API密钥
API_KEY = "sk-1234567890abcdef"
SECRET_PASSWORD = "admin123"

def bad_function():
    # 缺少文档字符串
    x = 1
    y = 2
    z = x + y
    return z

def risky_function():
    # 不安全的eval使用
    user_input = "print('Hello')"
    result = eval(user_input)  # 安全风险
    return result

def process_user_data(data):
    # 缺少类型提示和文档字符串
    # 缺少输入验证
    processed = data * 2
    return processed

def divide_numbers(a, b):
    # 缺少异常处理
    result = a / b  # 可能除零错误
    return result

# 全局变量（不好的实践）
global_var = "I'm global"

def use_global():
    global global_var
    global_var = "modified"
    return global_var

# 不安全的文件操作
def read_file(filename):
    # 没有异常处理
    with open(filename, 'r') as f:
        content = f.read()
    return content

# 内存泄漏风险
def create_large_list():
    big_list = []
    for i in range(1000000):
        big_list.append(f"item_{i}")
    return big_list

# 缺少主函数保护
print("This will always execute")

# 不安全的字符串格式化
def format_string(user_input):
    query = "SELECT * FROM users WHERE name = '%s'" % user_input  # SQL注入风险
    return query

