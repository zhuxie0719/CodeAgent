#!/usr/bin/env python3
"""
测试工具初始化和调用
"""
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.static_analysis.pylint_tool import PylintTool
from tools.static_analysis.flake8_tool import Flake8Tool

async def test_tools_async():
    test_file = "tests/test_python_bad.py"
    
    print("=" * 50)
    print("测试Pylint工具 (异步)")
    print("=" * 50)
    
    # 使用与BugDetectionAgent相同的配置
    config = {"pylint_args": ["--disable=C0114"]}
    pylint_tool = PylintTool(config)
    
    try:
        pylint_result = await pylint_tool.analyze(test_file)
        
        print(f"Pylint结果:")
        print(f"  success: {pylint_result.get('success')}")
        print(f"  total_issues: {pylint_result.get('total_issues')}")
        print(f"  issues count: {len(pylint_result.get('issues', []))}")
        print(f"  stdout length: {len(pylint_result.get('stdout', ''))}")
        print(f"  stderr length: {len(pylint_result.get('stderr', ''))}")
        
        if pylint_result.get('issues'):
            print("前3个问题:")
            for i, issue in enumerate(pylint_result['issues'][:3]):
                print(f"  {i+1}. {issue}")
        else:
            print("  没有发现问题")
            print(f"  stdout: {pylint_result.get('stdout', '')[:500]}")
            print(f"  stderr: {pylint_result.get('stderr', '')[:500]}")
            
    except Exception as e:
        print(f"Pylint测试失败: {e}")
    
    print("\n" + "=" * 50)
    print("测试Flake8工具 (异步)")
    print("=" * 50)
    
    config = {"flake8_args": ["--max-line-length=120"]}
    flake8_tool = Flake8Tool(config)
    
    try:
        flake8_result = await flake8_tool.analyze(test_file)
        
        print(f"Flake8结果:")
        print(f"  success: {flake8_result.get('success')}")
        print(f"  total_issues: {flake8_result.get('total_issues')}")
        print(f"  issues count: {len(flake8_result.get('issues', []))}")
        print(f"  stdout length: {len(flake8_result.get('stdout', ''))}")
        print(f"  stderr length: {len(flake8_result.get('stderr', ''))}")
        
        if flake8_result.get('issues'):
            print("前3个问题:")
            for i, issue in enumerate(flake8_result['issues'][:3]):
                print(f"  {i+1}. {issue}")
        else:
            print("  没有发现问题")
            print(f"  stdout: {flake8_result.get('stdout', '')[:500]}")
            print(f"  stderr: {flake8_result.get('stderr', '')[:500]}")
            
    except Exception as e:
        print(f"Flake8测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_tools_async())

