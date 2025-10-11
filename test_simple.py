#!/usr/bin/env python3
"""
简单测试修复后的工具
"""
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.static_analysis.pylint_tool import PylintTool
from tools.static_analysis.flake8_tool import Flake8Tool

async def test_tools():
    test_file = "tests/test_python_bad.py"
    
    print("测试修复后的工具...")
    
    # 测试Pylint
    print("\n=== 测试Pylint ===")
    config = {"pylint_args": ["--disable=C0114"]}
    pylint_tool = PylintTool(config)
    
    try:
        result = await pylint_tool.analyze(test_file)
        print(f"Success: {result.get('success')}")
        print(f"Total issues: {result.get('total_issues')}")
        print(f"Issues count: {len(result.get('issues', []))}")
        
        if result.get('issues'):
            print("发现的问题:")
            for i, issue in enumerate(result['issues'][:3]):
                print(f"  {i+1}. {issue}")
        else:
            print("没有发现问题")
            
    except Exception as e:
        print(f"Pylint错误: {e}")
    
    # 测试Flake8
    print("\n=== 测试Flake8 ===")
    config = {"flake8_args": ["--max-line-length=120"]}
    flake8_tool = Flake8Tool(config)
    
    try:
        result = await flake8_tool.analyze(test_file)
        print(f"Success: {result.get('success')}")
        print(f"Total issues: {result.get('total_issues')}")
        print(f"Issues count: {len(result.get('issues', []))}")
        
        if result.get('issues'):
            print("发现的问题:")
            for i, issue in enumerate(result['issues'][:3]):
                print(f"  {i+1}. {issue}")
        else:
            print("没有发现问题")
            
    except Exception as e:
        print(f"Flake8错误: {e}")

if __name__ == "__main__":
    asyncio.run(test_tools())

