#!/usr/bin/env python3
"""
使用模拟AI测试生成器创建测试
"""

import os
import sys
import asyncio

# 禁用日志
import logging
logging.disable(logging.CRITICAL)

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents', 'test_validation_agent'))

async def test_with_mock_generator():
    """使用模拟生成器测试"""
    try:
        print("导入模拟AI测试生成器...")
        from mock_ai_test_generator import MockAITestGenerator
        
        print("创建模拟生成器实例...")
        generator = MockAITestGenerator()
        
        # 检查目标文件
        target_file = "tests/output/test_python_bad_after.py"
        if not os.path.exists(target_file):
            print(f"❌ 目标文件不存在: {target_file}")
            return False
            
        print(f"✅ 目标文件存在: {target_file}")
        
        print("开始生成测试...")
        result = await generator.generate_test_file(target_file, ".")
        
        print(f"生成结果: {result}")
        
        if result.get("success"):
            test_file = result.get("test_file_path")
            if test_file and os.path.exists(test_file):
                print(f"✅ 测试文件已创建: {test_file}")
                
                # 读取测试文件内容
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"📄 测试文件大小: {len(content)} 字符")
                    print(f"📄 测试文件行数: {len(content.splitlines())} 行")
                
                # 显示测试文件的前20行
                lines = content.splitlines()
                print("\n📋 测试文件前20行:")
                for i, line in enumerate(lines[:20], 1):
                    print(f"{i:2d}| {line}")
                
                if len(lines) > 20:
                    print(f"... 还有 {len(lines) - 20} 行")
                
                return True
            else:
                print(f"❌ 测试文件未创建: {test_file}")
                return False
        else:
            print(f"❌ 生成失败: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 开始使用模拟AI生成器测试...")
    
    # 运行异步测试
    success = asyncio.run(test_with_mock_generator())
    
    if success:
        print("\n🎉 测试成功!")
    else:
        print("\n💥 测试失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()


