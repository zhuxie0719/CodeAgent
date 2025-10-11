#!/usr/bin/env python3
"""
测试修复后的静态分析工具
"""
import sys
import os
import asyncio
import json

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.static_analysis.pylint_tool import PylintTool
from tools.static_analysis.flake8_tool import Flake8Tool

async def test_pylint():
    """测试Pylint工具"""
    print("=== 测试Pylint工具 ===")
    
    config = {
        "pylint_args": [
            "--disable=C0114",  # 禁用missing-module-docstring
            "--disable=C0116",  # 禁用missing-function-docstring
            "--disable=C0103",  # 禁用invalid-name
            "--disable=C0115",  # 禁用missing-class-docstring
        ]
    }
    
    tool = PylintTool(config)
    test_file = "tests/test_python_bad.py"
    
    try:
        result = await tool.analyze(test_file)
        print(f"分析成功: {result.get('success')}")
        print(f"总问题数: {result.get('total_issues')}")
        
        issues = result.get('issues', [])
        print(f"检测到的问题数量: {len(issues)}")
        
        if issues:
            print("\n前5个问题:")
            for i, issue in enumerate(issues[:5]):
                print(f"  {i+1}. {issue}")
        else:
            print("没有检测到问题")
            
        return len(issues)
        
    except Exception as e:
        print(f"Pylint分析失败: {e}")
        return 0

async def test_flake8():
    """测试Flake8工具"""
    print("\n=== 测试Flake8工具 ===")
    
    config = {
        "flake8_args": [
            "--max-line-length=120",
            "--ignore=E501",  # 忽略行长度
        ]
    }
    
    tool = Flake8Tool(config)
    test_file = "tests/test_python_bad.py"
    
    try:
        result = await tool.analyze(test_file)
        print(f"分析成功: {result.get('success')}")
        print(f"总问题数: {result.get('total_issues')}")
        
        issues = result.get('issues', [])
        print(f"检测到的问题数量: {len(issues)}")
        
        if issues:
            print("\n前5个问题:")
            for i, issue in enumerate(issues[:5]):
                print(f"  {i+1}. {issue}")
        else:
            print("没有检测到问题")
            
        return len(issues)
        
    except Exception as e:
        print(f"Flake8分析失败: {e}")
        return 0

async def main():
    """主测试函数"""
    print("开始测试修复后的静态分析工具...")
    
    pylint_issues = await test_pylint()
    flake8_issues = await test_flake8()
    
    print(f"\n=== 测试结果总结 ===")
    print(f"Pylint检测到的问题: {pylint_issues}")
    print(f"Flake8检测到的问题: {flake8_issues}")
    print(f"总问题数: {pylint_issues + flake8_issues}")
    
    if pylint_issues + flake8_issues > 0:
        print("✅ 工具修复成功！能够检测到代码问题")
    else:
        print("❌ 工具仍有问题，无法检测到代码问题")

if __name__ == "__main__":
    asyncio.run(main())