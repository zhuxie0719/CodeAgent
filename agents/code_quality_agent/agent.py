"""
代码质量AGENT主类
专注于单文件分析        
"""

import asyncio
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..base_agent import BaseAgent, TaskStatus
from .quality_checker import analyze_file_quality, StyleChecker, QualityMetricsCalculator, AICodeQualityAnalyzer


class CodeQualityAgent(BaseAgent):
    """代码质量AGENT - 专注单文件分析"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("code_quality_agent", config)
        self.style_checker = StyleChecker(config)
        self.metrics_calculator = QualityMetricsCalculator(config)
        self.ai_analyzer = AICodeQualityAnalyzer(config)
        self.is_running = False
    
    async def initialize(self) -> bool:
        """初始化Agent"""
        try:
            # 检查AI配置
            ai_api_key = self.config.get('ai_api_key')
            if not ai_api_key:
                print("警告: 未配置AI API密钥，将使用备用报告生成")
            
            self.is_running = True
            print("代码质量AGENT初始化成功")
            return True
        except Exception as e:
            print(f"代码质量AGENT初始化失败: {e}")
            return False
    
    async def process_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理质量分析任务"""
        try:
            file_path = task_data.get('file_path')
            file_content = task_data.get('file_content')
            
            if not file_path or not file_content:
                return {'error': '缺少文件路径或文件内容'}
            
            # 调用单文件质量分析
            result = await analyze_file_quality(file_path, file_content, self.config)
            
            return result
            
        except Exception as e:
            print(f"处理质量分析任务失败: {e}")
            return {'error': str(e)}
    
    def get_capabilities(self) -> List[str]:
        """获取Agent能力列表"""
        return [
            "单文件代码风格检查",
            "代码质量指标计算",
            "AI驱动的质量评分报告生成",
            "多种编程语言支持",
            "详细的改进建议提供"
        ]
    
    async def analyze_single_file(self, file_path: str, file_content: str) -> Dict[str, Any]:
        """分析单个文件的质量 - 直接接口"""
        try:
            result = await analyze_file_quality(file_path, file_content, self.config)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path,
                'analysis_time': datetime.now().isoformat()
            }
    
    async def analyze_file_from_path(self, file_path: str) -> Dict[str, Any]:
        """从文件路径分析文件质量"""
        try:
            if not os.path.exists(file_path):
                return {'error': f'文件不存在: {file_path}'}
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            return await self.analyze_single_file(file_path, file_content)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'文件分析失败: {str(e)}',
                'file_path': file_path,
                'analysis_time': datetime.now().isoformat()
            }