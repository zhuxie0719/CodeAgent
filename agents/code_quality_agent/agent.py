"""
代码质量AGENT主类
"""

import asyncio
from typing import Dict, List, Any, Optional
from .quality_checker import StyleChecker, DocumentationGenerator, CodeReviewer


class CodeQualityAgent:
    """代码质量AGENT"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.style_checker = StyleChecker(config)
        self.doc_generator = DocumentationGenerator(config)
        self.code_reviewer = CodeReviewer(config)
        self.is_running = False
    
    async def start(self):
        """启动AGENT"""
        self.is_running = True
        print("代码质量AGENT已启动")
    
    async def stop(self):
        """停止AGENT"""
        self.is_running = False
        print("代码质量AGENT已停止")
    
    async def check_quality(self, project_path: str) -> Dict[str, Any]:
        """检查代码质量"""
        try:
            # 检查代码风格
            style_issues = await self.style_checker.check_style(project_path)
            
            # 生成文档
            doc_status = await self.doc_generator.generate_docs(project_path)
            
            # 代码审查
            review_results = await self.code_reviewer.review_code(project_path)
            
            return {
                'style_issues': style_issues,
                'documentation': doc_status,
                'review_results': review_results,
                'timestamp': asyncio.get_event_loop().time()
            }
        except Exception as e:
            print(f"代码质量检查失败: {e}")
            return {'error': str(e)}
