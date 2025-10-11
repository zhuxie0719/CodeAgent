"""
测试AI测试生成功能的演示脚本
"""
import asyncio
import os
import sys
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.test_validation_agent.ai_test_generator import AITestGenerator
from agents.test_validation_agent.mock_ai_test_generator import MockAITestGenerator

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_ai_generation():
    """测试AI测试生成功能"""
    
    # 检查API密钥
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("⚠️ 未设置DEEPSEEK_API_KEY环境变量，使用Mock生成器进行演示")
        generator = MockAITestGenerator()
    else:
        print("🤖 使用真实AI测试生成器")
        generator = AITestGenerator(api_key=api_key)
    
    print("🤖 AI测试生成功能演示")
    print("=" * 50)
    
    # 测试文件路径
    test_file = "tests/test_python_bad.py"
    project_path = "."
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return
    
    print(f"📄 源代码文件: {test_file}")
    print(f"📁 项目路径: {project_path}")
    print()
    
    # 生成测试文件
    print("🚀 开始生成测试文件...")
    result = await generator.generate_test_file(test_file, project_path)
    
    if result["success"]:
        print("✅ 测试文件生成成功!")
        print(f"📝 生成的测试文件: {result['test_file_path']}")
        print()
        
        # 显示生成的测试内容
        print("📋 生成的测试内容:")
        print("-" * 50)
        print(result["test_content"])
        print("-" * 50)
        
        # 询问是否保留文件
        keep_file = input("\n是否保留生成的测试文件? (y/n): ").lower().strip()
        if keep_file != 'y':
            await generator.cleanup_test_file(result["test_file_path"])
            print("🧹 已清理生成的测试文件")
        else:
            print("💾 测试文件已保留")
    else:
        print("❌ 测试文件生成失败!")
        print(f"错误信息: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_ai_generation())

