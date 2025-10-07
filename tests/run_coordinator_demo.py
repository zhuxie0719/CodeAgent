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
from config.settings import settings  # noqa: E402


async def main():
    # 0) 启用所需检测工具（配置层）：开启 pylint/flake8，关闭 static_detector
    try:
        if not hasattr(settings, 'TOOLS'):
            settings.TOOLS = {}
        settings.TOOLS.setdefault('pylint', {})['enabled'] = True
        settings.TOOLS.setdefault('flake8', {})['enabled'] = True
        settings.TOOLS.setdefault('static_detector', {})['enabled'] = False
    except Exception:
        pass

    # 1) 启动协调中心
    print("\n================= COORDINATOR BOOT =================")
    coordinator = Coordinator(config={})
    await coordinator.start()
    print("✅ Coordinator 已启动")

    # 2) 启动并注册需要的 Agent（最小集：检测 + 修复）
    print("\n================= AGENTS BOOT & REGISTER ===========")
    bug_agent = BugDetectionAgent(config={})
    await bug_agent.start()
    await coordinator.register_agent('bug_detection_agent', bug_agent)
    print("✅ BugDetectionAgent 已启动并注册")

    # 预留：修复执行Agent（同学功能，暂不参与流程，可随时开启）
    # fix_agent = FixExecutionAgent(config={})
    # await fix_agent.start()
    # await coordinator.register_agent('fix_execution_agent', fix_agent)
    # print("✅ FixExecutionAgent 已启动并注册")

    # 3) 选择待测文件路径（服务器本地路径）
    print("\n================= TEST TARGET =======================")
    test_file = str(CURRENT_DIR / 'test_python_bad.py')
    print(f"📄 测试文件: {test_file}")

    # 4) 创建 detect_bugs 任务并分配给 bug_detection_agent
    # 仅检测：启用 pylint/flake8，关闭 static/ai/bandit/mypy
    print("\n================= DETECT TASK SUBMIT ================")
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
    print(f"🆔 任务已创建: {task_id}")
    await coordinator.assign_task(task_id, 'bug_detection_agent')
    print("📤 已分配到: bug_detection_agent")

    # 5) 等待检测任务完成
    print("\n================= DETECT RESULT =====================")
    detection_result = await coordinator.task_manager.get_task_result(task_id, timeout=600)
    result_ok = detection_result.get('success')
    det = detection_result.get('detection_results', {})
    issues = det.get('issues', [])
    tools = det.get('detection_tools', [])
    print(f"✅ 成功: {result_ok}")
    print(f"🛠️ 使用工具: {', '.join(tools) if tools else '无'}")
    print(f"🐞 缺陷总数: {det.get('total_issues', 0)}")
    if issues:
        print("\nAll Issues:")
        for i, issue in enumerate(issues, start=1):
            loc = f"{issue.get('file','')}:{issue.get('line',0)}:{issue.get('column',0)}"
            sev = issue.get('severity', 'info')
            typ = issue.get('type', issue.get('symbol', 'unknown'))
            msg = issue.get('message', '')
            print(f"  {i:02d}. [{sev}] {typ} @ {loc} - {msg}")
    else:
        print("（未发现问题，若为意外，请确认已安装并启用 pylint/flake8）")

    # 预留：修复与验证编排（同学功能，录屏时可展示注释说明）
    # print("\n================= FIX & VALIDATION (预留) ===========")
    # fix_task_payload = {
    #     'file_path': test_file,
    #     'issues': issues,
    #     'decisions': {'auto_fixable': issues, 'ai_assisted': [], 'manual_review': []}
    # }
    # fix_task_id = await coordinator.create_task('fix_issues', fix_task_payload)
    # await coordinator.assign_task(fix_task_id, 'fix_execution_agent')
    # print(f"🆔 修复任务创建并分配: {fix_task_id} -> fix_execution_agent")
    # fix_result = await coordinator.task_manager.get_task_result(fix_task_id, timeout=900)
    # print("🧩 修复结果摘要:")
    # print({
    #     'success': fix_result.get('success'),
    #     'fixed_issues': len(fix_result.get('fix_results', [])),
    #     'errors': fix_result.get('errors', [])[:3]
    # })

    # 6) 收尾
    print("\n================= SHUTDOWN ===========================")
    await coordinator.stop()
    await bug_agent.stop()
    # if 'fix_agent' in locals():
    #     await fix_agent.stop()
    print("✅ 已退出")


if __name__ == '__main__':
    asyncio.run(main())


