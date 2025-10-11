#!/usr/bin/env python3
"""
直接测试工具调用
"""
import sys
import os
import asyncio

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_direct_tool_call():
    """直接测试工具调用"""
    try:
        print("开始直接测试工具调用...")
        
        # 测试文件
        test_file = "tests/test_python_bad.py"
        
        # 测试Pylint
        print("\n=== 测试Pylint ===")
        try:
            from tools.static_analysis.pylint_tool import PylintTool
            config = {"pylint_args": ["--disable=C0114"]}
            pylint_tool = PylintTool(config)
            
            result = await pylint_tool.analyze(test_file)
            print(f"Pylint结果: {result}")
            
            if result.get("issues"):
                print(f"✅ Pylint检测到 {len(result['issues'])} 个问题")
            else:
                print("⚠️ Pylint没有检测到问题")
                
        except Exception as e:
            print(f"❌ Pylint失败: {e}")
        
        # 测试Flake8
        print("\n=== 测试Flake8 ===")
        try:
            from tools.static_analysis.flake8_tool import Flake8Tool
            config = {"flake8_args": ["--max-line-length=120"]}
            flake8_tool = Flake8Tool(config)
            
            result = await flake8_tool.analyze(test_file)
            print(f"Flake8结果: {result}")
            
            if result.get("issues"):
                print(f"✅ Flake8检测到 {len(result['issues'])} 个问题")
            else:
                print("⚠️ Flake8没有检测到问题")
                
        except Exception as e:
            print(f"❌ Flake8失败: {e}")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_tool_call())


