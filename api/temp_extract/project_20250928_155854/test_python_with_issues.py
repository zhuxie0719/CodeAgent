#!/usr/bin/env python3
"""
测试文件 - 包含各种缺陷
"""

import os
import sys

# 硬编码密钥
API_KEY = "sk-1234567890abcdef"
SECRET_PASSWORD = "admin123"

def unsafe_function():
    """不安全的函数"""
    # 不安全的eval使用
    user_input = "print('Hello World')"
    result = eval(user_input)
    return result

def missing_docstring_function():
    # 缺少文档字符串
    return "test"

def unused_import_test():
    # 未使用的导入
    import unused_module
    return "test"

def main():
    print("测试文件运行中...")
    unsafe_function()
    missing_docstring_function()
    unused_import_test()

if __name__ == "__main__":
    main()
