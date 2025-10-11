#!/usr/bin/env python3
"""
测试AI测试生成功能的集成
"""
import os
import sys
import asyncio

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

async def test_ai_integration():
    """测试AI集成功能"""
    print("🧪 测试AI测试生成功能集成")
    
    try:
        # 测试导入现有配置
        from api.deepseek_config import deepseek_config
        print(f"✅ 成功导入DeepSeek配置")
        print(f"🔑 API密钥状态: {'已配置' if deepseek_config.is_configured() else '未配置'}")
        if deepseek_config.is_configured():
            print(f"🔗 API密钥: {deepseek_config.api_key[:10]}...{deepseek_config.api_key[-10:]}")
            print(f"🌐 基础URL: {deepseek_config.base_url}")
            print(f"🤖 模型: {deepseek_config.model}")
            print(f"📊 最大Token: {deepseek_config.max_tokens}")
            print(f"🌡️ 温度: {deepseek_config.temperature}")
        
        # 测试AI测试生成器
        from agents.test_validation_agent.ai_test_generator import AITestGenerator
        print(f"\n🤖 测试AI测试生成器初始化...")
        
        generator = AITestGenerator()
        print(f"✅ AI测试生成器初始化成功")
        print(f"🔑 生成器API密钥: {'已配置' if generator.api_key else '未配置'}")
        print(f"🌐 生成器基础URL: {generator.base_url}")
        print(f"🤖 生成器模型: {generator.model}")
        
        # 测试模拟生成器
        from agents.test_validation_agent.mock_ai_test_generator import MockAITestGenerator
        print(f"\n🎭 测试模拟AI测试生成器...")
        
        mock_generator = MockAITestGenerator()
        print(f"✅ 模拟AI测试生成器初始化成功")
        
        # 测试生成测试文件
        test_file = "tests/test_simple.py"
        if os.path.exists(test_file):
            print(f"\n📝 测试生成测试文件: {test_file}")
            result = await mock_generator.generate_test_file(test_file, "tests")
            print(f"📊 生成结果: {result}")
            
            if result.get("success"):
                print(f"✅ 测试文件生成成功: {result.get('test_file_path')}")
                # 清理测试文件
                if result.get("test_file_path") and os.path.exists(result["test_file_path"]):
                    os.remove(result["test_file_path"])
                    print(f"🧹 已清理测试文件")
            else:
                print(f"❌ 测试文件生成失败: {result.get('error')}")
        else:
            print(f"⚠️ 测试文件不存在: {test_file}")
        
        print(f"\n🎉 AI集成测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ai_integration())

