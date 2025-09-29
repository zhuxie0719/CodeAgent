# test_run.py（在 project/CodeAgent 目录下运行）
import asyncio
from config.settings import settings
from coordinator.coordinator import Coordinator
from agents.code_analysis_agent.agent import CodeAnalysisAgent
from agents.bug_detection_agent.agent import BugDetectionAgent
from agents.fix_execution_agent.agent import FixExecutionAgent
from agents.test_validation_agent.agent import TestValidationAgent
from agents.performance_optimization_agent.agent import PerformanceOptimizationAgent
from agents.code_quality_agent.agent import CodeQualityAgent


async def main():
    # 注意：Pydantic 2.x 需 settings.model_dump()
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

    # 提交一个缺陷检测任务（给一个真实存在的项目路径）
    project_path = "."  # 替换为你要扫描的项目目录
    result = await coordinator.process_workflow(project_path)
    print("workflow result:", result)

    await coordinator.stop()


if __name__ == "__main__":
    asyncio.run(main())