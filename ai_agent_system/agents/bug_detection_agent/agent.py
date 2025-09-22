"""
缺陷检测AGENT主类
"""

import asyncio
from typing import Dict, List, Any, Optional
from .detector import StaticAnalyzer, RuntimeAnalyzer, SecurityAnalyzer


class BugDetectionAgent:
    """缺陷检测AGENT"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.static_analyzer = StaticAnalyzer(config)
        self.runtime_analyzer = RuntimeAnalyzer(config)
        self.security_analyzer = SecurityAnalyzer(config)
        self.is_running = False
    
    async def start(self):
        """启动AGENT"""
        self.is_running = True
        print("缺陷检测AGENT已启动")
    
    async def stop(self):
        """停止AGENT"""
        self.is_running = False
        print("缺陷检测AGENT已停止")
    
    async def detect_bugs(self, project_path: str) -> Dict[str, Any]:
        """检测项目中的缺陷"""
        try:
            # 静态分析
            static_issues = await self.static_analyzer.analyze(project_path)
            
            # 运行时分析
            runtime_issues = await self.runtime_analyzer.analyze(project_path)
            
            # 安全分析
            security_issues = await self.security_analyzer.analyze(project_path)
            
            return {
                'static_issues': static_issues,
                'runtime_issues': runtime_issues,
                'security_issues': security_issues,
                'total_issues': len(static_issues) + len(runtime_issues) + len(security_issues),
                'timestamp': asyncio.get_event_loop().time()
            }
        except Exception as e:
            print(f"缺陷检测失败: {e}")
            return {'error': str(e)}
