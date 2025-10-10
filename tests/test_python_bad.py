"""
包含各种代码质量问题的Python文件
用于测试代码质量检测和修复功能
"""

import os

# 硬编码的敏感信息
API_KEY = os.getenv("API_KEY", "")
SECRET = "my_secret_password"
PASSWORD = "admin123"

def bad_function(x):
    """缺少参数验证的函数"""
    return x * 2

def risky_function(data):
    """使用不安全的eval函数"""
    return eval(data)

def process_user_data(user_input):
    """处理用户输入但缺少验证"""
    result = risky_function(user_input)
    return result

def divide_numbers(a, b):
    """除法函数但缺少异常处理"""
    return a / b if b != 0 else 0

# 全局变量使用
global_var = "I'm global"

def use_global():
    """使用全局变量"""
    return global_var

def read_file(filename):
    """文件读取但缺少异常处理"""
    with open(filename, 'r') as f:
        return f.read()

def create_large_list(size):
    """创建大列表但缺少参数验证"""
    return [i for i in range(size)]

def format_string(template, *args):
    """字符串格式化但缺少异常处理"""
    return template.format(*args)

def convert_to_int(value):
    """类型转换但缺少异常处理"""
    return int(value)

if __name__ == "__main__":
    # 测试各种函数
    print(bad_function(5))
    print(risky_function("2 + 2"))
    print(divide_numbers(10, 2))
    print(use_global())
    print(format_string("Hello {}", "World"))
    print(convert_to_int("123"))