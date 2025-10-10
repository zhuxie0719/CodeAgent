# test_run.py（在 project/CodeAgent 目录下运行） - 支持智能文件/目录检测
import asyncio
from pathlib import Path
from config.settings import settings
from coordinator.coordinator import Coordinator
from agents.code_analysis_agent.agent import CodeAnalysisAgent
from agents.bug_detection_agent.agent import BugDetectionAgent
from agents.fix_execution_agent.agent import FixExecutionAgent
from agents.test_validation_agent.agent import TestValidationAgent
from agents.performance_optimization_agent.agent import PerformanceOptimizationAgent
from agents.code_quality_agent.agent import CodeQualityAgent


async def run_workflow(target_path: str):
    """运行工作流，支持单文件和目录检测"""
    cfg = settings.model_dump()
    coordinator = Coordinator(cfg)

    agents = {
        'code_analysis_agent': CodeAnalysisAgent(settings.AGENTS['code_analysis_agent']),
        'bug_detection_agent': BugDetectionAgent(settings.AGENTS['bug_detection_agent']),
        'fix_execution_agent': FixExecutionAgent(settings.AGENTS['fix_execution_agent']),
        'test_validation_agent': TestValidationAgent(settings.AGENTS['test_validation_agent']),
        'performance_optimization_agent': PerformanceOptimizationAgent(settings.AGENTS['performance_optimization_agent']),
        'code_quality_agent': CodeQualityAgent(settings.AGENTS['code_quality_agent'])
    }

    for aid, agent in agents.items():
        await coordinator.register_agent(aid, agent)

    await coordinator.start()
    
    # 智能检测路径类型
    path = Path(target_path)
    if path.is_file():
        print(f"\n📄 智能检测：单文件模式")
        print(f"--- 开始处理单文件: {target_path} ---")
    elif path.is_dir():
        print(f"\n📁 智能检测：项目模式")
        print(f"--- 开始处理项目目录: {target_path} ---")
    else:
        print(f"\n❓ 未知路径类型: {target_path}")
        print(f"--- 尝试默认处理 ---")
    
    result = await coordinator.process_workflow(target_path)
    
    print("--- 工作流结果 ---")
    print(f"  成功: {result.get('success', False)}")
    print(f"  消息: {result.get('message', 'N/A')}")
    
    if 'detection_result' in result:
        detection = result['detection_result']
        print(f"  检测成功: {detection.get('success', False)}")
        print(f"  任务ID: {detection.get('task_id', 'N/A')}")
        print(f"  总问题数: {detection.get('summary', {}).get('total_issues', 0)}")
    
    if 'summary' in result:
        summary = result['summary']
        print(f"  总问题数 (汇总): {summary.get('total_issues', 0)}")
        print(f"  修复问题数: {summary.get('fixed_issues', 0)}")
        print(f"  处理时间: {summary.get('processing_time', 0):.3f} 秒")

    await coordinator.stop()
    return result


async def test_single_file():
    """测试单文件检测"""
    print("\n=== 🧪 测试单文件检测 ===")
    return await run_workflow("tests/test_python_bad.py")


async def test_directory():
    """测试目录检测"""
    print("\n=== 🧪 测试目录检测 ===")
    return await run_workflow("tests")


async def main():
    """主测试函数"""
    print("🎯 Coordinator 到 BugDetectionAgent 连通性测试")
    print("=" * 60)
    print("现在 Coordinator 支持智能检测和传递正确的参数给 BugDetectionAgent")
    print()

    try:
        # 确保测试文件存在
        test_file = Path("tests/test_python_bad.py")
        if not test_file.exists():
            print("📝 创建测试文件...")
            test_file.parent.mkdir(exist_ok=True)
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write("""
# test_python_bad.py - 有问题的Python代码示例
import os  # 未使用导入
x = 1  # 魔法数字
if True:print("格式问题")  # 缺少空格
""")
            print(f"✅ 已创建: {test_file}")

        # 测试单文件检测
        print(f"\n🔍 测试1: 单文件检测")
        file_result = await test_single_file()
        
        # 测试目录检测
        print(f"\n🔍 测试2: 目录检测")
        dir_result = await test_directory()
        
        # 结果对比
        print("\n📈 连通性测试结果对比")
        print("=" * 40)
        file_issues = file_result.get('summary', {}).get('total_issues', 0)
        dir_issues = dir_result.get('summary', {}).get('total_issues', 0)
        
        print(f"单文件检测问题数: {file_issues}")
        print(f"目录检测问题数:   {dir_issues}")
        
        if file_issues > 0 or dir_issues > 0:
            print("\n✅ Coordinator ↔ BugDetectionAgent 连通性测试成功!")
            print("💡 Coordinator 现在能够:")
            print("  - 自动检测路径类型（文件/目录）")
            print("  - 传递正确的参数（file_path/project_path）")
            print("  - BugDetectionAgent 正确接收并处理")
            print("  - 返回有效的检测结果")
        else:
            print("\n⚠️  连通性成功但未检测到问题")
            print("  这可能是因为测试文件中没有足够的问题")
            
    except Exception as e:
        print(f"❌ 连通性测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())