#!/usr/bin/env python3
"""
最小化测试 - 不依赖终端
"""
import sys
import os
import json

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """测试是否能导入工具"""
    try:
        from tools.static_analysis.pylint_tool import PylintTool
        from tools.static_analysis.flake8_tool import Flake8Tool
        print("✅ 工具导入成功")
        return True
    except Exception as e:
        print(f"❌ 工具导入失败: {e}")
        return False

def test_tool_creation():
    """测试工具创建"""
    try:
        from tools.static_analysis.pylint_tool import PylintTool
        from tools.static_analysis.flake8_tool import Flake8Tool
        
        config = {"pylint_args": ["--disable=C0114"]}
        pylint_tool = PylintTool(config)
        print("✅ PylintTool创建成功")
        
        config = {"flake8_args": ["--max-line-length=120"]}
        flake8_tool = Flake8Tool(config)
        print("✅ Flake8Tool创建成功")
        
        return True
    except Exception as e:
        print(f"❌ 工具创建失败: {e}")
        return False

def test_simple_analysis():
    """测试简单分析（不实际运行）"""
    try:
        from tools.static_analysis.pylint_tool import PylintTool
        from tools.static_analysis.flake8_tool import Flake8Tool
        
        # 测试Pylint工具
        config = {"pylint_args": ["--disable=C0114"]}
        pylint_tool = PylintTool(config)
        print("✅ PylintTool配置成功")
        
        # 测试Flake8工具
        config = {"flake8_args": ["--max-line-length=120"]}
        flake8_tool = Flake8Tool(config)
        print("✅ Flake8Tool配置成功")
        
        return True
    except Exception as e:
        print(f"❌ 工具配置失败: {e}")
        return False

if __name__ == "__main__":
    print("开始最小化测试...")
    
    import_ok = test_import()
    creation_ok = test_tool_creation()
    config_ok = test_simple_analysis()
    
    print(f"\n=== 测试结果 ===")
    print(f"导入测试: {'✅' if import_ok else '❌'}")
    print(f"创建测试: {'✅' if creation_ok else '❌'}")
    print(f"配置测试: {'✅' if config_ok else '❌'}")
    
    if import_ok and creation_ok and config_ok:
        print("\n🎉 所有基础测试通过！工具应该能正常工作")
    else:
        print("\n⚠️ 部分测试失败，需要进一步检查")


