#!/usr/bin/env python3
"""
简单测试工具导入
"""
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试导入"""
    try:
        print("测试导入...")
        
        # 测试工具导入
        from tools.static_analysis.pylint_tool import PylintTool
        print("✅ PylintTool导入成功")
        
        from tools.static_analysis.flake8_tool import Flake8Tool
        print("✅ Flake8Tool导入成功")
        
        # 测试工具创建
        config = {"pylint_args": ["--disable=C0114"]}
        pylint_tool = PylintTool(config)
        print("✅ PylintTool创建成功")
        
        config = {"flake8_args": ["--max-line-length=120"]}
        flake8_tool = Flake8Tool(config)
        print("✅ Flake8Tool创建成功")
        
        print("\n=== 导入测试完成 ===")
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_imports()


