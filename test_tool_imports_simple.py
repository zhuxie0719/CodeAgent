#!/usr/bin/env python3
"""
测试工具导入和创建
"""
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_tool_imports():
    """测试工具导入"""
    try:
        print("测试工具导入...")
        
        # 测试PylintTool导入
        try:
            from tools.static_analysis.pylint_tool import PylintTool
            print("✅ PylintTool导入成功")
            
            # 测试创建
            config = {"pylint_args": ["--disable=C0114"]}
            tool = PylintTool(config)
            print("✅ PylintTool创建成功")
            
        except Exception as e:
            print(f"❌ PylintTool失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 测试Flake8Tool导入
        try:
            from tools.static_analysis.flake8_tool import Flake8Tool
            print("✅ Flake8Tool导入成功")
            
            # 测试创建
            config = {"flake8_args": ["--max-line-length=120"]}
            tool = Flake8Tool(config)
            print("✅ Flake8Tool创建成功")
            
        except Exception as e:
            print(f"❌ Flake8Tool失败: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n=== 导入测试完成 ===")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tool_imports()


