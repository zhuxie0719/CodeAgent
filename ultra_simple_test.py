#!/usr/bin/env python3
"""
超简单测试 - 直接测试coordinator.run方法
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_simple():
    """最简单的测试"""
    try:
        from coordinator.coordinator import Coordinator
        
        print("=== 超简单测试 ===")
        
        # 创建coordinator
        coordinator = Coordinator()
        print("✅ Coordinator创建成功")
        
        # 测试文件
        test_file = project_root / "tests" / "test_python_bad.py"
        print(f"📁 测试文件: {test_file}")
        print(f"📁 文件存在: {test_file.exists()}")
        
        if not test_file.exists():
            print("❌ 测试文件不存在!")
            return False
        
        # 直接调用run方法
        print("\n🔍 开始检测...")
        result = coordinator.run(test_file)
        
        print(f"\n📊 检测结果:")
        print(f"  - 问题数量: {len(result.get('issues', []))}")
        print(f"  - 使用工具: {result.get('tools_used', '无')}")
        
        if result.get('issues'):
            print(f"\n✅ 成功! 检测到 {len(result['issues'])} 个问题")
            # 显示前3个问题
            for i, issue in enumerate(result['issues'][:3], 1):
                print(f"  {i}. {issue.get('description', 'N/A')}")
        else:
            print("\n❌ 没有检测到问题")
            
        return len(result.get('issues', [])) > 0
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple()
    print(f"\n🎯 测试结果: {'✅ 成功' if success else '❌ 失败'}")


