#!/usr/bin/env python3
"""
无日志测试脚本
"""

import os
import sys

# 禁用日志
import logging
logging.disable(logging.CRITICAL)

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents', 'test_validation_agent'))

def test_without_logging():
    """无日志测试"""
    try:
        print("导入模块...")
        from ai_test_generator import AITestGenerator
        
        print("创建生成器...")
        generator = AITestGenerator()
        
        print("检查API配置...")
        if not generator.api_key:
            print("❌ 没有API密钥")
            return False
            
        print("✅ API配置正常")
        
        print("检查目标文件...")
        target_file = "tests/output/test_python_bad_after.py"
        
        if not os.path.exists(target_file):
            print(f"❌ 文件不存在: {target_file}")
            return False
            
        print("✅ 目标文件存在")
        
        print("尝试生成测试...")
        result = generator.generate_tests(target_file)
        
        if result:
            print(f"✅ 生成成功: {result}")
            if os.path.exists(result):
                print("✅ 测试文件已创建")
                return True
            else:
                print("❌ 测试文件未创建")
                return False
        else:
            print("❌ 生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    success = test_without_logging()
    if success:
        print("\n🎉 测试完成!")
    else:
        print("\n💥 测试失败!")
        sys.exit(1)


