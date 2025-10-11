#!/usr/bin/env python3
"""
使用Python模块方式调用pylint和flake8
"""
import sys
import os
import json
import io
from contextlib import redirect_stdout, redirect_stderr

def test_pylint_module():
    print("=== 使用模块方式测试Pylint ===")
    test_file = "tests/test_python_bad.py"
    
    try:
        # 导入pylint模块
        from pylint import lint
        from pylint.reporters import JSONReporter
        
        # 创建输出缓冲区
        output = io.StringIO()
        
        # 配置参数
        args = [test_file, '--disable=C0114', '--output-format=json']
        
        # 运行pylint
        with redirect_stdout(output), redirect_stderr(output):
            lint.Run(args, exit=False)
        
        result = output.getvalue()
        print(f"输出长度: {len(result)}")
        if result:
            print("前200个字符:")
            print(repr(result[:200]))
            
    except ImportError as e:
        print(f"无法导入pylint模块: {e}")
    except Exception as e:
        print(f"错误: {e}")

def test_flake8_module():
    print("\n=== 使用模块方式测试Flake8 ===")
    test_file = "tests/test_python_bad.py"
    
    try:
        # 导入flake8模块
        import flake8.main.application
        
        # 创建应用实例
        app = flake8.main.application.Application()
        
        # 配置参数
        args = [test_file, '--max-line-length=120']
        
        # 创建输出缓冲区
        output = io.StringIO()
        
        # 运行flake8
        with redirect_stdout(output), redirect_stderr(output):
            app.run(args)
        
        result = output.getvalue()
        print(f"输出长度: {len(result)}")
        if result:
            print("前200个字符:")
            print(repr(result[:200]))
            
    except ImportError as e:
        print(f"无法导入flake8模块: {e}")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    test_pylint_module()
    test_flake8_module()

