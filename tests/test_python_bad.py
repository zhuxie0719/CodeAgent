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

def unsafe_eval():
    # 不安全的eval使用
    user_input = "print('Hello')"
    result = eval(user_input)  # 安全风险
    return result

def process_user_data(data):
    # 缺少类型提示和文档字符串
    # 缺少输入验证
    processed = data.upper()
    return processed

def divide_numbers(a, b):
    # 缺少异常处理
    result = a / b  # 可能除零错误
    return result

# 全局变量
global_var = "global"

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

# 不安全的字符串格式化
def format_string(user_input):
    query = "SELECT * FROM users WHERE name = '%s'" % user_input  # SQL注入风险
    return query

# 未处理的异常
def risky_operation():
    data = {"key": "value"}
    return data["nonexistent_key"]  # KeyError

# 死代码
def unreachable_code():
    return "reached"
    print("This will never execute")  # 死代码

# 类定义问题
class BadClass:
    def __init__(self):
        self.value = None
    
    def method_without_docstring(self):
        return self.value

# 主程序
if __name__ == "__main__":
    # 直接执行可能有问题的代码
    result = divide_numbers(10, 0)  # 除零错误
    print(result)