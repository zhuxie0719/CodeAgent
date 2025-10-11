#!/usr/bin/env python3
"""
详细调试BugDetectionAgent工具初始化
"""
import sys
import os
import asyncio
import logging

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置详细日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def debug_agent_init():
    """详细调试Agent初始化"""
    try:
        print("开始详细调试BugDetectionAgent...")
        
        from agents.bug_detection_agent.agent import BugDetectionAgent, settings
        
        print(f"Settings: {settings}")
        print(f"TOOLS配置: {settings.TOOLS}")
        
        # 创建agent
        config = {}
        agent = BugDetectionAgent(config)
        
        print(f"Agent创建成功")
        print(f"初始状态 - pylint_tool: {agent.pylint_tool}")
        print(f"初始状态 - flake8_tool: {agent.flake8_tool}")
        
        # 手动调用工具初始化
        print("\n开始手动工具初始化...")
        await agent._initialize_detection_tools()
        
        print(f"初始化后 - pylint_tool: {agent.pylint_tool}")
        print(f"初始化后 - flake8_tool: {agent.flake8_tool}")
        
        # 测试工具调用
        test_file = "tests/test_python_bad.py"
        print(f"\n测试文件: {test_file}")
        
        if agent.pylint_tool:
            print("测试Pylint工具...")
            try:
                result = await agent.pylint_tool.analyze(test_file)
                print(f"Pylint结果: {result}")
                if result.get("issues"):
                    print(f"✅ Pylint检测到 {len(result['issues'])} 个问题")
                else:
                    print("⚠️ Pylint没有检测到问题")
            except Exception as e:
                print(f"❌ Pylint调用失败: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ Pylint工具未初始化")
            
        if agent.flake8_tool:
            print("测试Flake8工具...")
            try:
                result = await agent.flake8_tool.analyze(test_file)
                print(f"Flake8结果: {result}")
                if result.get("issues"):
                    print(f"✅ Flake8检测到 {len(result['issues'])} 个问题")
                else:
                    print("⚠️ Flake8没有检测到问题")
            except Exception as e:
                print(f"❌ Flake8调用失败: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ Flake8工具未初始化")
        
        print("\n=== 调试完成 ===")
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_agent_init())


