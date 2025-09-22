"""
包含各种代码缺陷的演示文件
用于测试静态检测功能
"""

import os
import sys
import json
import hashlib
import subprocess
from typing import List, Dict, Any

# 1. 未使用的导入
import unused_module

# 2. 硬编码密码
PASSWORD = "admin123"
API_KEY = "sk-1234567890abcdef"

# 3. 不安全的eval使用
def calculate_expression(expr):
    return eval(expr)  # 安全风险

# 4. 缺少类型注解的函数
def process_data(data):
    result = []
    for item in data:
        if item > 10:
            result.append(item * 2)
    return result

# 5. 过长的函数
def very_long_function(param1, param2, param3, param4, param5, param6, param7, param8):
    # 这个函数太长了，应该拆分
    result = []
    for i in range(100):
        if param1 > 0:
            if param2 > 0:
                if param3 > 0:
                    if param4 > 0:
                        if param5 > 0:
                            if param6 > 0:
                                if param7 > 0:
                                    if param8 > 0:
                                        result.append(i * param1 * param2 * param3 * param4 * param5 * param6 * param7 * param8)
    return result

# 6. 重复代码
def calculate_sum1(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

def calculate_sum2(values):
    total = 0
    for val in values:
        total += val
    return total

# 7. 异常处理不当
def read_file(filename):
    try:
        with open(filename, 'r') as f:
            return f.read()
    except:
        return None  # 应该指定具体的异常类型

# 8. 全局变量使用
global_var = 0

def modify_global():
    global global_var
    global_var += 1
    return global_var

# 9. 魔法数字
def check_age(age):
    if age < 18:  # 魔法数字
        return "未成年"
    elif age < 65:  # 魔法数字
        return "成年人"
    else:
        return "老年人"

# 10. 不安全的文件操作
def create_temp_file():
    filename = "/tmp/temp_file.txt"  # 硬编码路径
    with open(filename, 'w') as f:
        f.write("temp data")
    return filename

# 11. 缺少文档字符串
class UserManager:
    def __init__(self):
        self.users = []
    
    def add_user(self, user):
        self.users.append(user)
    
    def get_user(self, user_id):
        for user in self.users:
            if user['id'] == user_id:
                return user
        return None

# 12. 不规范的命名
def BadlyNamedFunction():
    x = 1
    y = 2
    z = x + y
    return z

# 13. 未处理的异常
def divide_numbers(a, b):
    return a / b  # 可能抛出ZeroDivisionError

# 14. 过深的嵌套
def complex_logic(data):
    result = []
    for item in data:
        if item is not None:
            if isinstance(item, dict):
                if 'value' in item:
                    if item['value'] > 0:
                        if item['value'] < 100:
                            if item['value'] % 2 == 0:
                                result.append(item['value'])
    return result

# 15. 不安全的随机数使用
import random

def generate_token():
    return random.randint(1000, 9999)  # 不安全的随机数

# 16. 内存泄漏风险
def process_large_data():
    data = []
    for i in range(1000000):
        data.append(i * 2)
    # 没有清理大对象
    return len(data)

# 17. 缺少输入验证
def process_user_input(user_input):
    # 没有验证输入
    return user_input.upper()

# 18. 不规范的代码格式
def badly_formatted_function(  param1,param2,param3  ):
    if param1>0 and param2>0 and param3>0:
        return param1+param2+param3
    else:
        return 0

# 19. 死代码
def unused_function():
    return "这个函数永远不会被调用"

def main():
    # 20. 未使用的变量
    unused_variable = "这个变量不会被使用"
    
    # 测试一些函数
    data = [1, 2, 3, 4, 5]
    result = process_data(data)
    print(f"处理结果: {result}")
    
    # 测试不安全的函数
    try:
        result = calculate_expression("2 + 2")
        print(f"计算结果: {result}")
    except Exception as e:
        print(f"计算错误: {e}")

if __name__ == "__main__":
    main()
