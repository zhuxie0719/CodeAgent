#!/usr/bin/env python3
"""
测试项目 - 包含各种问题
"""

import os
import sys

# 未使用的变量
unused_var = "test"

def divide_by_zero():
    """除零错误"""
    return 10 / 0

def security_issue():
    """安全问题"""
    eval("os.system('ls')")  # 危险操作

def main():
    print("Hello World")
    divide_by_zero()
    security_issue()

if __name__ == "__main__":
    main()
