#!/usr/bin/env python3
"""
测试BugDetectionAgent的工具初始化
"""
import sys
import os
import asyncio

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_agent_tool_init():
    """测试Agent工具初始化"""
    try:
        print("开始测试BugDetectionAgent工具初始化...")
        
        from agents.bug_detection_agent.agent import BugDetectionAgent
        
        # 创建agent
        config = {}
        agent = BugDetectionAgent(config)
        
        print("Agent创建成功")
        print(f"初始状态 - pylint_tool: {agent.pylint_tool}")
        print(f"初始状态 - flake8_tool: {agent.flake8_tool}")
        
        # 调用初始化
        print("\n开始初始化...")
        result = await agent.initialize()
        print(f"初始化结果: {result}")
        
        print(f"初始化后 - pylint_tool: {agent.pylint_tool}")
        print(f"初始化后 - flake8_tool: {agent.flake8_tool}")
        
        # 测试工具调用
        if agent.pylint_tool:
            print("\n测试Pylint工具...")
            test_file = "tests/test_python_bad.py"
            result = await agent.pylint_tool.analyze(test_file)
            print(f"Pylint结果: {result}")
        else:
            print("❌ Pylint工具未初始化")
            
        if agent.flake8_tool:
            print("\n测试Flake8工具...")
            test_file = "tests/test_python_bad.py"
            result = await agent.flake8_tool.analyze(test_file)
            print(f"Flake8结果: {result}")
        else:
            print("❌ Flake8工具未初始化")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_tool_init())


