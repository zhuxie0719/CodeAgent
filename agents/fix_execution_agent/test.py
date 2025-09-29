# 测试 JavaScript 格式化

test_task = {
    "task_id": "test_js_001",
    "file_path": "main.js",
    "issues_by_priority": {
        "high": [
            {"language": "javascript", "file": "main.js", "type": "format", "message": "格式化问题"}
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