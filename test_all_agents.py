#!/usr/bin/env python3
"""
测试所有Agent的导入和基本功能
"""

import asyncio
from datetime import datetime

def test_agent_imports():
    """测试所有Agent的导入"""
    print("=== 测试Agent导入情况 ===\n")
    
    # 测试基类
    try:
        from agents import BaseAgent, AgentStatus, TaskStatus
        print("✅ BaseAgent, AgentStatus, TaskStatus 导入成功")
    except Exception as e:
        print(f"❌ 基类导入失败: {e}")
    
    print()
    
    # 测试各个Agent
    agents_to_test = [
        "BugDetectionAgent",
        "FixExecutionAgent", 
        "TestValidationAgent",
        "CodeAnalysisAgent",
        "CodeQualityAgent",
        "PerformanceOptimizationAgent"
    ]
    
    successful_imports = []
    failed_imports = []
    
    for agent_name in agents_to_test:
        try:
            exec(f"from agents import {agent_name}")
            print(f"✅ {agent_name} 导入成功")
            successful_imports.append(agent_name)
        except Exception as e:
            print(f"❌ {agent_name} 导入失败: {e}")
            failed_imports.append(agent_name)
    
    print(f"\n=== 导入结果统计 ===")
    print(f"✅ 成功导入: {len(successful_imports)} 个Agent")
    print(f"❌ 导入失败: {len(failed_imports)} 个Agent")
    
    return successful_imports, failed_imports

def test_agent_instantiation(successful_imports):
    """测试Agent的实例化"""
    print(f"\n=== 测试Agent实例化 ===")
    
    # 模拟配置
    config = {
        "debug": True,
        "timeout": 30,
        "max_retries": 3
    }
    
    instantiated_agents = []
    
    for agent_name in successful_imports:
        try:
            # 动态导入并实例化Agent
            exec(f"from agents import {agent_name}")
            exec(f"agent = {agent_name}(config)")
            exec(f"print(f'✅ {agent_name} 实例化成功')")
            instantiated_agents.append(agent_name)
        except Exception as e:
            exec(f"print(f'❌ {agent_name} 实例化失败: {e}')")
    
    print(f"\n=== 实例化结果统计 ===")
    print(f"✅ 成功实例化: {len(instantiated_agents)} 个Agent")
    
    return instantiated_agents

def test_baseagent_inheritance(successful_imports):
    """测试Agent是否继承BaseAgent"""
    print(f"\n=== 测试BaseAgent继承 ===")
    
    from agents import BaseAgent
    
    inherited_agents = []
    not_inherited_agents = []
    
    for agent_name in successful_imports:
        try:
            exec(f"from agents import {agent_name}")
            exec(f"agent_class = {agent_name}")
            exec(f"is_baseagent = issubclass(agent_class, BaseAgent)")
            
            if eval(f"issubclass({agent_name}, BaseAgent)"):
                print(f"✅ {agent_name} 继承了BaseAgent")
                inherited_agents.append(agent_name)
            else:
                print(f"❌ {agent_name} 没有继承BaseAgent")
                not_inherited_agents.append(agent_name)
        except Exception as e:
            print(f"❌ {agent_name} 继承检查失败: {e}")
            not_inherited_agents.append(agent_name)
    
    print(f"\n=== 继承结果统计 ===")
    print(f"✅ 继承BaseAgent: {len(inherited_agents)} 个Agent")
    print(f"❌ 未继承BaseAgent: {len(not_inherited_agents)} 个Agent")
    
    return inherited_agents, not_inherited_agents

def test_coordinator_import():
    """测试协调中心的导入"""
    print(f"\n=== 测试协调中心导入 ===")
    
    try:
        from coordinator import Coordinator, TaskManager, EventBus, DecisionEngine
        print("✅ 协调中心组件导入成功")
        
        # 测试消息类型
        from coordinator import MessageType, TaskStatus, EventType, TaskPriority
        print("✅ 消息类型导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 协调中心导入失败: {e}")
        return False

async def test_coordinator_basic():
    """测试协调中心基本功能"""
    print(f"\n=== 测试协调中心基本功能 ===")
    
    try:
        from coordinator import Coordinator
        
        # 创建配置
        config = {
            "coordinator": {
                "max_concurrent_tasks": 5,
                "task_timeout": 300,
                "retry_attempts": 3
            },
            "task_manager": {
                "max_concurrent_tasks": 5,
                "task_timeout": 300,
                "retry_attempts": 3
            },
            "event_bus": {
                "max_queue_size": 1000,
                "message_timeout": 30,
                "retry_attempts": 3
            },
            "decision_engine": {
                "ai_api_key": "test_key",
                "ai_model": "gpt-3.5-turbo",
                "max_tokens": 1000
            }
        }
        
        # 创建协调中心
        coordinator = Coordinator(config)
        print("✅ 协调中心创建成功")
        
        # 启动协调中心
        await coordinator.start()
        print("✅ 协调中心启动成功")
        
        # 停止协调中心
        await coordinator.stop()
        print("✅ 协调中心停止成功")
        
        return True
    except Exception as e:
        print(f"❌ 协调中心基本功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试AI Agent系统")
    print("=" * 50)
    
    # 测试Agent导入
    successful_imports, failed_imports = test_agent_imports()
    
    if successful_imports:
        # 测试Agent实例化
        instantiated_agents = test_agent_instantiation(successful_imports)
        
        # 测试BaseAgent继承
        inherited_agents, not_inherited_agents = test_baseagent_inheritance(successful_imports)
    
    # 测试协调中心
    coordinator_ok = test_coordinator_import()
    
    if coordinator_ok:
        # 测试协调中心基本功能
        asyncio.run(test_coordinator_basic())
    
    print("\n" + "=" * 50)
    print("🎯 测试完成")
    
    # 总结
    print(f"\n📊 测试总结:")
    print(f"✅ Agent导入成功: {len(successful_imports)} 个")
    print(f"❌ Agent导入失败: {len(failed_imports)} 个")
    
    if successful_imports:
        print(f"✅ Agent实例化成功: {len(instantiated_agents)} 个")
        print(f"✅ 继承BaseAgent: {len(inherited_agents)} 个")
        print(f"❌ 未继承BaseAgent: {len(not_inherited_agents)} 个")
    
    print(f"✅ 协调中心: {'正常' if coordinator_ok else '异常'}")

if __name__ == "__main__":
    main()
