"""
测试验证AGENT主类（重构：继承 BaseAgent 并实现标准任务处理流程）
"""

import asyncio
from typing import Dict, List, Any, Optional
from agents.base_agent import BaseAgent
from .tester import UnitTester, IntegrationTester, PerformanceTester
from .ai_test_generator import AITestGenerator
from .mock_ai_test_generator import MockAITestGenerator


class TestValidationAgent(BaseAgent):
    """测试验证AGENT：负责对修复后的项目进行自动化测试与反馈"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(agent_id="test_validation_agent", config=config)
        self.unit_tester = UnitTester(config)
        self.integration_tester = IntegrationTester(config)
        self.performance_tester = PerformanceTester(config)
        
        # 根据是否有API密钥选择AI生成器
        api_key = config.get("ai_api_key")
        if api_key:
            self.ai_test_generator = AITestGenerator(api_key=api_key)
            print("🤖 使用真实AI测试生成器")
        else:
            # 强制使用Mock生成器进行测试
            self.ai_test_generator = MockAITestGenerator()
            print("🤖 使用模拟AI测试生成器（演示模式）")
        
        self.task_status = {}  # 存储任务状态

    async def initialize(self) -> bool:
        return True
    
    async def submit_task(self, task_id: str, payload: Dict[str, Any]):
        """提交任务 - 协调中心调用的接口"""
        try:
            # 设置任务状态为运行中
            self.task_status[task_id] = {
                'status': 'running',
                'result': None,
                'error': None
            }
            
            # 异步执行任务
            asyncio.create_task(self._execute_task_async(task_id, payload))
            
        except Exception as e:
            self.task_status[task_id] = {
                'status': 'failed',
                'result': None,
                'error': str(e)
            }
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态 - 协调中心调用的接口"""
        return self.task_status.get(task_id)
    
    async def _execute_task_async(self, task_id: str, payload: Dict[str, Any]):
        """异步执行任务"""
        try:
            print(f"开始处理验证任务 {task_id}")
            
            # 执行验证
            validation_result = await self.process_task(task_id, payload)
            
            # 更新任务状态为完成
            self.task_status[task_id] = {
                'status': 'completed',
                'result': validation_result,
                'error': None
            }
            
        except Exception as e:
            # 更新任务状态为失败
            self.task_status[task_id] = {
                'status': 'failed',
                'result': None,
                'error': str(e)
            }

    def get_capabilities(self) -> List[str]:
        return [
            "validate_fix",
            "run_unit_tests",
            "run_integration_tests",
            "run_performance_tests",
            "generate_tests_with_ai"
        ]

    async def process_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """统一任务入口
        处理协调器发送的验证任务
        task_data 结构（来自协调器）：
        {
            "project_path": str,
            "file_path": str,
            "fix_result": dict,
            "original_issues": list,
            "test_options": dict
        }
        """
        try:
            self.logger.info(f"开始处理验证任务: {task_id}")
            
            # 从协调器发送的数据中提取信息
            project_path = task_data.get("project_path")
            file_path = task_data.get("file_path") or task_data.get("test_file")  # 支持test_file字段
            fix_result = task_data.get("fix_result", {})
            test_options = task_data.get("test_options", {})
            
            # 导入os模块
            import os
            
            # 如果没有project_path，使用file_path的目录
            if not project_path and file_path:
                project_path = os.path.dirname(file_path)
            
            # 如果file_path不是绝对路径，则相对于project_path构建完整路径
            if file_path and not os.path.isabs(file_path) and project_path:
                file_path = os.path.join(project_path, file_path)
            
            if not project_path:
                raise ValueError("缺少 project_path 或 file_path")

            # 设置测试选项
            min_coverage = self.config.get("min_coverage", 80)
            generate_with_ai = test_options.get("generate_with_ai", True)  # 默认启用AI生成

            # 可选：在测试前进行AI用例生成
            ai_generated_test = None
            if generate_with_ai and file_path:
                print(f"🤖 使用AI生成测试文件: {file_path}")
                ai_result = await self.ai_test_generator.generate_test_file(file_path, project_path)
                if ai_result["success"]:
                    ai_generated_test = ai_result["test_file_path"]
                    print(f"✅ AI测试文件生成成功: {ai_generated_test}")
                else:
                    print(f"❌ AI测试文件生成失败: {ai_result.get('error', '未知错误')}")

            # 执行完整验证
            validation_result = {
                "passed": False,
                "test_results": {},
                "coverage": 0,
                "performance_metrics": {},
                "timestamp": asyncio.get_event_loop().time(),
                "validation_status": "unknown"
            }

            # 运行单元测试
            # 优先使用AI生成的测试文件
            target_file = None
            if ai_generated_test:
                import os
                # 使用完整的相对路径，而不是仅仅文件名
                target_file = os.path.relpath(ai_generated_test, project_path)
                print(f"🎯 使用AI生成的测试文件: {target_file}")
            elif file_path:
                import os
                target_file = os.path.basename(file_path)
                # 如果是Python文件，转换为测试文件名
                if target_file.endswith('.py') and not target_file.startswith('test_'):
                    # 将普通Python文件转换为测试文件名
                    target_file = f"test_{target_file}"
            
            unit_results = await self.unit_tester.run_tests(project_path, target_file)
            validation_result["test_results"]["unit"] = unit_results
            
            # 添加AI生成信息到结果中
            if ai_generated_test:
                validation_result["ai_generated_test"] = {
                    "file_path": ai_generated_test,
                    "success": True
                }
                validation_result["ai_generated_test_file"] = ai_generated_test

            # 运行集成测试
            integration_results = await self.integration_tester.run_tests(project_path)
            validation_result["test_results"]["integration"] = integration_results

            # 运行性能测试
            performance_results = await self.performance_tester.run_tests(project_path)
            validation_result["performance_metrics"] = performance_results

            # 计算代码覆盖率
            coverage = await self.unit_tester.calculate_coverage(project_path)
            validation_result["coverage"] = coverage

            # 判断验证是否通过
            validation_result["passed"] = (
                unit_results.get("passed", False)
                and integration_results.get("passed", False)
                and coverage >= min_coverage
            )
            
            # 设置验证状态
            validation_result["validation_status"] = "passed" if validation_result["passed"] else "failed"
            
            # 添加回归检测（简化实现）
            validation_result["regression_detected"] = False
            
            # 清理AI生成的测试文件（可选）
            cleanup_ai_tests = test_options.get("cleanup_ai_tests", False)  # 默认不清理
            if cleanup_ai_tests and ai_generated_test:
                await self.ai_test_generator.cleanup_test_file(ai_generated_test)
                print(f"🧹 已清理AI生成的测试文件: {ai_generated_test}")
            elif ai_generated_test:
                print(f"📁 AI生成的测试文件已保留: {ai_generated_test}")
            
            self.logger.info(f"验证任务完成: {task_id}, 通过: {validation_result['passed']}")
            return validation_result
            
        except Exception as e:
            self.logger.error(f"验证任务失败: {task_id}, 错误: {e}")
            return {
                "passed": False,
                "test_results": {},
                "coverage": 0,
                "performance_metrics": {},
                "validation_status": "failed",
                "regression_detected": False,
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
