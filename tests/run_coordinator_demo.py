import asyncio
import sys
from pathlib import Path


# 将项目根路径加入 sys.path，便于模块导入
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


from coordinator.coordinator import Coordinator  # noqa: E402
from agents.bug_detection_agent.agent import BugDetectionAgent  # noqa: E402
from agents.fix_execution_agent.agent import FixExecutionAgent  # noqa: E402


async def main():
    # 1) 启动协调中心
    coordinator = Coordinator(config={})
    await coordinator.start()

    # 2) 启动并注册需要的 Agent（最小集：检测 + 修复）
    bug_agent = BugDetectionAgent(config={})
    fix_agent = FixExecutionAgent(config={})
    await bug_agent.start()
    await fix_agent.start()
    await coordinator.register_agent('bug_detection_agent', bug_agent)
    await coordinator.register_agent('fix_execution_agent', fix_agent)

    # 3) 选择待测文件路径（服务器本地路径）
    test_file = str(CURRENT_DIR / 'test_python_bad.py')

    # 4) 创建 detect_bugs 任务并分配给 bug_detection_agent
    # 注意：如果 StaticDetector 未实现，请将 enable_static 置为 False
    task_payload = {
        'file_path': test_file,
        'options': {
            'enable_static': False,
            'enable_pylint': True,
            'enable_flake8': True,
            'enable_bandit': False,
            'enable_mypy': False,
            'enable_ai_analysis': False
        }
    }
    task_id = await coordinator.create_task('detect_bugs', task_payload)
    await coordinator.assign_task(task_id, 'bug_detection_agent')

    # 5) 等待检测任务完成
    detection_result = await coordinator.task_manager.get_task_result(task_id, timeout=600)
    print('\n=== Detection Result ===')
    print(detection_result)

    # 6) 收尾
    await coordinator.stop()
    await bug_agent.stop()
    await fix_agent.stop()


if __name__ == '__main__':
    asyncio.run(main())


