#!/usr/bin/env python3
"""
测试null字节修复
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_import():
    """测试导入是否正常"""
    try:
        print("=== 测试导入 ===")
        
        # 测试LLMFixer导入
        from agents.fix_execution_agent.llm_utils import LLMFixer
        print("✅ LLMFixer导入成功")
        
        # 测试FixExecutionAgent导入
        from agents.fix_execution_agent.agent import FixExecutionAgent
        print("✅ FixExecutionAgent导入成功")
        
        # 测试coordinator导入
        from coordinator.coordinator import Coordinator
        print("✅ Coordinator导入成功")
        
        # 创建实例测试
        coordinator = Coordinator()
        print("✅ Coordinator实例创建成功")
        
        print("\n🎉 所有导入测试通过！null字节问题已修复！")
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_import()
    if success:
        print("\n✅ 现在可以运行: python tests/run_coordinator_demo.py")
    else:
        print("\n❌ 还需要进一步修复...")


