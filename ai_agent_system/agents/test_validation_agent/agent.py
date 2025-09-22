"""
测试验证AGENT主类
"""

import asyncio
from typing import Dict, List, Any, Optional
from .tester import UnitTester, IntegrationTester, PerformanceTester


class TestValidationAgent:
    """测试验证AGENT"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.unit_tester = UnitTester(config)
        self.integration_tester = IntegrationTester(config)
        self.performance_tester = PerformanceTester(config)
        self.is_running = False
    
    async def start(self):
        """启动AGENT"""
        self.is_running = True
        print("测试验证AGENT已启动")
    
    async def stop(self):
        """停止AGENT"""
        self.is_running = False
        print("测试验证AGENT已停止")
    
    async def validate_fix(self, fix_result: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """验证修复结果"""
        try:
            validation_result = {
                'passed': False,
                'test_results': {},
                'coverage': 0,
                'performance_metrics': {},
                'timestamp': asyncio.get_event_loop().time()
            }
            
            # 运行单元测试
            unit_results = await self.unit_tester.run_tests(project_path)
            validation_result['test_results']['unit'] = unit_results
            
            # 运行集成测试
            integration_results = await self.integration_tester.run_tests(project_path)
            validation_result['test_results']['integration'] = integration_results
            
            # 运行性能测试
            performance_results = await self.performance_tester.run_tests(project_path)
            validation_result['performance_metrics'] = performance_results
            
            # 计算测试覆盖率
            coverage = await self.unit_tester.calculate_coverage(project_path)
            validation_result['coverage'] = coverage
            
            # 判断是否通过验证
            validation_result['passed'] = (
                unit_results.get('passed', False) and
                integration_results.get('passed', False) and
                coverage >= self.config.get('min_coverage', 80)
            )
            
            return validation_result
        except Exception as e:
            print(f"测试验证失败: {e}")
            return {'passed': False, 'error': str(e)}
