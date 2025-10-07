"""
代码分析AGENT主类
"""

import asyncio
import json
import time
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from ..base_agent import BaseAgent, TaskStatus
from .analyzer import ProjectAnalyzer, CodeAnalyzer, DependencyAnalyzer, AIAnalysisService, ProjectIntent


class CodeAnalysisAgent(BaseAgent):
    """代码分析AGENT"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("code_analysis_agent", config)
        self.ai_service = AIAnalysisService()
        self.project_analyzer = ProjectAnalyzer()
        self.code_analyzer = CodeAnalyzer(self.ai_service)
        self.dependency_analyzer = DependencyAnalyzer()
    
    async def start(self):
        """启动AGENT"""
        self.is_running = True
        print("代码分析AGENT已启动")
    
    async def stop(self):
        """停止AGENT"""
        self.is_running = False
        print("代码分析AGENT已停止")
    
    async def submit_task(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """提交任务"""
        try:
            # 添加到任务列表
            self.tasks[task_id] = {
                "task_id": task_id,
                "status": TaskStatus.PENDING,
                "created_at": datetime.now(),
                "started_at": None,
                "completed_at": None,
                "result": None,
                "error": None,
                "data": task_data
            }
            
            # 启动任务处理
            asyncio.create_task(self._process_task(task_id, task_data))
            return True
            
        except Exception as e:
            print(f"提交任务失败: {e}")
            return False
    
    async def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """分析项目结构"""
        try:
            print(f"开始分析项目: {project_path}")
            
            # 并行执行基础分析
            project_structure_task = self.project_analyzer.analyze_project_structure(project_path)
            code_quality_task = self.code_analyzer.analyze_code_quality(project_path)
            dependencies_task = self.dependency_analyzer.analyze_dependencies(project_path)
            
            # 等待所有基础分析完成
            project_structure, code_quality, dependencies = await asyncio.gather(
                project_structure_task,
                code_quality_task,
                dependencies_task
            )
            
            # 生成项目意图分析（添加超时处理）
            try:
                project_intent = await asyncio.wait_for(
                    self._generate_project_intent({
                        'project_structure': project_structure,
                        'code_quality': code_quality,
                        'dependencies': dependencies
                    }),
                    timeout=15.0  # 15秒超时
                )
            except asyncio.TimeoutError:
                print("项目意图分析超时，使用默认意图")
                project_intent = {
                    'project_type': 'unknown',
                    'purpose': '项目意图分析超时',
                    'key_features': [],
                    'architecture': 'unknown',
                    'technology_stack': [],
                    'complexity': 'unknown',
                    'maintainability': 'unknown'
                }
            except Exception as e:
                print(f"项目意图分析失败: {e}")
                project_intent = {
                    'project_type': 'unknown',
                    'purpose': f'项目意图分析失败: {str(e)}',
                    'key_features': [],
                    'architecture': 'unknown',
                    'technology_stack': [],
                    'complexity': 'unknown',
                    'maintainability': 'unknown'
                }
            
            # 生成AI项目摘要（添加超时处理）
            try:
                ai_summary = await asyncio.wait_for(
                    self.ai_service.generate_project_summary({
                        'project_structure': project_structure,
                        'code_quality': code_quality,
                        'dependencies': dependencies
                    }),
                    timeout=30.0  # 30秒超时
                )
            except asyncio.TimeoutError:
                print("AI分析超时，使用默认摘要")
                ai_summary = {
                    'success': False,
                    'error': 'AI分析超时',
                    'summary': 'AI分析服务暂时不可用，请稍后重试。'
                }
            except Exception as e:
                print(f"AI分析失败: {e}")
                ai_summary = {
                    'success': False,
                    'error': f'AI分析失败: {str(e)}',
                    'summary': 'AI分析服务出现错误，请检查网络连接或稍后重试。'
                }
            
            result = {
                'project_structure': project_structure,
                'code_quality': code_quality,
                'dependencies': dependencies,
                'project_intent': project_intent,
                'ai_summary': ai_summary,
                'analysis_metadata': {
                    'timestamp': asyncio.get_event_loop().time(),
                    'agent_version': '2.0',
                    'analysis_depth': 'comprehensive'
                }
            }
            
            print(f"项目分析完成: {project_path}")
            return result
            
        except Exception as e:
            print(f"项目分析失败: {e}")
            return {'error': str(e)}
    
    async def _generate_project_intent(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成项目意图分析"""
        try:
            project_structure = analysis_data['project_structure']
            code_quality = analysis_data['code_quality']
            dependencies = analysis_data['dependencies']
            
            # 基于分析数据推断项目意图
            metadata = project_structure.get('project_metadata', {})
            
            # 推断项目类型
            project_type = self._infer_project_type(metadata, dependencies)
            
            # 推断主要用途
            main_purpose = self._infer_main_purpose(project_structure, code_quality)
            
            # 提取关键特性
            key_features = self._extract_key_features(project_structure, code_quality)
            
            # 识别架构模式
            architecture_pattern = self._identify_architecture_pattern(project_structure, dependencies)
            
            # 识别技术栈
            technology_stack = self._identify_technology_stack(metadata, dependencies)
            
            # 评估复杂度等级
            complexity_level = self._assess_complexity_level(code_quality)
            
            # 计算可维护性分数
            maintainability_score = self._calculate_maintainability_score(code_quality)
            
            return {
                'project_type': project_type,
                'main_purpose': main_purpose,
                'key_features': key_features,
                'architecture_pattern': architecture_pattern,
                'technology_stack': technology_stack,
                'complexity_level': complexity_level,
                'maintainability_score': maintainability_score,
                'confidence': self._calculate_confidence(analysis_data)
            }
            
        except Exception as e:
            print(f"生成项目意图失败: {e}")
            return {
                'project_type': 'unknown',
                'main_purpose': 'unknown',
                'key_features': [],
                'architecture_pattern': 'unknown',
                'technology_stack': [],
                'complexity_level': 'unknown',
                'maintainability_score': 0.0,
                'confidence': 0.0
            }
    
    def _infer_project_type(self, metadata: Dict[str, Any], dependencies: Dict[str, Any]) -> str:
        """推断项目类型"""
        project_type = metadata.get('type', 'unknown')
        framework = metadata.get('framework')
        
        if framework:
            if framework in ['django', 'flask']:
                return 'web_application'
            elif framework in ['nextjs', 'vue', 'angular', 'react']:
                return 'frontend_application'
            elif framework == 'fastapi':
                return 'api_service'
        
        # 基于依赖推断
        python_packages = dependencies.get('python_packages', [])
        node_modules = dependencies.get('node_modules', [])
        
        if any('django' in pkg.get('name', '') for pkg in python_packages):
            return 'web_application'
        elif any('flask' in pkg.get('name', '') for pkg in python_packages):
            return 'web_application'
        elif any('fastapi' in pkg.get('name', '') for pkg in python_packages):
            return 'api_service'
        elif any('pytest' in pkg.get('name', '') for pkg in python_packages):
            return 'test_project'
        elif 'express' in node_modules:
            return 'web_application'
        elif 'react' in node_modules:
            return 'frontend_application'
        
        return project_type
    
    def _infer_main_purpose(self, project_structure: Dict[str, Any], code_quality: Dict[str, Any]) -> str:
        """推断主要用途"""
        # 基于文件结构推断
        code_files = project_structure.get('code_files', [])
        config_files = project_structure.get('config_files', [])
        
        # 检查是否有API相关文件
        api_indicators = ['api', 'endpoint', 'route', 'controller']
        has_api = any(
            any(indicator in file['path'].lower() for indicator in api_indicators)
            for file in code_files
        )
        
        if has_api:
            return 'API服务开发'
        
        # 检查是否有前端相关文件
        frontend_indicators = ['html', 'css', 'js', 'component', 'view']
        has_frontend = any(
            any(indicator in file['path'].lower() for indicator in frontend_indicators)
            for file in code_files
        )
        
        if has_frontend:
            return '前端应用开发'
        
        # 检查是否有测试文件
        test_files = project_structure.get('test_files', [])
        if test_files:
            return '测试项目'
        
        # 检查是否有配置文件
        if config_files:
            return '配置管理'
        
        return '通用软件开发'
    
    def _extract_key_features(self, project_structure: Dict[str, Any], code_quality: Dict[str, Any]) -> List[str]:
        """提取关键特性"""
        features = []
        
        # 基于文件结构提取特性
        code_files = project_structure.get('code_files', [])
        
        # 检查数据库相关
        db_indicators = ['model', 'database', 'db', 'sql', 'orm']
        has_db = any(
            any(indicator in file['path'].lower() for indicator in db_indicators)
            for file in code_files
        )
        if has_db:
            features.append('数据库集成')
        
        # 检查认证相关
        auth_indicators = ['auth', 'login', 'user', 'permission']
        has_auth = any(
            any(indicator in file['path'].lower() for indicator in auth_indicators)
            for file in code_files
        )
        if has_auth:
            features.append('用户认证')
        
        # 检查API相关
        api_indicators = ['api', 'endpoint', 'route']
        has_api = any(
            any(indicator in file['path'].lower() for indicator in api_indicators)
            for file in code_files
        )
        if has_api:
            features.append('RESTful API')
        
        # 检查测试覆盖
        test_files = project_structure.get('test_files', [])
        if test_files:
            features.append('单元测试')
        
        # 检查文档
        doc_files = project_structure.get('documentation_files', [])
        if doc_files:
            features.append('文档完善')
        
        return features
    
    def _identify_architecture_pattern(self, project_structure: Dict[str, Any], dependencies: Dict[str, Any]) -> str:
        """识别架构模式"""
        # 基于目录结构识别
        files = project_structure.get('files', [])
        
        # 检查MVC模式
        mvc_indicators = ['model', 'view', 'controller', 'mvc']
        has_mvc = any(
            any(indicator in file['path'].lower() for indicator in mvc_indicators)
            for file in files
        )
        if has_mvc:
            return 'MVC模式'
        
        # 检查微服务架构
        microservice_indicators = ['service', 'microservice', 'gateway']
        has_microservice = any(
            any(indicator in file['path'].lower() for indicator in microservice_indicators)
            for file in files
        )
        if has_microservice:
            return '微服务架构'
        
        # 检查分层架构
        layer_indicators = ['layer', 'tier', 'level']
        has_layers = any(
            any(indicator in file['path'].lower() for indicator in layer_indicators)
            for file in files
        )
        if has_layers:
            return '分层架构'
        
        return '单体架构'
    
    def _identify_technology_stack(self, metadata: Dict[str, Any], dependencies: Dict[str, Any]) -> List[str]:
        """识别技术栈"""
        stack = []
        
        # 基于项目类型添加技术
        project_type = metadata.get('type', '')
        if project_type == 'python':
            stack.append('Python')
        elif project_type == 'nodejs':
            stack.append('Node.js')
        elif project_type == 'java':
            stack.append('Java')
        elif project_type == 'rust':
            stack.append('Rust')
        
        # 基于框架添加技术
        framework = metadata.get('framework')
        if framework:
            stack.append(framework.title())
        
        # 基于依赖添加技术
        python_packages = dependencies.get('python_packages', [])
        for pkg in python_packages:
            pkg_name = pkg.get('name', '').lower()
            if 'django' in pkg_name:
                stack.append('Django')
            elif 'flask' in pkg_name:
                stack.append('Flask')
            elif 'fastapi' in pkg_name:
                stack.append('FastAPI')
            elif 'pandas' in pkg_name:
                stack.append('Pandas')
            elif 'numpy' in pkg_name:
                stack.append('NumPy')
        
        node_modules = dependencies.get('node_modules', [])
        for module in node_modules:
            if 'react' in module:
                stack.append('React')
            elif 'vue' in module:
                stack.append('Vue.js')
            elif 'angular' in module:
                stack.append('Angular')
            elif 'express' in module:
                stack.append('Express.js')
        
        return list(set(stack))  # 去重
    
    def _assess_complexity_level(self, code_quality: Dict[str, Any]) -> str:
        """评估复杂度等级"""
        overall_metrics = code_quality.get('overall_metrics', {})
        avg_complexity = overall_metrics.get('average_complexity', 1)
        
        if avg_complexity <= 3:
            return '简单'
        elif avg_complexity <= 7:
            return '中等'
        elif avg_complexity <= 15:
            return '复杂'
        else:
            return '非常复杂'
    
    def _calculate_maintainability_score(self, code_quality: Dict[str, Any]) -> float:
        """计算可维护性分数"""
        overall_metrics = code_quality.get('overall_metrics', {})
        avg_maintainability = overall_metrics.get('average_maintainability', 50)
        
        # 基于问题数量调整分数
        total_issues = overall_metrics.get('total_issues', 0)
        error_count = overall_metrics.get('error_count', 0)
        
        # 问题惩罚
        issue_penalty = min(total_issues * 2, 20)  # 最多扣20分
        error_penalty = min(error_count * 5, 30)   # 最多扣30分
        
        final_score = max(0, avg_maintainability - issue_penalty - error_penalty)
        return round(final_score, 2)
    
    def _calculate_confidence(self, analysis_data: Dict[str, Any]) -> float:
        """计算分析置信度"""
        confidence = 0.5  # 基础置信度
        
        # 基于分析数据完整性调整
        project_structure = analysis_data['project_structure']
        code_quality = analysis_data['code_quality']
        dependencies = analysis_data['dependencies']
        
        # 项目结构完整性
        if project_structure.get('project_metadata', {}).get('type') != 'unknown':
            confidence += 0.2
        
        # 代码质量分析完整性
        if code_quality.get('overall_metrics', {}).get('files_analyzed', 0) > 0:
            confidence += 0.2
        
        # 依赖分析完整性
        if dependencies.get('python_packages') or dependencies.get('node_modules'):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    async def monitor_changes(self, project_path: str, callback):
        """监控代码变更"""
        while self.is_running:
            # 实现文件监控逻辑
            await asyncio.sleep(1)  # 临时实现
    
    async def _process_task(self, task_id: str, task_data: Dict[str, Any]):
        """处理任务"""
        try:
            # 更新状态为运行中
            self.tasks[task_id]["status"] = TaskStatus.RUNNING
            self.tasks[task_id]["started_at"] = datetime.now()
            
            # 获取文件路径
            file_path = task_data.get("file_path", "")
            if not file_path:
                raise ValueError("缺少文件路径")
            
            # 执行深度分析
            print(f"开始深度分析: {file_path}")
            result = await self._analyze_file(file_path, task_data.get("options", {}))
            
            # 更新任务结果
            self.tasks[task_id]["status"] = TaskStatus.COMPLETED
            self.tasks[task_id]["completed_at"] = datetime.now()
            self.tasks[task_id]["result"] = result
            
        except Exception as e:
            print(f"任务处理失败: {e}")
            self.tasks[task_id]["status"] = TaskStatus.FAILED
            self.tasks[task_id]["error"] = str(e)
            self.tasks[task_id]["completed_at"] = datetime.now()
    
    async def _analyze_file(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """分析单个文件"""
        try:
            start_time = time.time()
            file_path = Path(file_path)
            
            # 如果是单文件，创建一个临时项目结构
            temp_dir = None
            if file_path.is_file():
                # 创建临时目录
                temp_dir = Path(tempfile.mkdtemp())
                temp_project = temp_dir / "project"
                temp_project.mkdir(parents=True)
                
                # 复制文件到临时项目
                shutil.copy2(file_path, temp_project / file_path.name)
                project_path = str(temp_project)
            else:
                project_path = str(file_path)
            
            # 执行项目分析
            analysis_result = await self.analyze_project(project_path)
            
            # 清理临时目录
            if temp_dir and temp_dir.exists():
                shutil.rmtree(temp_dir)
            
            # 格式化结果
            formatted_result = {
                "file_path": str(file_path),
                "analysis_type": "deep",
                "agent_id": "code_analysis_agent",
                "files_analyzed": 1,
                "issues_found": len(analysis_result.get("issues", [])),
                "took": time.time() - start_time,
                "summary": "深度代码分析完成",
                "analysis_result": analysis_result
            }
            
            return formatted_result
            
        except Exception as e:
            print(f"文件分析失败: {e}")
            return {
                "file_path": str(file_path),
                "analysis_type": "deep",
                "agent_id": "code_analysis_agent", 
                "files_analyzed": 0,
                "issues_found": 0,
                "error": str(e),
                "summary": f"分析失败: {e}"
            }
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        return {
            "task_id": task_id,
            "agent_id": self.agent_id,
            "status": task["status"].value,
            "created_at": task["created_at"].isoformat(),
            "started_at": task.get("started_at").isoformat() if task.get("started_at") else None,
            "completed_at": task.get("completed_at").isoformat() if task.get("completed_at") else None,
            "result": task.get("result"),
            "error": task.get("error")
        }
    
    def get_capabilities(self) -> List[str]:
        """获取agent能力"""
        return [
            "deep_code_analysis",
            "ai_analysis", 
            "project_structure_analysis",
            "quality_assessment",
            "architecture_analysis"
        ]
    
    async def get_metrics(self) -> Dict[str, Any]:
        """获取agent指标"""
        return {
            "total_tasks": len(self.tasks),
            "completed_tasks": len([t for t in self.tasks.values() if t["status"] == TaskStatus.COMPLETED]),
            "failed_tasks": len([t for t in self.tasks.values() if t["status"] == TaskStatus.FAILED]),
            "is_running": self.is_running
        }
    
    async def initialize(self) -> bool:
        """初始化agent"""
        try:
            print("初始化CodeAnalysisAgent...")
            # 这里可以添加具体的初始化逻辑
            return True
        except Exception as e:
            print(f"CodeAnalysisAgent初始化失败: {e}")
            return False
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理任务的抽象方法实现"""
        try:
            file_path = task_data.get("file_path", "")
            options = task_data.get("options", {})
            
            if not file_path:
                return {"error": "缺少文件路径", "success": False}
            
            # 执行分析
            result = await self._analyze_file(file_path, options)
            return {"success": True, "result": result}
            
        except Exception as e:
            return {"error": str(e), "success": False}
