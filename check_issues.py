#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

project_root = Path('.')
sys.path.insert(0, str(project_root))
from agents.bug_detection_agent.agent import BugDetectionAgent

async def check_detection():
    config = {
        'enabled': True,
        'max_files_per_project': 100,
        'max_file_size': 1024*1024,
        'supported_languages': ['python', 'java', 'c', 'cpp', 'javascript', 'go'],
        'detection_rules': {
            'unused_imports': True,
            'hardcoded_secrets': True,
            'unsafe_eval': True,
            'missing_type_hints': True,
            'long_functions': True,
            'duplicate_code': True,
        }
    }
    
    agent = BugDetectionAgent(config)
    await agent.start()
    await agent._initialize_detection_tools()
    
    result = await agent.analyze_project('flask_simple_test', {
        'enable_static': True,
        'enable_pylint': True,
        'enable_flake8': True,
        'enable_bandit': True,
        'enable_mypy': True,
        'enable_ai_analysis': True,
        'enable_dynamic': True
    })
    
    print(f"总问题数: {result['detection_results']['total_issues']}")
    print(f"检测工具: {result['detection_results']['detection_tools']}")
    
    tool_stats = {}
    for issue in result['detection_results']['issues']:
        tool = issue.get('detection_tool', 'unknown')
        tool_stats[tool] = tool_stats.get(tool, 0) + 1
    
    print("\n按工具统计:")
    for tool, count in sorted(tool_stats.items()):
        print(f"  {tool}: {count}个问题")
    
    await agent.stop()

if __name__ == "__main__":
    asyncio.run(check_detection())


