# 只测试一个格式不规范的 Python 文件 main.py

test_task = {
    "task_id": "test001",
    "file_path": "agents/fix_execution_agent/main.py",  # 用于推断 project_path
    "issues_by_priority": {
        "high": [
            {"language": "python", "file": "main.py", "type": "format", "message": "格式化问题"}
        ]
    }
}


import asyncio
from agents.fix_execution_agent.agent import FixExecutionAgent

async def main():
    agent = FixExecutionAgent(config={})
    result = await agent.process_task(test_task)
    print("\n=== 修复结果 ===")
    print(result)
    print("\n=== 修复摘要 ===")
    print(await agent.get_fix_summary(result))

if __name__ == "__main__":
    asyncio.run(main())