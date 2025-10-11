#!/usr/bin/env python3
"""
直接测试pylint和flake8工具
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.static_analysis.pylint_tool import PylintTool
from tools.static_analysis.flake8_tool import Flake8Tool

def test_tools():
    test_file = "tests/test_python_bad.py"
    
    # 先检查文件是否存在
    if not os.path.exists(test_file):
        print(f"错误: 文件 {test_file} 不存在")
        return
    
    print("=" * 50)
    print("测试Pylint工具")
    print("=" * 50)
    
    pylint_tool = PylintTool()
    pylint_result = pylint_tool.run(test_file)
    
    print(f"Pylint结果:")
    print(f"  success: {pylint_result.get('success')}")
    print(f"  total_issues: {pylint_result.get('total_issues')}")
    print(f"  issues: {len(pylint_result.get('issues', []))}")
    print(f"  stdout: {pylint_result.get('stdout', '')[:200]}...")
    print(f"  stderr: {pylint_result.get('stderr', '')[:200]}...")
    
    if pylint_result.get('issues'):
        print("前3个问题:")
        for i, issue in enumerate(pylint_result['issues'][:3]):
            print(f"  {i+1}. {issue}")
    
    print("\n" + "=" * 50)
    print("测试Flake8工具")
    print("=" * 50)
    
    flake8_tool = Flake8Tool()
    flake8_result = flake8_tool.run(test_file)
    
    print(f"Flake8结果:")
    print(f"  success: {flake8_result.get('success')}")
    print(f"  total_issues: {flake8_result.get('total_issues')}")
    print(f"  issues: {len(flake8_result.get('issues', []))}")
    print(f"  stdout: {flake8_result.get('stdout', '')[:200]}...")
    print(f"  stderr: {flake8_result.get('stderr', '')[:200]}...")
    
    if flake8_result.get('issues'):
        print("前3个问题:")
        for i, issue in enumerate(flake8_result['issues'][:3]):
            print(f"  {i+1}. {issue}")

if __name__ == "__main__":
    test_tools()
