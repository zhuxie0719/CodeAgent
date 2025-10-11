#!/usr/bin/env python3
"""
正确的测试验证脚本 - 测试修复后的文件
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents', 'test_validation_agent'))

from ai_test_generator import AITestGenerator

def test_correct_file():
    """测试修复后的文件"""
    print("=== 测试修复后的文件 ===")
    
    # 正确的文件路径 - 修复后的文件
    target_file = "tests/output/test_python_bad_after.py"
    
    if not os.path.exists(target_file):
        print(f"❌ 文件不存在: {target_file}")
        return False
    
    print(f"✅ 找到目标文件: {target_file}")
    
    # 创建测试生成器
    generator = AITestGenerator()
    
    try:
        # 生成测试
        print("\n🔧 开始生成测试...")
        result = generator.generate_tests(target_file)
        
        if result:
            print("✅ 测试生成成功!")
            print(f"📁 测试文件位置: {result}")
            
            # 检查生成的测试文件
            if os.path.exists(result):
                print(f"✅ 测试文件已创建: {result}")
                
                # 读取测试文件内容
                with open(result, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"📄 测试文件大小: {len(content)} 字符")
                    print(f"📄 测试文件行数: {len(content.splitlines())} 行")
                    
                    # 显示前几行
                    lines = content.splitlines()
                    print("\n📋 测试文件前10行:")
                    for i, line in enumerate(lines[:10], 1):
                        print(f"{i:2d}| {line}")
                    
                    if len(lines) > 10:
                        print(f"... 还有 {len(lines) - 10} 行")
                
                return True
            else:
                print(f"❌ 测试文件未创建: {result}")
                return False
        else:
            print("❌ 测试生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 生成测试时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 开始正确的测试验证...")
    
    success = test_correct_file()
    
    if success:
        print("\n🎉 测试验证完成!")
    else:
        print("\n💥 测试验证失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()