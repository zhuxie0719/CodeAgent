#!/usr/bin/env python3
"""
简单测试脚本 - 直接测试AI测试生成器
"""

import os
import sys

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents', 'test_validation_agent'))

def simple_test():
    """简单测试"""
    try:
        print("导入模块...")
        from ai_test_generator import AITestGenerator
        
        print("创建生成器...")
        generator = AITestGenerator()
        
        print("生成测试...")
        target_file = "tests/output/test_python_bad_after.py"
        
        if not os.path.exists(target_file):
            print(f"文件不存在: {target_file}")
            return False
            
        result = generator.generate_tests(target_file)
        print(f"结果: {result}")
        
        if result and os.path.exists(result):
            print("✅ 成功!")
            return True
        else:
            print("❌ 失败!")
            return False
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    simple_test()