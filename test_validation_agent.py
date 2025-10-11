#!/usr/bin/env python3
"""
测试验证Agent功能测试脚本
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from agents.test_validation_agent.agent import TestValidationAgent
from config.settings import settings

async def test_validation_agent():
    """测试验证Agent的基本功能"""
    print("🚀 开始测试验证Agent...")
    
    # 创建Agent实例
    config = settings.AGENTS.get('test_validation_agent', {})
    agent = TestValidationAgent(config)
    
    # 启动Agent
    await agent.start()
    print("✅ Agent启动成功")
    
    # 测试项目路径（使用当前项目目录）
    project_path = str(Path(__file__).parent)
    print(f"📁 测试项目路径: {project_path}")
    
    # 测试1: 单元测试
    print("\n🧪 测试1: 单元测试")
    try:
        task_data = {
            "action": "unit",
            "project_path": project_path,
            "options": {
                "generate_with_ai": False,
                "min_coverage": 50
            }
        }
        
        result = await agent.process_task("test_unit_001", task_data)
        print(f"✅ 单元测试结果: {result}")
        
    except Exception as e:
        print(f"❌ 单元测试失败: {e}")
    
    # 测试2: 集成测试
    print("\n🔗 测试2: 集成测试")
    try:
        task_data = {
            "action": "integration",
            "project_path": project_path,
            "options": {}
        }
        
        result = await agent.process_task("test_integration_001", task_data)
        print(f"✅ 集成测试结果: {result}")
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
    
    # 测试3: 性能测试
    print("\n⚡ 测试3: 性能测试")
    try:
        task_data = {
            "action": "performance",
            "project_path": project_path,
            "options": {}
        }
        
        result = await agent.process_task("test_performance_001", task_data)
        print(f"✅ 性能测试结果: {result}")
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
    
    # 测试4: 完整验证（包含AI生成）
    print("\n🎯 测试4: 完整验证（含AI生成）")
    try:
        task_data = {
            "action": "validate",
            "project_path": project_path,
            "options": {
                "generate_with_ai": True,
                "min_coverage": 30
            },
            "fix_result": {
                "summary": "修复了除零错误和SQL注入问题",
                "files_changed": ["test_python_bad.py"]
            }
        }
        
        result = await agent.process_task("test_validate_001", task_data)
        print(f"✅ 完整验证结果: {result}")
        
        # 检查AI生成的文件
        ai_tests_dir = Path(project_path) / "ai_tests"
        if ai_tests_dir.exists():
            print(f"📝 AI测试文件已生成: {list(ai_tests_dir.glob('*'))}")
        
    except Exception as e:
        print(f"❌ 完整验证失败: {e}")
    
    # 测试5: Agent能力查询
    print("\n🔍 测试5: Agent能力查询")
    capabilities = agent.get_capabilities()
    print(f"✅ Agent能力: {capabilities}")
    
    # 测试6: Agent状态查询
    print("\n📊 测试6: Agent状态查询")
    status = agent.get_status()
    print(f"✅ Agent状态: {status}")
    
    # 停止Agent
    await agent.stop()
    print("\n🛑 Agent已停止")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    asyncio.run(test_validation_agent())

