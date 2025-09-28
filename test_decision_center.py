#!/usr/bin/env python3
"""
协调中心测试脚本
只测试协调中心的核心功能，不依赖其他Agent
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent))

async def test_coordinator_basic():
    """测试协调中心基本功能"""
    print("🚀 开始测试协调中心基本功能")
    print("=" * 50)
    
    try:
        # 导入协调中心组件
        from coordinator import Coordinator, DecisionEngine, TaskManager, EventBus, TaskPriority
        from coordinator.message_types import EventType
        print("✅ 协调中心组件导入成功")
        
        # 创建测试配置
        config = {
            "coordinator": {"max_concurrent_tasks": 3},
            "task_manager": {"max_concurrent_tasks": 3, "task_timeout": 30},
            "event_bus": {"max_queue_size": 100},
            "decision_engine": {"ai_api_key": "test"}
        }
        
        # 1. 测试决策引擎
        print("\n=== 1. 测试决策引擎 ===")
        decision_engine = DecisionEngine(config["decision_engine"])
        
        # 模拟缺陷数据
        mock_issues = [
            {"type": "unused_imports", "severity": "low", "description": "未使用的导入"},
            {"type": "hardcoded_secrets", "severity": "high", "description": "硬编码密钥"},
            {"type": "long_functions", "severity": "medium", "description": "函数过长"}
        ]
        
        # 测试复杂度分析
        complexity_result = await decision_engine.analyze_complexity(mock_issues)
        print(f"✅ 复杂度分析完成:")
        print(f"   - 简单缺陷: {len(complexity_result.get('auto_fixable', []))} 个")
        print(f"   - 中等缺陷: {len(complexity_result.get('ai_assisted', []))} 个")
        print(f"   - 复杂缺陷: {len(complexity_result.get('manual_review', []))} 个")
        
        # 2. 测试任务管理器
        print("\n=== 2. 测试任务管理器 ===")
        task_manager = TaskManager(config["task_manager"])
        await task_manager.start()
        
        # 创建任务
        task_id = await task_manager.create_task(
            task_type="test_task",
            task_data={"test": "data"},
            priority=TaskPriority.NORMAL
        )
        print(f"✅ 任务创建成功: {task_id}")
        
        # 分配任务
        await task_manager.assign_task(task_id, "test_agent")
        print("✅ 任务分配成功")
        
        # 更新任务结果
        await task_manager.update_task_result(task_id, {"success": True, "result": "test_completed"})
        print("✅ 任务结果更新成功")
        
        # 获取任务结果
        result = await task_manager.get_task_result(task_id)
        print(f"✅ 任务结果获取成功: {result}")
        
        await task_manager.stop()
        
        # 3. 测试事件总线
        print("\n=== 3. 测试事件总线 ===")
        event_bus = EventBus(config["event_bus"])
        await event_bus.start()
        
        # 测试事件发布和订阅
        received_events = []
        
        async def event_handler(event_data):
            received_events.append(event_data)
            # 修复：EventMessage对象没有get方法，直接访问属性
            if hasattr(event_data, 'payload') and isinstance(event_data.payload, dict):
                message = event_data.payload.get('message', 'no message')
            else:
                message = 'no message'
            print(f"✅ 收到事件: {message}")
        
        # 订阅事件
        await event_bus.subscribe(EventType.TASK_CREATED.value, "test_subscriber", event_handler)
        print("✅ 事件订阅成功")
        
        # 发布事件
        await event_bus.publish(EventType.TASK_CREATED.value, {"message": "测试事件"}, "test_publisher")
        print("✅ 事件发布成功")
        
        # 等待事件处理
        await asyncio.sleep(0.1)
        
        await event_bus.stop()
        
        # 4. 测试协调中心整体
        print("\n=== 4. 测试协调中心整体 ===")
        coordinator = Coordinator(config)
        await coordinator.start()
        print("✅ 协调中心启动成功")
        
        # 测试创建任务
        coord_task_id = await coordinator.create_task(
            task_type="test_coordinator_task",
            task_data={"project_path": "/test/project"},
            priority=TaskPriority.HIGH
        )
        print(f"✅ 协调中心任务创建成功: {coord_task_id}")
        
        # 获取统计信息
        stats = await coordinator.get_stats()
        print(f"✅ 协调中心统计信息获取成功")
        print(f"   - 注册的Agent数量: {len(stats.get('registered_agents', []))}")
        print(f"   - 完成的工作流数量: {stats.get('workflows_completed', 0)}")
        
        await coordinator.stop()
        
        print("\n" + "=" * 50)
        print("🎉 所有基本功能测试通过！")
        print("✅ 决策引擎: 正常")
        print("✅ 任务管理器: 正常")
        print("✅ 事件总线: 正常")
        print("✅ 协调中心: 正常")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_decision_engine_detailed():
    """详细测试决策引擎功能"""
    print("\n🔍 详细测试决策引擎")
    print("=" * 30)
    
    try:
        from coordinator import DecisionEngine
        
        config = {"ai_api_key": "test", "confidence_threshold": 0.8}
        decision_engine = DecisionEngine(config)
        
        # 测试不同类型的缺陷
        test_issues = [
            {"type": "unused_imports", "severity": "low", "file": "test.py", "line": 5},
            {"type": "bad_formatting", "severity": "low", "file": "test.py", "line": 10},
            {"type": "magic_numbers", "severity": "medium", "file": "test.py", "line": 15},
            {"type": "long_functions", "severity": "medium", "file": "test.py", "line": 20},
            {"type": "hardcoded_secrets", "severity": "high", "file": "config.py", "line": 5},
            {"type": "memory_leaks", "severity": "high", "file": "main.py", "line": 25}
        ]
        
        # 分析复杂度
        result = await decision_engine.analyze_complexity(test_issues)
        
        print("📊 决策引擎分析结果:")
        for category, issues in result.items():
            if issues and isinstance(issues, list):
                print(f"\n{category.upper()}:")
                for issue in issues:
                    if isinstance(issue, dict):
                        print(f"  - {issue.get('type', 'unknown')}: {issue.get('description', 'no description')}")
        
        # 测试修复策略选择
        print("\n🔧 修复策略选择:")
        for issue in test_issues:
            strategy = await decision_engine.select_fix_strategy(issue)
            print(f"  {issue['type']} -> {strategy}")
        
        # 测试风险评估
        # 注意：evaluate_risk需要修复计划，不是缺陷列表
        mock_fix_plan = {
            "type": "auto_format",
            "file_path": "test.py",
            "changes_count": 3
        }
        risk_score = await decision_engine.evaluate_risk(mock_fix_plan)
        print(f"\n⚠️ 风险评估:")
        print(f"  修复风险分数: {risk_score:.2f}")
        print(f"  风险等级: {'低' if risk_score < 0.3 else '中' if risk_score < 0.6 else '高'}")
        
        print("✅ 决策引擎详细测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 决策引擎详细测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🎯 协调中心简单测试")
    print("=" * 60)
    
    # 基本功能测试
    basic_success = await test_coordinator_basic()
    
    # 详细决策引擎测试
    decision_success = await test_decision_engine_detailed()
    
    # 总结
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    print(f"✅ 基本功能测试: {'通过' if basic_success else '失败'}")
    print(f"✅ 决策引擎测试: {'通过' if decision_success else '失败'}")
    
    if basic_success and decision_success:
        print("\n🎉 恭喜！你的协调中心工作正常！")
        print("\n📝 下一步建议:")
        print("1. 让其他同学修改他们的Agent继承BaseAgent")
        print("2. 测试完整的Agent集成")
        print("3. 测试真实的工作流程")
    else:
        print("\n⚠️ 部分测试失败，需要检查问题")
    
    return basic_success and decision_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
