#!/usr/bin/env python3
"""
简单验证测试 - 不调用API
"""

import os
import sys

# 禁用日志
import logging
logging.disable(logging.CRITICAL)

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents', 'test_validation_agent'))

def test_basic_functionality():
    """测试基本功能"""
    try:
        print("导入AI测试生成器...")
        from ai_test_generator import AITestGenerator
        
        print("创建生成器实例...")
        generator = AITestGenerator()
        
        print(f"✅ API密钥: {'已设置' if generator.api_key else '未设置'}")
        print(f"✅ 基础URL: {generator.base_url}")
        print(f"✅ 模型: {generator.model}")
        
        # 检查目标文件
        target_file = "tests/output/test_python_bad_after.py"
        if not os.path.exists(target_file):
            print(f"❌ 目标文件不存在: {target_file}")
            return False
            
        print(f"✅ 目标文件存在: {target_file}")
        
        # 读取文件内容
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"✅ 文件大小: {len(content)} 字符")
            print(f"✅ 文件行数: {len(content.splitlines())} 行")
        
        # 检查文件内容
        if "def bad_function" in content:
            print("✅ 找到目标函数: bad_function")
        else:
            print("❌ 未找到目标函数")
            
        if "def good_function" in content:
            print("✅ 找到目标函数: good_function")
        else:
            print("❌ 未找到目标函数")
        
        print("\n📋 文件前10行:")
        lines = content.splitlines()
        for i, line in enumerate(lines[:10], 1):
            print(f"{i:2d}| {line}")
        
        print("\n✅ 基本功能验证完成!")
        return True
        
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 开始基本功能验证...")
    
    success = test_basic_functionality()
    
    if success:
        print("\n🎉 验证成功!")
    else:
        print("\n💥 验证失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()


