#!/usr/bin/env python3
"""
简单测试脚本 - 验证coordinator修复
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_coordinator():
    """测试coordinator是否能正常工作"""
    try:
        print("=== 测试Coordinator修复 ===")
        
        # 导入coordinator
        from coordinator.coordinator import Coordinator
        print("✅ Coordinator导入成功")
        
        # 创建coordinator实例
        coordinator = Coordinator()
        print("✅ Coordinator创建成功")
        
        # 检查测试文件
        test_file = project_root / "tests" / "test_python_bad.py"
        print(f"📁 测试文件: {test_file}")
        print(f"📁 文件存在: {test_file.exists()}")
        
        if not test_file.exists():
            print("❌ 测试文件不存在!")
            return False
        
        # 读取测试文件内容
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 文件内容长度: {len(content)} 字符")
        print(f"📄 包含API_KEY: {'API_KEY' in content}")
        print(f"📄 包含eval: {'eval(' in content}")
        print(f"📄 包含除零: {'a / b' in content}")
        
        # 运行检测
        print("\n🔍 开始检测...")
        result = coordinator.run(test_file)
        
        print(f"\n📊 检测结果:")
        print(f"  - 问题数量: {len(result.get('issues', []))}")
        print(f"  - 使用工具: {result.get('tools_used', '无')}")
        print(f"  - 检测时间: {result.get('detection_time', 'N/A')}")
        
        if result.get('issues'):
            print(f"\n✅ 成功! 检测到 {len(result['issues'])} 个问题")
            print("\n📋 问题列表:")
            for i, issue in enumerate(result['issues'][:5], 1):  # 显示前5个问题
                print(f"  {i}. {issue.get('description', 'N/A')}")
                print(f"     类型: {issue.get('type', 'N/A')}")
                print(f"     行号: {issue.get('line', 'N/A')}")
                print()
        else:
            print("\n❌ 没有检测到问题")
            
        return len(result.get('issues', [])) > 0
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_coordinator()
    print(f"\n🎯 测试结果: {'✅ 成功' if success else '❌ 失败'}")
    if success:
        print("🎉 Coordinator修复成功！现在可以正常检测代码问题了。")
    else:
        print("😞 还需要进一步调试...")