#!/usr/bin/env python3
"""
测试工具初始化
"""
import sys
import os
import asyncio

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_tool_initialization():
    """测试工具初始化"""
    try:
        from tools.static_analysis.pylint_tool import PylintTool
        from tools.static_analysis.flake8_tool import Flake8Tool
        
        print("开始测试工具初始化...")
        
        # 测试Pylint工具
        print("\n=== 测试Pylint工具 ===")
        try:
            config = {"pylint_args": ["--disable=C0114"]}
            pylint_tool = PylintTool(config)
            print("✅ PylintTool创建成功")
            
            # 测试分析
            result = await pylint_tool.analyze("tests/test_python_bad.py")
            print(f"✅ Pylint分析结果: {result}")
            
        except Exception as e:
            print(f"❌ Pylint工具失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 测试Flake8工具
        print("\n=== 测试Flake8工具 ===")
        try:
            config = {"flake8_args": ["--max-line-length=120"]}
            flake8_tool = Flake8Tool(config)
            print("✅ Flake8Tool创建成功")
            
            # 测试分析
            result = await flake8_tool.analyze("tests/test_python_bad.py")
            print(f"✅ Flake8分析结果: {result}")
            
        except Exception as e:
            print(f"❌ Flake8工具失败: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tool_initialization())


