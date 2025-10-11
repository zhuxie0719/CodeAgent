#!/usr/bin/env python3
"""
直接测试AI生成器核心功能
"""

import os
import sys
import asyncio

# 禁用所有日志
import logging
logging.disable(logging.CRITICAL)

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents', 'test_validation_agent'))

async def test_ai_generator():
    """测试AI生成器"""
    try:
        print("导入AI测试生成器...")
        from ai_test_generator import AITestGenerator
        
        print("创建生成器实例...")
        generator = AITestGenerator()
        
        print(f"API密钥状态: {'已设置' if generator.api_key else '未设置'}")
        print(f"基础URL: {generator.base_url}")
        print(f"模型: {generator.model}")
        
        # 检查目标文件
        target_file = "tests/output/test_python_bad_after.py"
        if not os.path.exists(target_file):
            print(f"❌ 目标文件不存在: {target_file}")
            return False
            
        print(f"✅ 目标文件存在: {target_file}")
        
        # 读取文件内容
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"文件大小: {len(content)} 字符")
        
        print("开始生成测试...")
        result = await generator.generate_test_file(target_file, ".")
        
        print(f"生成结果: {result}")
        
        if result.get("success"):
            test_file = result.get("test_file_path")
            if test_file and os.path.exists(test_file):
                print(f"✅ 测试文件已创建: {test_file}")
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
    print("🚀 开始测试AI生成器...")
    
    # 运行异步测试
    success = asyncio.run(test_ai_generator())
    
    if success:
        print("\n🎉 测试成功!")
    else:
        print("\n💥 测试失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()


