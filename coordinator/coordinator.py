"""
协调中心主类
负责整体工作流协调和Agent管理
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .task_manager import TaskManager, TaskPriority
from .event_bus import EventBus
from .decision_engine import DecisionEngine
from .message_types import EventType, MessageFactory


class Coordinator:
    """协调中心 - 系统的核心控制器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.task_manager = TaskManager(config.get("task_manager", {}))
        self.event_bus = EventBus(config.get("event_bus", {}))
        self.decision_engine = DecisionEngine(config.get("decision_engine", {}))
        self.agents = {}
        self.is_running = False
        self.logger = logging.getLogger(__name__)
        
        # 工作流状态
        self.current_workflow = None
        self.workflow_history = []
        
        # 统计信息
        self.stats = {
            "workflows_completed": 0,
            "workflows_failed": 0,
            "total_issues_processed": 0,
            "total_fixes_applied": 0
        }
    
    async def start(self):
        """启动协调中心"""
        self.logger.info("协调中心启动中...")
        self.is_running = True
        
        # 启动核心组件
        await self.task_manager.start()
        await self.event_bus.start()
        await self.decision_engine.start()
        
        # 设置事件总线消息处理
        await self._setup_event_handlers()
        # 注册协调中心自身以接收 Result/Status/Error 消息
        async def _coordinator_bus_handler(message):
            try:
                from .message_types import TaskMessage, ResultMessage, StatusMessage, ErrorMessage, EventMessage
                if isinstance(message, ResultMessage):
                    await self._handle_agent_result(message.source_agent, message)
                elif isinstance(message, StatusMessage):
                    await self._handle_agent_status(message.source_agent, message)
                elif isinstance(message, ErrorMessage):
                    await self._handle_agent_error(message.source_agent, message)
                elif isinstance(message, EventMessage):
                    # 处理事件消息
                    if message.event_type.value == "task_completed":
                        await self._handle_task_completed(message.payload)
                    elif message.event_type.value == "task_failed":
                        await self._handle_task_failed(message.payload)
                elif isinstance(message, TaskMessage):
                    # 协调中心不直接处理 TaskMessage
                    self.logger.debug("Coordinator 收到 TaskMessage，忽略")
            except Exception as e:
                self.logger.error(f"协调中心消息处理失败: {e}")
                import traceback
                self.logger.error(f"错误详情: {traceback.format_exc()}")
        await self.event_bus.subscribe("agent_message", "coordinator", _coordinator_bus_handler)
        
        self.logger.info("协调中心已启动")
    
    async def stop(self):
        """停止协调中心"""
        import asyncio
        
        self.logger.info("协调中心停止中...")
        self.is_running = False
        
        # 停止核心组件（添加超时和异常处理）
        components = [
            ("任务管理器", self.task_manager),
            ("事件总线", self.event_bus),
            ("决策引擎", self.decision_engine)
        ]
        
        for name, component in components:
            try:
                await asyncio.wait_for(
                    component.stop(),
                    timeout=2.0  # 每个组件最多等待2秒
                )
                self.logger.info(f"{name}已停止")
            except asyncio.TimeoutError:
                self.logger.warning(f"{name}停止超时，跳过")
            except Exception as e:
                self.logger.warning(f"{name}停止异常: {e}")
        
        self.logger.info("协调中心已停止")
    
    async def register_agent(self, agent_id: str, agent):
        """注册Agent"""
        self.agents[agent_id] = agent
        
        # 为Agent设置消息处理函数：接收 TaskMessage -> 交给该 Agent 执行 -> 回传 ResultMessage 给 Coordinator
        async def agent_handler(message):
            try:
                from .message_types import TaskMessage
                if hasattr(message, 'task_id') and hasattr(message, 'payload'):
                    # 仅处理指向该Agent的任务
                    if isinstance(message, TaskMessage):
                        await agent.submit_task(message.task_id, message.payload)
                        # 轮询等待Agent完成
                        while True:
                            status = await agent.get_task_status(message.task_id)
                            if status and status.get('status') in ["completed", "failed"]:
                                break
                            await asyncio.sleep(0.2)
                        success = status.get('status') == 'completed'
                        result = status.get('result') if success else { 'error': status.get('error', 'Unknown error') }
                        await self.event_bus.send_result_message(
                            source_agent=agent_id,
                            target_agent='coordinator',
                            task_id=message.task_id,
                            result=result,
                            success=success,
                            error=None if success else status.get('error')
                        )
            except Exception as e:
                self.logger.error(f"Agent任务处理失败: {agent_id} - {e}")
        await self.event_bus.subscribe("agent_message", agent_id, agent_handler)
        
        # 发布Agent注册事件
        await self.event_bus.publish(
            EventType.AGENT_STARTED.value,
            {"agent_id": agent_id, "capabilities": getattr(agent, 'get_capabilities', lambda: [])()},
            "coordinator",
            broadcast=True
        )
        
        self.logger.info(f"Agent {agent_id} 已注册")
    
    async def unregister_agent(self, agent_id: str):
        """注销Agent"""
        if agent_id in self.agents:
            # 发布Agent停止事件
            await self.event_bus.publish(
                EventType.AGENT_STOPPED.value,
                {"agent_id": agent_id},
                "coordinator",
                broadcast=True
            )
            
            # 取消订阅
            await self.event_bus.unsubscribe("agent_message", agent_id)
            
            # 从注册表移除
            del self.agents[agent_id]
            
            self.logger.info(f"Agent {agent_id} 已注销")
    
    async def create_task(self, task_type: str, task_data: Dict[str, Any], 
                         priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """创建任务"""
        task_id = await self.task_manager.create_task(task_type, task_data, priority)
        
        # 发布任务创建事件
        await self.event_bus.publish(
            EventType.TASK_CREATED.value,
            {"task_id": task_id, "task_type": task_type, "priority": priority.name},
            "coordinator",
            broadcast=True
        )
        
        return task_id
    
    async def assign_task(self, task_id: str, agent_id: str):
        """分配任务给Agent"""
        if agent_id in self.agents:
            success = await self.task_manager.assign_task(task_id, agent_id)
            if success:
                # 发送任务消息给Agent
                task = self.task_manager.tasks.get(task_id)
                if task:
                    await self.event_bus.send_task_message(
                        source_agent="coordinator",
                        target_agent=agent_id,
                        task_id=task_id,
                        task_type=task['type'],
                        payload=task['data']
                    )
                self.logger.info(f"任务 {task_id} 已分配给 {agent_id}")
            else:
                self.logger.error(f"任务分配失败: {task_id} -> {agent_id}")
        else:
            self.logger.error(f"Agent不存在: {agent_id}")
    
    async def _setup_event_handlers(self):
        """设置事件处理器"""
        # 订阅任务完成事件
        await self.event_bus.subscribe(EventType.TASK_COMPLETED.value, "coordinator", self._handle_task_completed)
        await self.event_bus.subscribe(EventType.TASK_FAILED.value, "coordinator", self._handle_task_failed)
    
    async def _handle_agent_message(self, agent_id: str, message):
        """处理来自Agent的消息"""
        try:
            if hasattr(message, 'message_type'):
                if message.message_type.value == "result":
                    await self._handle_agent_result(agent_id, message)
                elif message.message_type.value == "status":
                    await self._handle_agent_status(agent_id, message)
                elif message.message_type.value == "error":
                    await self._handle_agent_error(agent_id, message)
        except Exception as e:
            self.logger.error(f"处理Agent消息失败: {agent_id} - {e}")
    
    async def _handle_agent_result(self, agent_id: str, message):
        """处理Agent结果消息"""
        task_id = message.task_id
        result = message.result
        success = message.status.value == "completed"
        
        print(f"\n{'='*60}")
        print(f"📨 Coordinator收到Agent结果消息")
        print(f"Agent: {agent_id}")
        print(f"Task ID: {task_id}")
        print(f"Status: {'成功' if success else '失败'}")
        print(f"{'='*60}\n")
        
        # 更新任务结果
        await self.task_manager.update_task_result(task_id, result, success)
        
        # 发布任务完成事件
        event_type = EventType.TASK_COMPLETED.value if success else EventType.TASK_FAILED.value
        await self.event_bus.publish(
            event_type,
            {"task_id": task_id, "agent_id": agent_id, "result": result},
            "coordinator",
            broadcast=True
        )
        
        self.logger.info(f"Agent {agent_id} 任务结果已处理: {task_id}")
    
    async def _handle_agent_status(self, agent_id: str, message):
        """处理Agent状态消息"""
        # 更新Agent状态信息
        self.logger.debug(f"Agent {agent_id} 状态更新: {message.agent_status}")
    
    async def _handle_agent_error(self, agent_id: str, message):
        """处理Agent错误消息"""
        self.logger.error(f"Agent {agent_id} 错误: {message.error_message}")
        
        # 发布系统错误事件
        await self.event_bus.publish(
            EventType.SYSTEM_ERROR.value,
            {"agent_id": agent_id, "error": message.error_message, "details": message.details},
            "coordinator",
            broadcast=True
        )
    
    async def _handle_task_completed(self, event_data):
        """处理任务完成事件"""
        task_id = event_data.get("task_id")
        agent_id = event_data.get("agent_id")
        result = event_data.get("result")
        
        print(f"\n{'='*60}")
        print(f"✅ 任务完成事件触发")
        print(f"Task ID: {task_id}")
        print(f"Agent: {agent_id}")
        print(f"Result keys: {list(result.keys()) if result else 'None'}")
        print(f"{'='*60}\n")
        
        self.logger.info(f"任务完成: {task_id} by {agent_id}")
        
        # 根据任务类型进行后续处理
        task = self.task_manager.tasks.get(task_id)
        if task:
            print(f"🔄 开始处理任务完成后续逻辑，任务类型: {task['type']}")
            await self._process_task_completion(task, result)
    
    async def _handle_task_failed(self, event_data):
        """处理任务失败事件"""
        task_id = event_data.get("task_id")
        agent_id = event_data.get("agent_id")
        
        self.logger.warning(f"任务失败: {task_id} by {agent_id}")
        
        # 尝试重试任务
        await self.task_manager.retry_task(task_id)
    
    async def _process_task_completion(self, task, result):
        """处理任务完成后的后续逻辑"""
        task_type = task['type']
        
        if task_type == 'detect_bugs':
            # 缺陷检测完成，启动决策流程
            await self._process_detection_completion(task, result)
        elif task_type == 'fix_issues':
            # 修复完成，启动验证流程
            await self._process_fix_completion(task, result)
        elif task_type == 'validate_fix':
            # 验证完成，工作流结束
            await self._process_validation_completion(task, result)
    
    async def _process_detection_completion(self, task, result):
        """处理缺陷检测完成（透传 file_path / project_path）"""
        issues = result.get('detection_results', {}).get('issues', [])
        
        print(f"\n{'='*60}")
        print(f"🔍 缺陷检测完成，开始处理")
        print(f"发现 {len(issues)} 个缺陷")
        print(f"{'='*60}\n")

        if issues:
            print(f"🧠 使用决策引擎分析缺陷...")
            # 使用决策引擎分析缺陷
            decisions = await self.decision_engine.analyze_complexity(issues)

            # 原样携带 file_path 或 project_path（不做父目录推断）
            payload = {
                'issues': issues,
                'decisions': decisions
            }
            if 'project_path' in task['data'] and task['data']['project_path']:
                payload['project_path'] = task['data']['project_path']
            if 'file_path' in task['data'] and task['data']['file_path']:
                payload['file_path'] = task['data']['file_path']

            print(f"🔧 创建修复任务...")
            # 创建修复任务
            fix_task_id = await self.create_task('fix_issues', payload, TaskPriority.HIGH)

            print(f"📤 分配修复任务给 fix_execution_agent (task_id: {fix_task_id})")
            # 分配给修复执行Agent
            await self.assign_task(fix_task_id, 'fix_execution_agent')
        else:
            self.logger.info("未发现需要修复的缺陷")
    
    async def _process_fix_completion(self, task, result):
        """处理修复完成（透传 file_path / project_path）"""
        # 原样携带 file_path 或 project_path
        payload = {
            'fix_result': result
        }
        if 'project_path' in task['data'] and task['data']['project_path']:
            payload['project_path'] = task['data']['project_path']
        if 'file_path' in task['data'] and task['data']['file_path']:
            payload['file_path'] = task['data']['file_path']

        # 创建验证任务
        validation_task_id = await self.create_task('validate_fix', payload, TaskPriority.HIGH)
        
        # 分配给测试验证Agent
        await self.assign_task(validation_task_id, 'test_validation_agent')
    
    async def _process_validation_completion(self, task, result):
        """处理验证完成"""
        self.logger.info("工作流验证完成")
        # 这里可以添加最终报告生成等逻辑
    
    async def process_workflow(self, file_path: Optional[str] = None, project_path: Optional[str] = None) -> Dict[str, Any]:
        """
        处理完整的工作流 
        
        主工作流程（按照workflow_diagram.md）：
        1. Bug Detection Agent - 检测缺陷，生成缺陷清单
        2. Decision Engine - 判断缺陷复杂度
        3. Fix Execution Agent - 执行修复
        4. Test Validation Agent - 验证修复结果
        """
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_workflow = {
            'id': workflow_id,
            'project_path': project_path,
            'file_path': file_path,
            'start_time': datetime.now(),
            'status': 'running',
            'tasks': []
        }
        
        try:
            if not file_path and not project_path:
                raise Exception("process_workflow 需要提供 file_path 或 project_path 之一")
            self.logger.info(f"开始处理工作流: {workflow_id} (file_path={file_path}, project_path={project_path})")
            
            # ===== 阶段1: 缺陷检测 =====
            self.logger.info("=== 阶段1: Bug Detection Agent - 缺陷检测 ===")
            # 同时支持单文件/项目两种入口
            if file_path:
                detection_task_payload = {
                    'file_path': file_path,
                    'options': {
                        'enable_static': True,
                        'enable_pylint': True,
                        'enable_flake8': True,
                        'enable_bandit': True,
                        'enable_mypy': True,
                        'enable_ai_analysis': True,
                        'enable_dynamic': True  # 启用动态检测
                    }
                }
            else:
                detection_task_payload = {
                    'project_path': project_path,
                    'options': {
                        'enable_static': True,
                        'enable_pylint': True,
                        'enable_flake8': True,
                        'enable_bandit': True,
                        'enable_mypy': True,
                        'enable_ai_analysis': True,
                        'enable_dynamic': True  # 启用动态检测
                    }
                }
            detection_task_id = await self.create_task('detect_bugs', detection_task_payload, TaskPriority.HIGH)

            
            self.current_workflow['tasks'].append({
                'task_id': detection_task_id,
                'type': 'detect_bugs',
                'status': 'created',
                'stage': 1,
                'agent': 'bug_detection_agent'
            })
            
            # 分配给Bug Detection Agent
            if 'bug_detection_agent' in self.agents:
                await self.assign_task(detection_task_id, 'bug_detection_agent')
                self.logger.info("缺陷检测任务已分配给Bug Detection Agent")
            else:
                raise Exception("Bug Detection Agent未注册")
            
            # 等待检测完成
            self.logger.info("等待缺陷检测完成...")
            detection_result = await self.task_manager.get_task_result(detection_task_id, timeout=600)
            
            if not detection_result.get('success', False):
                raise Exception(f"缺陷检测失败: {detection_result.get('error', '未知错误')}")
            
            issues = detection_result.get('detection_results', {}).get('issues', [])
            self.stats["total_issues_processed"] += len(issues)
            
            if not issues:
                # 没有发现缺陷，工作流结束
                self.logger.info("未发现需要修复的缺陷，工作流完成")
                self.current_workflow['status'] = 'completed'
                self.current_workflow['end_time'] = datetime.now()
                self.stats["workflows_completed"] += 1
                
                return {
                    'workflow_id': workflow_id,
                    'success': True,
                    'message': '未发现需要修复的缺陷',
                    'detection_result': detection_result,
                    'summary': {
                        'total_issues': 0,
                        'fixed_issues': 0,
                        'processing_time': (self.current_workflow['end_time'] - self.current_workflow['start_time']).total_seconds()
                    }
                }
            
            # ===== 阶段2: 智能决策 =====
            self.logger.info("=== 阶段2: Decision Engine - 智能决策 ===")
            self.logger.info(f"决策引擎开始分析 {len(issues)} 个缺陷")
            
            # 使用决策引擎分析缺陷复杂度
            decisions = await self.decision_engine.analyze_complexity(issues)
            
            auto_fixable_count = len(decisions.get('auto_fixable', []))
            ai_assisted_count = len(decisions.get('ai_assisted', []))
            manual_review_count = len(decisions.get('manual_review', []))
            
            self.logger.info(f"决策分析完成: 自动修复={auto_fixable_count}, AI辅助={ai_assisted_count}, 人工审查={manual_review_count}")
            
            # ===== 阶段3: 修复执行 =====
            self.logger.info("=== 阶段3: Fix Execution Agent - 修复执行 ===")
            fix_task_id = await self.create_task('fix_issues', {
                'project_path': project_path,
                'issues': issues,
                'decisions': decisions,
                'fix_options': {
                    'backup_enabled': True,
                    'rollback_enabled': True,
                    'auto_fix_enabled': True,
                    'ai_assisted_enabled': True
                }
            }, TaskPriority.HIGH)
            
            self.current_workflow['tasks'].append({
                'task_id': fix_task_id,
                'type': 'fix_issues',
                'status': 'created',
                'stage': 3,
                'agent': 'fix_execution_agent'
            })
            
            # 分配给Fix Execution Agent
            if 'fix_execution_agent' in self.agents:
                await self.assign_task(fix_task_id, 'fix_execution_agent')
                self.logger.info("修复任务已分配给Fix Execution Agent")
            else:
                raise Exception("Fix Execution Agent未注册")
                
                # 等待修复完成
            self.logger.info("等待修复完成...")
            fix_result = await self.task_manager.get_task_result(fix_task_id, timeout=900)
            
            if not fix_result.get('success', False):
                raise Exception(f"修复失败: {fix_result.get('error', '未知错误')}")
            
            self.stats["total_fixes_applied"] += len(fix_result.get('fix_results', []))
            
            # ===== 阶段4: 验证与反馈 =====
            self.logger.info("=== 阶段4: Test Validation Agent - 验证与反馈 ===")
            validation_task_id = await self.create_task('validate_fix', {
                'project_path': project_path,
                'file_path': file_path,
                'fix_result': fix_result,
                'original_issues': issues,
                'test_options': {
                    'enable_unit_tests': True,
                    'enable_api_tests': True,
                    'enable_integration_tests': True,
                    'enable_regression_tests': True
                }
            }, TaskPriority.HIGH)
            
            self.current_workflow['tasks'].append({
                'task_id': validation_task_id,
                'type': 'validate_fix',
                'status': 'created',
                'stage': 4,
                'agent': 'test_validation_agent'
            })
            
            # 分配给Test Validation Agent
            if 'test_validation_agent' in self.agents:
                await self.assign_task(validation_task_id, 'test_validation_agent')
                self.logger.info("验证任务已分配给Test Validation Agent")
                
                # 等待验证完成
                self.logger.info("等待验证完成...")
                validation_result = await self.task_manager.get_task_result(validation_task_id, timeout=300)
            else:
                self.logger.warning("Test Validation Agent未注册，跳过验证步骤")
                validation_result = {
                    'success': True, 
                    'message': '验证Agent未注册，跳过验证',
                    'validation_status': 'skipped'
                }
            
            # ===== 工作流完成 =====
            self.logger.info("=== 工作流完成 ===")
            self.current_workflow['status'] = 'completed'
            self.current_workflow['end_time'] = datetime.now()
            self.stats["workflows_completed"] += 1
            
            # 生成统计信息
            workflow_duration = (self.current_workflow['end_time'] - self.current_workflow['start_time']).total_seconds()
            
            return {
                'workflow_id': workflow_id,
                'success': True,
                'workflow_summary': {
                    'total_issues_found': len(issues),
                    'auto_fixable': auto_fixable_count,
                    'ai_assisted': ai_assisted_count,
                    'manual_review': manual_review_count,
                    'workflow_duration_seconds': workflow_duration,
                    'stages_completed': 4
                },
                'results': {
                    'detection_result': detection_result,
                    'decisions': decisions,
                    'fix_result': fix_result,
                    'validation_result': validation_result
                },
                'summary': {
                    'total_issues': len(issues),
                    'fixed_issues': len(fix_result.get('fix_results', [])),
                    'processing_time': workflow_duration
                }
            }
                
        except Exception as e:
            self.logger.error(f"工作流处理失败: {e}")
            self.current_workflow['status'] = 'failed'
            self.current_workflow['error'] = str(e)
            self.current_workflow['end_time'] = datetime.now()
            self.stats["workflows_failed"] += 1
            
            return {
                'workflow_id': workflow_id,
                'success': False,
                'error': str(e),
                'summary': {
                    'processing_time': (self.current_workflow['end_time'] - self.current_workflow['start_time']).total_seconds()
                }
            }
        finally:
            # 记录工作流历史
            if self.current_workflow:
                self.workflow_history.append(self.current_workflow.copy())
                # 限制历史记录数量
                if len(self.workflow_history) > 100:
                    self.workflow_history = self.workflow_history[-50:]
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            "registered_agents": list(self.agents.keys()),
            "current_workflow": self.current_workflow,
            "task_manager_stats": await self.task_manager.get_stats(),
            "decision_engine_stats": await self.decision_engine.get_stats(),
            "event_bus_stats": await self.event_bus.get_stats()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "is_running": self.is_running,
            "registered_agents": len(self.agents),
            "current_workflow": self.current_workflow,
            "task_manager": await self.task_manager.health_check(),
            "decision_engine": await self.decision_engine.health_check(),
            "event_bus": await self.event_bus.health_check()
            }