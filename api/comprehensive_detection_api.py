"""
综合检测API
统一的检测入口，集成静态检测和动态检测功能
"""

import asyncio
import tempfile
import os
import json
import sys
import httpx
import zipfile
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Form
from pydantic import BaseModel, Field

# 导入检测组件
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from agents.dynamic_detection_agent.agent import DynamicDetectionAgent
from agents.bug_detection_agent.agent import BugDetectionAgent
from api.deepseek_config import deepseek_config

# 数据模型
class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(True, description="是否成功")
    message: str = Field("", description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息")

class DetectionRequest(BaseModel):
    """检测请求模型"""
    static_analysis: bool = Field(True, description="是否进行静态分析")
    dynamic_monitoring: bool = Field(True, description="是否进行动态监控")
    runtime_analysis: bool = Field(True, description="是否进行运行时分析")

# 创建APIRouter
router = APIRouter()

# 全局管理器引用（在 main_api.py 中设置）
_coordinator_manager = None
_agent_manager = None

def set_managers(coord_mgr, agent_mgr):
    """设置全局管理器引用"""
    global _coordinator_manager, _agent_manager
    _coordinator_manager = coord_mgr
    _agent_manager = agent_mgr

# 全局检测器（保留用于直接调用，作为备用方案）
dynamic_agent = DynamicDetectionAgent({
    "monitor_interval": 5,
    "alert_thresholds": {
        "cpu_threshold": 80,
        "memory_threshold": 85,
        "disk_threshold": 90,
        "network_threshold": 80
    },
    "enable_web_app_test": False,
    "enable_dynamic_detection": True,
    "enable_flask_specific_tests": True,
    "enable_server_testing": True
})

# 检查是否启用Docker支持（通过环境变量，默认禁用）
use_docker = os.getenv("USE_DOCKER", "false").lower() == "true"

static_agent = BugDetectionAgent({
    "enable_ai_analysis": True,
    "analysis_depth": "comprehensive",
    "use_docker": use_docker
})

# 注意：动态检测不使用Docker，它直接使用本地虚拟环境

class ComprehensiveDetector:
    """综合检测器，集成静态检测和动态检测功能"""
    
    def __init__(self, static_agent, dynamic_agent):
        self.static_agent = static_agent
        self.dynamic_agent = dynamic_agent
        self.enable_web_app_test = False
        self.enable_dynamic_detection = True
        self.enable_flask_specific_tests = True
        self.enable_server_testing = True
    
    async def detect_defects(self, zip_file_path: str, 
                           static_analysis: bool = True,
                           dynamic_monitoring: bool = True,
                           runtime_analysis: bool = True,
                           enable_web_app_test: bool = False,
                           enable_dynamic_detection: bool = True,
                           enable_flask_specific_tests: bool = True,
                           enable_server_testing: bool = True,
                           # 静态检测工具选择
                           enable_pylint: bool = True,
                           enable_mypy: bool = True,
                           enable_semgrep: bool = True,
                           enable_ruff: bool = True,
                           enable_bandit: bool = True,
                           enable_llm_filter: bool = True) -> Dict[str, Any]:
        """执行综合检测"""
        # 设置enable_web_app_test属性，并同步到dynamic_agent
        self.enable_web_app_test = enable_web_app_test
        if hasattr(self.dynamic_agent, 'enable_web_app_test'):
            self.dynamic_agent.enable_web_app_test = enable_web_app_test
        
        results = {
            "detection_type": "comprehensive",
            "timestamp": datetime.now().isoformat(),
            "zip_file": zip_file_path,
            "analysis_options": {
                "static_analysis": static_analysis,
                "dynamic_monitoring": dynamic_monitoring,
                "runtime_analysis": runtime_analysis,
                "enable_web_app_test": enable_web_app_test,
                "enable_dynamic_detection": enable_dynamic_detection,
                "enable_flask_specific_tests": enable_flask_specific_tests,
                "enable_server_testing": enable_server_testing,
                # 静态检测工具选择
                "enable_pylint": enable_pylint,
                "enable_mypy": enable_mypy,
                "enable_semgrep": enable_semgrep,
                "enable_ruff": enable_ruff,
                "enable_bandit": enable_bandit,
                "enable_llm_filter": enable_llm_filter
            }
        }
        
        try:
            # 检查文件大小
            file_size = os.path.getsize(zip_file_path)
            max_size = 50 * 1024 * 1024  # 50MB限制
            
            if file_size > max_size:
                results["error"] = f"文件过大 ({file_size // (1024*1024)}MB > {max_size // (1024*1024)}MB)"
                return results
            
            # 使用BugDetectionAgent的extract_project方法来解压项目并创建虚拟环境
            print(f"🔧 开始解压项目并创建虚拟环境: {zip_file_path}")
            print(f"⏱️  注意：虚拟环境创建和依赖安装可能需要较长时间（最多5分钟）...")
            extract_dir = None  # 初始化为None，确保在所有情况下都有值
            try:
                # 设置更长的超时时间，给虚拟环境创建和依赖安装足够时间
                # 虚拟环境创建可能需要30-180秒，依赖安装可能需要1-5分钟
                extract_dir = await asyncio.wait_for(
                    self.static_agent.extract_project(zip_file_path),
                    timeout=300.0  # 增加到5分钟（300秒）
                )
                print(f"✅ 项目解压完成，虚拟环境已创建: {extract_dir}")
            except asyncio.TimeoutError:
                print("⚠️ 虚拟环境创建超时（5分钟），使用简单解压模式")
                print("   提示：如果项目依赖较多，建议启用Docker或增加超时时间")
                try:
                    extract_dir = await self._simple_extract_project(zip_file_path)
                    results["warning"] = "虚拟环境创建超时（5分钟），使用简单解压模式。如需完整功能，建议启用Docker或增加超时时间"
                except Exception as e2:
                    print(f"❌ 简单解压也失败: {e2}")
                    extract_dir = None
                    results["error"] = f"项目解压失败: {e2}"
            except KeyboardInterrupt:
                print("⚠️ 虚拟环境创建被中断，使用简单解压模式")
                try:
                    extract_dir = await self._simple_extract_project(zip_file_path)
                    results["warning"] = "虚拟环境创建被中断，使用简单解压模式"
                except Exception as e2:
                    print(f"❌ 简单解压也失败: {e2}")
                    extract_dir = None
                    results["error"] = f"项目解压失败: {e2}"
            except Exception as e:
                print(f"❌ 项目解压失败: {e}")
                import traceback
                print(f"错误详情:\n{traceback.format_exc()}")
                # 如果虚拟环境创建失败，尝试简单的文件解压
                try:
                    extract_dir = await self._simple_extract_project(zip_file_path)
                    results["warning"] = f"虚拟环境创建失败，使用简单解压模式: {e}"
                except Exception as e2:
                    print(f"❌ 简单解压也失败: {e2}")
                    extract_dir = None
                    results["error"] = f"项目解压失败: {e2}"
            
            # 检查extract_dir是否有效
            if not extract_dir:
                print("❌ 无法获取有效的解压目录，终止检测")
                results["error"] = "无法解压项目文件"
                return results
            
            results["extracted_path"] = extract_dir
            results["files"] = self._list_files(extract_dir)
            
            # 限制文件数量，避免处理过多文件
            if len(results["files"]) > 1000:
                results["warning"] = f"文件数量过多 ({len(results['files'])} > 1000)，将进行采样分析"
                results["files"] = results["files"][:1000]  # 只取前1000个文件
            
            # ========== 步骤1: 执行初步代码分析 ==========
            print("🔍 开始初步代码分析...")
            preliminary_analysis = await self._perform_preliminary_analysis(extract_dir)
            results["preliminary_analysis"] = preliminary_analysis
            
            # 生成仓库结构文件
            repository_structure_file = await self._generate_repository_structure(extract_dir)
            if repository_structure_file:
                results["repository_structure_file"] = repository_structure_file
            
            # 保存初步分析结果供静态检测使用
            self._current_preliminary_analysis = preliminary_analysis
            
            # ========== 步骤2: 执行静态分析和动态检测 ==========
            # 并行执行静态分析和动态检测
            tasks = []
            
            # 静态分析
            if static_analysis:
                tasks.append(self._perform_static_analysis_async(
                    extract_dir,
                    enable_pylint=enable_pylint,
                    enable_mypy=enable_mypy,
                    enable_semgrep=enable_semgrep,
                    enable_ruff=enable_ruff,
                    enable_bandit=enable_bandit,
                    enable_llm_filter=enable_llm_filter
                ))
            
            # 动态监控
            if dynamic_monitoring:
                tasks.append(self._perform_dynamic_monitoring_async())
            
            # 运行时分析
            if runtime_analysis:
                tasks.append(self._perform_runtime_analysis_async(extract_dir))
            
            # 动态缺陷检测
            if enable_dynamic_detection:
                tasks.append(self._perform_dynamic_detection_async(extract_dir, enable_flask_specific_tests, enable_server_testing))
            
            # 等待所有任务完成（添加超时机制）
            if tasks:
                print(f"🔄 [DEBUG] 开始等待 {len(tasks)} 个检测任务完成...")
                try:
                    # 设置30分钟超时，给检测足够时间
                    task_results = await asyncio.wait_for(
                        asyncio.gather(*tasks, return_exceptions=True),
                        timeout=1800.0  # 30分钟（1800秒）
                    )
                    print(f"✅ [DEBUG] 所有检测任务完成，开始处理结果...")
                except asyncio.TimeoutError:
                    print("⚠️ 检测任务超时（30分钟），使用默认结果")
                    results["warning"] = "检测任务超时，部分功能可能未完成"
                    # 创建默认的失败结果
                    task_results = []
                    for i, task in enumerate(tasks):
                        if i == 0 and static_analysis:
                            task_results.append({"error": "检测超时", "issues": []})
                        elif i == 1 and dynamic_monitoring:
                            task_results.append({"error": "检测超时", "alerts": []})
                        elif i == 2 and runtime_analysis:
                            task_results.append({"error": "检测超时", "execution_successful": False})
                        elif i == 3 and enable_dynamic_detection:
                            task_results.append({"error": "检测超时", "tests_completed": False})
                except Exception as gather_error:
                    print(f"❌ [DEBUG] asyncio.gather执行异常: {gather_error}")
                    import traceback
                    traceback.print_exc()
                    # 创建默认的失败结果
                    task_results = []
                    for i, task in enumerate(tasks):
                        if i == 0 and static_analysis:
                            task_results.append({"error": f"任务执行异常: {gather_error}", "issues": []})
                        elif i == 1 and dynamic_monitoring:
                            task_results.append({"error": f"任务执行异常: {gather_error}", "alerts": []})
                        elif i == 2 and runtime_analysis:
                            task_results.append({"error": f"任务执行异常: {gather_error}", "execution_successful": False})
                        elif i == 3 and enable_dynamic_detection:
                            task_results.append({"error": f"任务执行异常: {gather_error}", "tests_completed": False})
                
                # 处理结果
                print(f"📊 [DEBUG] 开始处理任务结果，task_results数量: {len(task_results) if task_results else 0}")
                task_index = 0
                if static_analysis:
                    print(f"📊 [DEBUG] 处理静态分析结果，索引: {task_index}")
                    if isinstance(task_results[task_index], Exception):
                        print(f"⚠️ [DEBUG] 静态分析任务异常: {task_results[task_index]}")
                        results["static_analysis"] = {"error": str(task_results[task_index]), "issues": []}
                    else:
                        print(f"✅ [DEBUG] 静态分析任务完成，结果类型: {type(task_results[task_index])}")
                        results["static_analysis"] = task_results[task_index]
                    task_index += 1
                
                if dynamic_monitoring:
                    print(f"📊 [DEBUG] 处理动态监控结果，索引: {task_index}")
                    if isinstance(task_results[task_index], Exception):
                        print(f"⚠️ [DEBUG] 动态监控任务异常: {task_results[task_index]}")
                        results["dynamic_monitoring"] = {"error": str(task_results[task_index]), "alerts": []}
                    else:
                        results["dynamic_monitoring"] = task_results[task_index]
                    task_index += 1
                
                if runtime_analysis:
                    print(f"📊 [DEBUG] 处理运行时分析结果，索引: {task_index}")
                    if isinstance(task_results[task_index], Exception):
                        print(f"⚠️ [DEBUG] 运行时分析任务异常: {task_results[task_index]}")
                        results["runtime_analysis"] = {"error": str(task_results[task_index]), "execution_successful": False}
                    else:
                        results["runtime_analysis"] = task_results[task_index]
                    task_index += 1
                
                if enable_dynamic_detection:
                    print(f"📊 [DEBUG] 处理动态检测结果，索引: {task_index}")
                    if isinstance(task_results[task_index], Exception):
                        print(f"⚠️ [DEBUG] 动态检测任务异常: {task_results[task_index]}")
                        results["dynamic_detection"] = {"error": str(task_results[task_index]), "tests_completed": False}
                    else:
                        results["dynamic_detection"] = task_results[task_index]
            
            # 生成综合摘要
            print("📝 [DEBUG] 开始生成综合摘要...")
            results["summary"] = self._generate_summary(results)
            print("✅ [DEBUG] 综合摘要生成完成")
            
            # 清理临时目录和虚拟环境
            try:
                if extract_dir and os.path.exists(extract_dir):
                    await self.static_agent.cleanup_project_environment(extract_dir)
                    print(f"✅ 项目环境清理完成: {extract_dir}")
                else:
                    print(f"⚠️ 跳过环境清理（路径无效）: {extract_dir}")
            except Exception as cleanup_error:
                print(f"⚠️ 环境清理失败: {cleanup_error}")
                import traceback
                traceback.print_exc()
                # 回退到手动清理
                if extract_dir and os.path.exists(extract_dir):
                    try:
                        shutil.rmtree(extract_dir, ignore_errors=True)
                    except Exception as e:
                        print(f"⚠️ 手动清理也失败: {e}")
            # 合并静态和动态检测缺陷清单，生成统一格式
            print("📋 [DEBUG] 开始合并缺陷清单...")
            merged_defects = []
            try:
                merged_defects = self._merge_defects_list(results, extract_dir)
                results["merged_defects"] = merged_defects
                print(f"📋 [DEBUG] 合并后的缺陷数量: {len(merged_defects)}")
            except Exception as merge_error:
                print(f"❌ [DEBUG] 合并缺陷清单失败: {merge_error}")
                import traceback
                traceback.print_exc()
                results["merged_defects"] = []
                merged_defects = []
                results["warning"] = results.get("warning", "") + f" 合并缺陷清单失败: {merge_error}"
            
            if merged_defects:
                print(f"📋 [DEBUG] 前3个缺陷示例:")
                for i, defect in enumerate(merged_defects[:3], 1):
                    print(f"  {i}. 文件: {defect.get('file', 'N/A')}, 行号: {defect.get('line', 'N/A')}, 来源: {defect.get('source', 'N/A')}")
            else:
                print("⚠️ [DEBUG] 警告: merged_defects 为空！")
            
            # 生成任务信息JSON文件供修复工作流使用（保存到永久位置）
            print("📝 [DEBUG] 开始生成任务信息JSON...")
            try:
                task_info_path = self._generate_task_info_json(merged_defects, extract_dir)
                print(f"📝 [DEBUG] task_info_path = {task_info_path}")
            except Exception as task_info_error:
                print(f"❌ [DEBUG] 生成任务信息JSON失败: {task_info_error}")
                import traceback
                traceback.print_exc()
                task_info_path = None
                results["warning"] = results.get("warning", "") + f" 生成任务信息JSON失败: {task_info_error}"
            if task_info_path:
                print(f"📝 [DEBUG] 检查文件是否存在: {os.path.exists(task_info_path)}")
            else:
                print("⚠️ [DEBUG] 警告: task_info_path 为 None，可能没有生成任务信息")
            
            if task_info_path and os.path.exists(task_info_path):
                # 将任务信息文件复制到结果目录（使用绝对路径，确保保存在项目根目录）
                # 获取项目根目录（API文件所在目录的父目录）
                api_dir = Path(__file__).parent
                project_root = api_dir.parent
                results_dir = project_root / "comprehensive_detection_results"
                results_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                permanent_task_info_file = results_dir / f"agent_task_info_{timestamp}.json"
                permanent_task_info_file_abs = permanent_task_info_file.resolve()
                print(f"📝 [DEBUG] 复制任务信息文件到永久位置:")
                print(f"   相对路径: {permanent_task_info_file}")
                print(f"   绝对路径: {permanent_task_info_file_abs}")
                shutil.copy2(task_info_path, permanent_task_info_file_abs)
                results["task_info_file"] = str(permanent_task_info_file_abs)
                print(f"✅ [DEBUG] 文件已复制，验证文件存在: {permanent_task_info_file_abs.exists()}")
                # 同时将任务信息内容包含在结果中
                with open(permanent_task_info_file_abs, 'r', encoding='utf-8') as f:
                    task_info_data = json.load(f)
                    results["task_info"] = task_info_data
                print(f"✅ [DEBUG] 任务信息已保存，任务数量: {len(task_info_data)}")
                print(f"📝 [DEBUG] 注意: 任务信息中的文件路径为绝对路径")
                print(f"📝 [DEBUG] 临时目录: {extract_dir}")
                print(f"📝 [DEBUG] 临时目录将保留，以便修复Agent使用")
            else:
                print("⚠️ [DEBUG] 警告: 未保存任务信息文件到永久位置")
                results["task_info_file"] = None
                results["task_info"] = []
            
            # 不删除临时目录，保留上传的文件以便后续修复使用
            # 注意：临时目录会一直保留，需要手动清理或定期清理
            print(f"📝 [DEBUG] 保留临时目录: {extract_dir}")
            print(f"⚠️ [DEBUG] 注意: 临时目录未删除，需要定期清理以释放磁盘空间")
            
            return results
            
        except Exception as e:
            results["error"] = str(e)
            # 即使出现错误也要生成summary
            results["summary"] = self._generate_summary(results)
            return results
    
    async def _simple_extract_project(self, zip_file_path: str) -> str:
        """简单的项目解压方法（不创建虚拟环境）"""
        try:
            import zipfile
            import tempfile
            
            # 创建临时解压目录
            temp_dir = tempfile.mkdtemp(prefix="comprehensive_extract_")
            
            # 解压ZIP文件
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            print(f"⚠️ 使用简单解压模式: {temp_dir}")
            return temp_dir
            
        except Exception as e:
            print(f"❌ 简单解压也失败: {e}")
            raise e
    
    def _list_files(self, project_path: str) -> List[str]:
        """列出项目文件（排除虚拟环境和缓存文件）"""
        files = []
        skip_dirs = {'venv', '__pycache__', '.git', 'node_modules', '.pytest_cache', '.mypy_cache'}
        
        for root, dirs, filenames in os.walk(project_path):
            # 跳过不需要的目录
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for filename in filenames:
                # 跳过隐藏文件和缓存文件
                if filename.startswith('.') or filename.endswith(('.pyc', '.pyo', '.pyd')):
                    continue
                    
                file_path = os.path.relpath(os.path.join(root, filename), project_path)
                files.append(file_path)
        return files
    
    async def _perform_preliminary_analysis(self, project_path: str) -> Dict[str, Any]:
        """执行初步代码分析（项目结构、代码质量、依赖关系）"""
        try:
            from agents.code_analysis_agent.agent import CodeAnalysisAgent
            
            # 初始化代码分析代理
            code_analysis_agent = CodeAnalysisAgent({
                "enable_ai_analysis": True,
                "analysis_depth": "comprehensive"
            })
            
            print("  📊 执行项目结构分析...")
            project_structure = await code_analysis_agent.project_analyzer.analyze_project_structure(project_path)
            
            print("  📈 执行代码质量分析...")
            print("     ⏳ 这可能需要几分钟，请耐心等待...")
            try:
                # 为代码质量分析添加超时保护（最多3分钟）
                code_quality = await asyncio.wait_for(
                    code_analysis_agent.code_analyzer.analyze_code_quality(project_path),
                    timeout=180.0  # 3分钟超时
                )
                print("     ✅ 代码质量分析完成")
            except asyncio.TimeoutError:
                print("     ⚠️ 代码质量分析超时（3分钟），使用简化结果")
                code_quality = {
                    'total_files': 0,
                    'analyzed_files': 0,
                    'error': '分析超时',
                    'file_analysis': []
                }
            except Exception as e:
                print(f"     ⚠️ 代码质量分析失败: {e}，使用简化结果")
                code_quality = {
                    'total_files': 0,
                    'analyzed_files': 0,
                    'error': str(e),
                    'file_analysis': []
                }
            
            print("  🔗 执行依赖关系分析...")
            try:
                # 为依赖分析添加超时保护（最多1分钟）
                dependencies = await asyncio.wait_for(
                    code_analysis_agent.dependency_analyzer.analyze_dependencies(project_path),
                    timeout=60.0  # 1分钟超时
                )
                print("     ✅ 依赖关系分析完成")
            except asyncio.TimeoutError:
                print("     ⚠️ 依赖关系分析超时（1分钟），使用简化结果")
                dependencies = {
                    'error': '分析超时',
                    'dependencies': []
                }
            except Exception as e:
                print(f"     ⚠️ 依赖关系分析失败: {e}，使用简化结果")
                dependencies = {
                    'error': str(e),
                    'dependencies': []
                }
            
            print("✅ 初步代码分析完成")
            
            return {
                "success": True,
                "project_structure": project_structure,
                "code_quality": code_quality,
                "dependencies": dependencies
            }
        except Exception as e:
            print(f"❌ 初步代码分析失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "project_structure": {},
                "code_quality": {},
                "dependencies": {}
            }
    
    async def _generate_repository_structure(self, project_path: str) -> Optional[str]:
        """生成仓库结构文件（tree格式）"""
        try:
            from tools.repository_structure_generator import repository_structure_generator
            
            # 创建输出目录（使用绝对路径）
            api_dir = Path(__file__).parent
            project_root = api_dir.parent
            structure_dir = project_root / "comprehensive_detection_results"
            structure_dir.mkdir(exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            structure_file = structure_dir / f"repository_structure_{timestamp}.txt"
            
            # 生成并保存树形结构
            success = repository_structure_generator.save_tree_structure(
                project_path, 
                str(structure_file),
                max_depth=10
            )
            
            if success:
                print(f"✅ 仓库结构文件已生成: {structure_file}")
                return str(structure_file)
            else:
                print("⚠️ 仓库结构文件生成失败")
                return None
        except Exception as e:
            print(f"❌ 生成仓库结构文件失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _perform_static_analysis_async(self, project_path: str,
                                             enable_pylint: bool = True,
                                             enable_mypy: bool = True,
                                             enable_semgrep: bool = True,
                                             enable_ruff: bool = True,
                                             enable_bandit: bool = True,
                                             enable_llm_filter: bool = True) -> Dict[str, Any]:
        """异步执行静态分析 - 优先使用Coordinator，否则直接调用Agent"""
        try:
            # 优先使用Coordinator（如果可用）
            if _coordinator_manager and _coordinator_manager.coordinator:
                coordinator = _coordinator_manager.coordinator
                
                try:
                    # 获取初步分析结果（如果已执行）
                    preliminary_analysis = None
                    if hasattr(self, '_current_preliminary_analysis'):
                        preliminary_analysis = self._current_preliminary_analysis
                    
                    print(f"🚀 [Coordinator] 通过Coordinator创建静态检测任务: {project_path}")
                    print(f"   工具选择: pylint={enable_pylint}, mypy={enable_mypy}, semgrep={enable_semgrep}, ruff={enable_ruff}, bandit={enable_bandit}")
                    
                    # 创建任务数据
                    # 注意：project_path 已经是解压后的目录，不是zip文件
                    # 应该使用 project_path 而不是 file_path，避免再次解压
                    task_data = {
                        "project_path": project_path,  # 使用 project_path 而不是 file_path
                        "analysis_type": "project",
                        "options": {
                            "enable_static": True,
                            "enable_pylint": enable_pylint,
                            "enable_mypy": enable_mypy,
                            "enable_semgrep": enable_semgrep,
                            "enable_ruff": enable_ruff,
                            "enable_bandit": enable_bandit,
                            "enable_llm_filter": enable_llm_filter,
                            "enable_ai_analysis": True,
                            "preliminary_analysis": preliminary_analysis,
                            "pylint_directory_mode": False,
                            "max_parallel_files": 10,
                            "max_issues_to_return": 1000
                        }
                    }
                    
                    # 通过Coordinator创建任务并分配
                    task_id = await coordinator.create_task('detect_bugs', task_data)
                    await coordinator.assign_task(task_id, 'bug_detection_agent')
                    
                    print(f"✅ [Coordinator] 静态检测任务已创建并分配: {task_id}")
                    
                    # 等待任务完成（最多30分钟）
                    try:
                        analysis_result = await coordinator.task_manager.get_task_result(task_id, timeout=1800.0)
                        print(f"✅ [Coordinator] 静态检测任务完成")
                        
                        if analysis_result and analysis_result.get("success", False):
                            detection_results = analysis_result.get("detection_results", {})
                            if preliminary_analysis and preliminary_analysis.get("success"):
                                detection_results["preliminary_analysis"] = preliminary_analysis
                            return detection_results
                        else:
                            return {
                                "error": analysis_result.get("error", "静态分析失败") if analysis_result else "任务执行失败",
                                "issues": [],
                                "statistics": {
                                    "total_files": 0,
                                    "total_lines": 0,
                                    "average_complexity": 0,
                                    "maintainability_score": 0
                                },
                                "files_analyzed": 0
                            }
                    except Exception as e:
                        print(f"⚠️ [Coordinator] 获取静态检测结果失败: {e}，回退到直接调用")
                        import traceback
                        traceback.print_exc()
                        # 回退到直接调用方式
                except Exception as e:
                    print(f"⚠️ [Coordinator] Coordinator调用异常: {e}，回退到直接调用")
                    import traceback
                    traceback.print_exc()
                    # 回退到直接调用方式
            
            # 备用方案：直接调用Agent（如果Coordinator不可用）
            print(f"⚠️ [Direct] Coordinator不可用，直接调用静态检测Agent")
            
            # 确保静态检测agent已初始化（工具初始化）
            if not hasattr(self.static_agent, '_tools_initialized') or not self.static_agent._tools_initialized:
                print("🔧 初始化静态检测工具...")
                try:
                    # 添加超时保护，避免初始化卡死
                    await asyncio.wait_for(
                        self.static_agent.initialize(),
                        timeout=30.0  # 30秒超时
                    )
                    self.static_agent._tools_initialized = True
                    print("✅ 静态检测工具初始化完成")
                except asyncio.TimeoutError:
                    print("⚠️ 静态检测工具初始化超时，继续使用部分工具")
                    self.static_agent._tools_initialized = True  # 标记为已初始化，避免重复尝试
                except Exception as e:
                    print(f"⚠️ 静态检测工具初始化异常: {e}")
                    self.static_agent._tools_initialized = True  # 标记为已初始化，避免重复尝试
            
            # 获取初步分析结果（如果已执行）
            preliminary_analysis = None
            if hasattr(self, '_current_preliminary_analysis'):
                preliminary_analysis = self._current_preliminary_analysis
            
            print(f"🚀 开始调用静态检测agent分析项目: {project_path}")
            print(f"   工具选择: pylint={enable_pylint}, mypy={enable_mypy}, semgrep={enable_semgrep}, ruff={enable_ruff}, bandit={enable_bandit}")
            
            # 调用静态检测agent（传递初步分析结果和工具选择）
            # 添加超时保护和进度日志
            try:
                analysis_result = await asyncio.wait_for(
                    self.static_agent.analyze_project(project_path, {
                        "enable_static": True,
                        "enable_pylint": enable_pylint,
                        "enable_mypy": enable_mypy,
                        "enable_semgrep": enable_semgrep,
                        "enable_ruff": enable_ruff,
                        "enable_bandit": enable_bandit,
                        "enable_llm_filter": enable_llm_filter,
                        "enable_ai_analysis": True,
                        "preliminary_analysis": preliminary_analysis,  # 传递初步分析结果
                        "pylint_directory_mode": False,  # 禁用目录模式，使用单文件模式以确保问题不被过滤掉
                        "max_parallel_files": 10,  # 并行文件数限制
                        "max_issues_to_return": 1000  # 限制返回的问题数量，避免数据过大
                    }),
                    timeout=1800.0  # 30分钟超时
                )
                print(f"✅ 静态检测分析完成")
            except asyncio.TimeoutError:
                print(f"⚠️ 静态检测分析超时（30分钟），返回部分结果")
                analysis_result = {
                    "success": False,
                    "error": "静态检测分析超时",
                    "detection_results": {
                        "project_path": project_path,
                        "total_issues": 0,
                        "issues": [],
                        "summary": {"error_count": 0, "warning_count": 0, "info_count": 0}
                    }
                }
            except Exception as e:
                print(f"❌ 静态检测分析异常: {e}")
                import traceback
                print(f"错误详情:\n{traceback.format_exc()}")
                analysis_result = {
                    "success": False,
                    "error": str(e),
                    "detection_results": {
                        "project_path": project_path,
                        "total_issues": 0,
                        "issues": [],
                        "summary": {"error_count": 0, "warning_count": 0, "info_count": 0}
                    }
                }
            
            if analysis_result.get("success", False):
                detection_results = analysis_result.get("detection_results", {})
                # 调试：检查结果结构
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"静态分析结果: success={analysis_result.get('success')}, detection_results keys={list(detection_results.keys()) if detection_results else 'None'}")
                if detection_results:
                    logger.info(f"检测到的问题数: {len(detection_results.get('issues', []))}")
                    logger.info(f"工具覆盖率: {detection_results.get('tool_coverage', {})}")
                # 如果有初步分析结果，合并进去
                if preliminary_analysis and preliminary_analysis.get("success"):
                    detection_results["preliminary_analysis"] = preliminary_analysis
                return detection_results
            else:
                return {
                    "error": analysis_result.get("error", "静态分析失败"),
                    "issues": [],
                    "statistics": {
                        "total_files": 0,
                        "total_lines": 0,
                        "average_complexity": 0,
                        "maintainability_score": 0
                    },
                    "files_analyzed": 0
                }
        except Exception as e:
            return {
                "error": str(e), 
                "issues": [],
                "statistics": {
                    "total_files": 0,
                    "total_lines": 0,
                    "average_complexity": 0,
                    "maintainability_score": 0
                },
                "files_analyzed": 0
            }
    
    async def _perform_dynamic_monitoring_async(self) -> Dict[str, Any]:
        """异步执行动态监控"""
        try:
            return await self.dynamic_agent.start_monitoring(duration=60)
        except Exception as e:
            return {"error": str(e), "alerts": []}
    
    async def _perform_runtime_analysis_async(self, project_path: str) -> Dict[str, Any]:
        """异步执行运行时分析"""
        try:
            return await self.dynamic_agent.perform_runtime_analysis(project_path)
        except Exception as e:
            return {"error": str(e), "execution_successful": False}
    
    async def _perform_dynamic_detection_async(self, project_path: str, enable_flask_tests: bool = True, enable_server_tests: bool = True) -> Dict[str, Any]:
        """异步执行动态缺陷检测 - 优先使用Coordinator，否则直接调用Agent"""
        try:
            # 优先使用Coordinator（如果可用且dynamic_detection_agent已注册）
            if _coordinator_manager and _coordinator_manager.coordinator:
                coordinator = _coordinator_manager.coordinator
                
                try:
                    # 检查是否有dynamic_detection_agent（可能未注册）
                    if 'dynamic_detection_agent' in coordinator.agents:
                        print(f"🚀 [Coordinator] 通过Coordinator创建动态检测任务: {project_path}")
                        
                        # 创建任务数据
                        task_data = {
                            "project_path": project_path,
                            "enable_flask_tests": enable_flask_tests,
                            "enable_server_tests": enable_server_tests,
                            "enable_web_app_test": self.enable_web_app_test,
                            "enable_dynamic_detection": self.enable_dynamic_detection,
                            "enable_flask_specific_tests": self.enable_flask_specific_tests,
                            "enable_server_testing": self.enable_server_testing
                        }
                        
                        # 通过Coordinator创建任务并分配
                        task_id = await coordinator.create_task('dynamic_detect', task_data)
                        await coordinator.assign_task(task_id, 'dynamic_detection_agent')
                        
                        print(f"✅ [Coordinator] 动态检测任务已创建并分配: {task_id}")
                        
                        # 等待任务完成（最多30分钟）
                        try:
                            result = await coordinator.task_manager.get_task_result(task_id, timeout=1800.0)
                            print(f"✅ [Coordinator] 动态检测任务完成")
                            return result if result else {"error": "任务执行失败", "tests_completed": False}
                        except Exception as e:
                            print(f"⚠️ [Coordinator] 获取动态检测结果失败: {e}，回退到直接调用")
                            import traceback
                            traceback.print_exc()
                            # 回退到直接调用方式
                    else:
                        print(f"⚠️ [Coordinator] dynamic_detection_agent未注册，使用直接调用")
                except Exception as e:
                    print(f"⚠️ [Coordinator] Coordinator调用异常: {e}，回退到直接调用")
                    import traceback
                    traceback.print_exc()
                    # 回退到直接调用方式
            
            # 备用方案：直接调用Agent
            print(f"⚠️ [Direct] 直接调用动态检测Agent")
            return await self.dynamic_agent.perform_dynamic_detection(project_path, enable_flask_tests, enable_server_tests)
        except Exception as e:
            return {"error": str(e), "tests_completed": False}
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成综合摘要"""
        summary = {
            "total_files": len(results.get("files", [])),
            "analysis_completed": not bool(results.get("error")),
            "issues_summary": {}
        }
        
        # 统计问题数量
        total_issues = 0
        critical_issues = 0
        warning_issues = 0
        info_issues = 0
        
        # 统计静态分析问题
        if "static_analysis" in results:
            static = results["static_analysis"]
            issues = static.get("issues", [])
            statistics = static.get("statistics", {})
            
            summary["issues_summary"]["static"] = {
                "analysis_type": static.get("analysis_type", "unknown"),
                "files_analyzed": static.get("files_analyzed", 0),
                "issues_found": len(issues),
                "total_files": statistics.get("total_files", 0),
                "total_lines": statistics.get("total_lines", 0),
                "average_complexity": statistics.get("average_complexity", 0),
                "maintainability_score": statistics.get("maintainability_score", 0),
                "issues_by_severity": statistics.get("issues_by_severity", {}),
                "issues_by_type": statistics.get("issues_by_type", {}),
                "issues_by_tool": statistics.get("issues_by_tool", {})
            }
            
            # 统计问题严重程度
            for issue in issues:
                total_issues += 1
                severity = issue.get("severity", "info").lower()
                if severity == "error" or severity == "critical":
                    critical_issues += 1
                elif severity == "warning":
                    warning_issues += 1
                else:
                    info_issues += 1
        
        # 统计动态监控结果
        if "dynamic_monitoring" in results:
            dynamic = results["dynamic_monitoring"]
            alerts = dynamic.get("alerts", [])
            summary["issues_summary"]["dynamic"] = {
                "monitoring_duration": dynamic.get("duration", 0),
                "alerts_generated": len(alerts)
            }
            
            # 统计告警数量
            for alert in alerts:
                total_issues += 1
                severity = alert.get("severity", "info").lower()
                if severity == "error" or severity == "critical":
                    critical_issues += 1
                elif severity == "warning":
                    warning_issues += 1
                else:
                    info_issues += 1
        
        # 统计运行时分析结果
        if "runtime_analysis" in results:
            runtime = results["runtime_analysis"]
            summary["issues_summary"]["runtime"] = {
                "execution_successful": runtime.get("execution_successful", False),
                "main_file": runtime.get("main_file", "unknown")
            }
            
            # 如果有运行时错误，计入问题
            if runtime.get("error"):
                total_issues += 1
                critical_issues += 1
        
        # 统计动态检测结果
        if "dynamic_detection" in results:
            dynamic_detection = results["dynamic_detection"]
            summary["issues_summary"]["dynamic_detection"] = {
                "status": dynamic_detection.get("status", "unknown"),
                "is_flask_project": dynamic_detection.get("is_flask_project", False),
                "tests_completed": dynamic_detection.get("tests_completed", False),
                "success_rate": dynamic_detection.get("success_rate", 0)
            }
            
            # 统计动态检测问题
            dynamic_issues = dynamic_detection.get("issues", [])
            for issue in dynamic_issues:
                total_issues += 1
                severity = issue.get("severity", "info").lower()
                if severity == "error" or severity == "critical":
                    critical_issues += 1
                elif severity == "warning":
                    warning_issues += 1
                else:
                    info_issues += 1
        
        # 设置整体状态
        if critical_issues > 0:
            overall_status = "error"
        elif warning_issues > 0:
            overall_status = "warning"
        elif info_issues > 0:
            overall_status = "info"
        else:
            overall_status = "good"
        
        # 生成建议
        recommendations = []
        if critical_issues > 0:
            recommendations.append("发现严重问题，建议立即修复")
        if warning_issues > 0:
            recommendations.append("发现警告问题，建议及时处理")
        
        # 检查运行时分析和动态检测的状态
        runtime_analysis = results.get("runtime_analysis", {})
        dynamic_detection = results.get("dynamic_detection", {})
        runtime_failed = not runtime_analysis.get("execution_successful", True)
        dynamic_success = dynamic_detection.get("tests_completed", False) and dynamic_detection.get("success_rate", 0) >= 100
        
        if runtime_failed:
            if dynamic_success:
                # 运行时分析失败但动态检测成功，说明项目需要Flask环境才能运行
                recommendations.append("运行时分析失败，但动态检测成功。这可能是因为项目需要Flask环境才能运行，属于正常情况")
            else:
                # 两者都失败，需要检查配置
                recommendations.append("运行时分析失败，检查项目配置和依赖")
        
        # 添加摘要字段
        summary.update({
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "warning_issues": warning_issues,
            "info_issues": info_issues,
            "overall_status": overall_status,
            "recommendations": recommendations
        })
        
        return summary
    
    def _generate_natural_language_description(self, issue: Dict[str, Any], source: str = "static") -> str:
        """
        为每个缺陷生成自然语言描述
        
        Args:
            issue: 缺陷信息字典
            source: 来源（"static" 或 "dynamic"）
        
        Returns:
            自然语言描述字符串
        """
        if source == "static":
            tool = issue.get("tool", "unknown")
            message = issue.get("message", "")
            severity = issue.get("severity", "info")
            file_path = issue.get("file", "unknown")
            line = issue.get("line", 0)
            symbol = issue.get("symbol", "")
            
            # 根据工具和问题类型生成描述
            if tool == "pylint":
                if "import" in message.lower() and "error" in message.lower():
                    return f"在 {file_path} 的第 {line} 行，存在导入错误：{message}"
                elif "missing" in message.lower() and "docstring" in message.lower():
                    return f"在 {file_path} 的第 {line} 行，缺少函数或方法的文档字符串"
                elif "unused" in message.lower():
                    return f"在 {file_path} 的第 {line} 行，存在未使用的变量或参数：{message}"
                elif severity == "error":
                    return f"在 {file_path} 的第 {line} 行，发现严重错误：{message}"
                else:
                    return f"在 {file_path} 的第 {line} 行，{tool} 检测到问题：{message}"
            
            elif tool == "mypy":
                return f"在 {file_path} 的第 {line} 行，类型检查发现问题：{message}"
            
            elif tool == "semgrep":
                rule_id = issue.get("check_id", "")
                return f"在 {file_path} 的第 {line} 行，检测到安全或代码质量问题（规则：{rule_id}）：{message}"
            
            elif tool == "ruff":
                rule_code = issue.get("code", "")
                return f"在 {file_path} 的第 {line} 行，代码规范问题（规则：{rule_code}）：{message}"
            
            elif tool == "bandit":
                test_id = issue.get("test_id", "")
                return f"在 {file_path} 的第 {line} 行，发现安全问题（检测项：{test_id}）：{message}"
            
            else:
                return f"在 {file_path} 的第 {line} 行，{tool} 检测到{severity}级别问题：{message}"
        
        elif source == "dynamic":
            issue_type = issue.get("type", "unknown")
            message = issue.get("message", "")
            file_path = issue.get("file", "unknown")
            line = issue.get("line", 0)
            
            if issue_type == "import_error":
                import_name = issue.get("import", "")
                return f"在 {file_path} 的第 {line} 行，动态检测发现导入错误：无法导入模块 '{import_name}'"
            
            elif "flask" in issue_type.lower() or "functionality" in issue_type.lower():
                return f"在 {file_path} 的第 {line} 行，Flask功能测试发现问题：{message}"
            
            elif "runtime" in issue_type.lower():
                return f"在 {file_path} 的第 {line} 行，运行时检测发现问题：{message}"
            
            elif issue_type in ["cpu_high", "memory_high", "disk_high", "network_high"]:
                return f"系统资源监控告警：{message}"
            
            else:
                return f"在 {file_path} 的第 {line} 行，动态检测发现问题：{message}"
        
        else:
            return issue.get("message", "检测到问题")
    
    def _merge_defects_list(self, results: Dict[str, Any], project_path: str) -> List[Dict[str, Any]]:
        """
        合并静态检测和动态检测的缺陷清单，生成统一格式
        
        Args:
            results: 检测结果字典
            project_path: 项目路径
        
        Returns:
            合并后的缺陷列表，每个缺陷包含：
            - description: 自然语言描述
            - file: 文件路径（相对路径）
            - line: 行号
            - severity: 严重程度
            - source: 来源（"static" 或 "dynamic"）
            - tool: 检测工具
            - original_issue: 原始问题信息
        """
        merged_defects = []
        
        # 处理静态分析结果
        if "static_analysis" in results:
            static_result = results["static_analysis"]
            if isinstance(static_result, dict) and not static_result.get("error"):
                issues = static_result.get("issues", [])
                for issue in issues:
                    file_path = issue.get("file", "")
                    line = issue.get("line", 0)
                    
                    # 转换为相对路径
                    if file_path and os.path.isabs(file_path):
                        try:
                            file_path = os.path.relpath(file_path, project_path)
                        except:
                            pass
                    
                    # 生成自然语言描述时使用相对路径
                    issue_for_desc = issue.copy()
                    issue_for_desc["file"] = file_path  # 使用已转换的相对路径
                    merged_defect = {
                        "description": self._generate_natural_language_description(issue_for_desc, "static"),
                        "file": file_path,
                        "line": line,
                        "severity": issue.get("severity", "info"),
                        "source": "static",
                        "tool": issue.get("tool", "unknown"),
                        "original_issue": issue
                    }
                    merged_defects.append(merged_defect)
        
        # 处理动态监控结果
        if "dynamic_monitoring" in results:
            dynamic_result = results["dynamic_monitoring"]
            if isinstance(dynamic_result, dict) and not dynamic_result.get("error"):
                alerts = dynamic_result.get("alerts", [])
                for alert in alerts:
                    # 动态监控告警可能没有文件信息
                    file_path = alert.get("file", "")
                    line = alert.get("line", 0)
                    
                    if file_path and os.path.isabs(file_path):
                        try:
                            file_path = os.path.relpath(file_path, project_path)
                        except:
                            pass
                    
                    # 生成自然语言描述时使用相对路径
                    alert_for_desc = alert.copy()
                    alert_for_desc["file"] = file_path if file_path else "system"
                    merged_defect = {
                        "description": self._generate_natural_language_description(alert_for_desc, "dynamic"),
                        "file": file_path if file_path else "system",
                        "line": line if line else 0,
                        "severity": alert.get("severity", "warning"),
                        "source": "dynamic",
                        "tool": "dynamic_monitoring",
                        "original_issue": alert
                    }
                    merged_defects.append(merged_defect)
        
        # 处理动态检测结果
        if "dynamic_detection" in results:
            dynamic_detection_result = results["dynamic_detection"]
            if isinstance(dynamic_detection_result, dict) and not dynamic_detection_result.get("error"):
                issues = dynamic_detection_result.get("issues", [])
                for issue in issues:
                    file_path = issue.get("file", "")
                    line = issue.get("line", 0)
                    
                    if file_path and os.path.isabs(file_path):
                        try:
                            file_path = os.path.relpath(file_path, project_path)
                        except:
                            pass
                    
                    # 生成自然语言描述时使用相对路径
                    issue_for_desc = issue.copy()
                    issue_for_desc["file"] = file_path if file_path else "unknown"
                    merged_defect = {
                        "description": self._generate_natural_language_description(issue_for_desc, "dynamic"),
                        "file": file_path if file_path else "unknown",
                        "line": line if line else 0,
                        "severity": issue.get("severity", "error"),
                        "source": "dynamic",
                        "tool": "dynamic_detection",
                        "original_issue": issue
                    }
                    merged_defects.append(merged_defect)
        
        # 按文件路径和行号排序
        merged_defects.sort(key=lambda x: (x.get("file", ""), x.get("line", 0)))
        
        return merged_defects
    
    def _generate_task_info_json(self, merged_defects: List[Dict[str, Any]], project_path: str) -> Optional[str]:
        """
        生成任务信息JSON文件供修复工作流使用
        每个缺陷生成一个独立任务，task字段为缺陷的简单描述
        
        Args:
            merged_defects: 合并后的缺陷列表
            project_path: 项目路径
        
        Returns:
            生成的任务信息JSON文件路径，如果生成失败则返回None
        """
        try:
            print(f"📝 [DEBUG] _generate_task_info_json: 输入缺陷数量={len(merged_defects)}, 项目路径={project_path}")
            
            # 为每个缺陷生成一个任务
            tasks = []
            skipped_count = 0
            not_exist_count = 0
            
            for defect in merged_defects:
                file_path = defect.get("file", "")
                if not file_path or file_path in ["system", "unknown"]:
                    skipped_count += 1
                    print(f"  ⚠️ [DEBUG] 跳过无效文件路径的缺陷: {file_path}")
                    continue
                
                # 规范化文件路径：如果已经是绝对路径，直接使用；否则拼接项目路径
                if os.path.isabs(file_path):
                    # 已经是绝对路径
                    abs_file_path = os.path.normpath(file_path)
                    
                    # 检查路径是否包含project_path（避免重复嵌套）
                    # 使用规范化后的路径进行比较
                    norm_project_path = os.path.normpath(project_path)
                    if norm_project_path in abs_file_path:
                        # 路径已经包含项目路径，直接使用
                        # 但需要检查是否有重复嵌套
                        # 例如：project_path/temp_extract/project_xxx/temp_extract/project_xxx/file.py
                        # 应该变成：project_path/temp_extract/project_xxx/file.py
                        path_parts = abs_file_path.split(os.sep)
                        project_parts = norm_project_path.split(os.sep)
                        
                        # 查找重复的路径段序列
                        if len(path_parts) > len(project_parts) + 2:
                            max_pattern_len = min((len(path_parts) - len(project_parts)) // 2, 10)
                            for pattern_len in range(max_pattern_len, 0, -1):
                                start_idx = len(project_parts)
                                if len(path_parts) >= start_idx + pattern_len * 2:
                                    pattern = path_parts[start_idx:start_idx + pattern_len]
                                    next_pattern = path_parts[start_idx + pattern_len:start_idx + pattern_len * 2]
                                    if pattern == next_pattern:
                                        # 找到重复模式，移除重复的部分
                                        print(f"  🔧 [DEBUG] 检测到路径重复嵌套，移除重复段: {os.sep.join(pattern)}")
                                        abs_file_path = os.sep.join(project_parts + path_parts[start_idx + pattern_len:])
                                        abs_file_path = os.path.normpath(abs_file_path)
                                        break
                    else:
                        # 路径不包含项目路径，但已经是绝对路径，直接使用
                        # 这种情况可能发生在Docker环境下，路径映射不同
                        print(f"  ⚠️ [DEBUG] 绝对路径不包含项目路径，直接使用: {abs_file_path}")
                else:
                    # 相对路径，拼接项目路径
                    # 先规范化相对路径，移除开头的./或../
                    file_path = file_path.lstrip('./').lstrip('../')
                    abs_file_path = os.path.normpath(os.path.join(project_path, file_path))
                
                # 最终规范化路径
                abs_file_path = os.path.normpath(abs_file_path)
                
                # 检查文件是否存在
                if not os.path.exists(abs_file_path):
                    not_exist_count += 1
                    print(f"  ⚠️ [DEBUG] 文件不存在: {abs_file_path}")
                    print(f"     project_path: {project_path}")
                    print(f"     file_path: {file_path}")
                    # 注意：即使文件不存在，也创建任务（文件可能在后续步骤中创建）
                
                # 获取缺陷描述作为任务描述
                task_description = defect.get("description", "")
                if not task_description:
                    # 如果没有描述，生成一个简单的描述
                    severity = defect.get("severity", "unknown")
                    tool = defect.get("tool", "unknown")
                    line = defect.get("line", 0)
                    file_name = os.path.basename(file_path)
                    task_description = f"修复 {file_name} 第 {line} 行的 {tool} {severity} 级别问题"
                
                # 统一使用正斜杠（跨平台兼容）
                problem_file = abs_file_path.replace("\\", "/")
                
                task = {
                    "task": task_description,  # 使用缺陷的简单描述
                    "problem_file": problem_file,  # 保存绝对路径
                    "project_root": project_path.replace("\\", "/"),
                    "agent_test_path": os.path.join(project_path, "agent-test").replace("\\", "/"),
                    "backup_agent_path": os.path.join(project_path, "backup-agent").replace("\\", "/"),
                    # 可选：添加缺陷的详细信息，方便后续处理
                    "defect_info": {
                        "line": defect.get("line", 0),
                        "severity": defect.get("severity", "unknown"),
                        "tool": defect.get("tool", "unknown"),
                        "source": defect.get("source", "unknown")
                    }
                }
                tasks.append(task)
            
            print(f"📝 [DEBUG] 生成任务统计:")
            print(f"   总缺陷数: {len(merged_defects)}")
            print(f"   生成任务数: {len(tasks)}")
            print(f"   跳过缺陷数: {skipped_count}")
            print(f"   文件不存在数: {not_exist_count}")
            
            if not tasks:
                print("⚠️ [DEBUG] 警告: tasks 为空，无法生成任务信息JSON文件")
                return None
            
            # 保存任务信息JSON文件
            task_info_dir = Path(project_path)
            task_info_dir.mkdir(parents=True, exist_ok=True)
            task_info_file = task_info_dir / "agent_task_info.json"
            
            print(f"📝 [DEBUG] 保存任务信息到: {task_info_file}")
            with open(task_info_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)
            
            print(f"✅ [DEBUG] 任务信息JSON文件已生成: {task_info_file}")
            print(f"✅ [DEBUG] 每个缺陷都生成了一个独立任务")
            return str(task_info_file)
        
        except Exception as e:
            print(f"❌ [DEBUG] 生成任务信息JSON文件失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """生成文本报告"""
        report_lines = [
            "# 综合检测报告",
            f"生成时间: {results.get('timestamp', 'unknown')}",
            f"检测类型: {results.get('detection_type', 'unknown')}",
            "",
            "## 检测摘要",
        ]
        
        summary = results.get("summary", {})
        report_lines.extend([
            f"- 总文件数: {summary.get('total_files', 0)}",
            f"- 分析完成: {summary.get('analysis_completed', False)}",
            ""
        ])
        
        # 添加问题摘要
        issues_summary = summary.get("issues_summary", {})
        if issues_summary:
            report_lines.append("## 问题统计")
            for analysis_type, stats in issues_summary.items():
                report_lines.append(f"### {analysis_type.upper()}")
                for key, value in stats.items():
                    report_lines.append(f"- {key}: {value}")
                report_lines.append("")
        
        return "\n".join(report_lines)
    
    def save_results(self, results: Dict[str, Any], file_path: str):
        """保存结果到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"检测结果已保存到: {file_path}")
        except Exception as e:
            print(f"保存结果失败: {e}")
    
    def generate_severe_issues_report(self, results: Dict[str, Any], filename: str) -> str:
        """生成严重问题汇总文档"""
        report_lines = [
            "# 严重问题汇总报告",
            f"**项目名称**: {filename}",
            f"**生成时间**: {results.get('timestamp', 'unknown')}",
            f"**检测类型**: {results.get('detection_type', 'unknown')}",
            "",
            "## 概述",
            "本报告汇总了代码检测中发现的严重问题，排除了格式化和风格问题，重点关注可能影响功能和安全的关键问题。",
            ""
        ]
        
        # 收集所有严重问题
        severe_issues = []
        
        # 静态分析问题
        if "static_analysis" in results:
            static_issues = results["static_analysis"].get("issues", [])
            for issue in static_issues:
                if self._is_severe_issue(issue):
                    severe_issues.append({
                        "type": "静态分析",
                        "severity": issue.get("severity", "unknown"),
                        "file": issue.get("file", "unknown"),
                        "line": issue.get("line", "unknown"),
                        "message": issue.get("message", "unknown"),
                        "tool": issue.get("tool", "unknown"),
                        "issue_type": issue.get("type", "unknown")
                    })
        
        # 动态监控问题
        if "dynamic_monitoring" in results:
            dynamic_alerts = results["dynamic_monitoring"].get("alerts", [])
            for alert in dynamic_alerts:
                if self._is_severe_alert(alert):
                    severe_issues.append({
                        "type": "动态监控",
                        "severity": alert.get("severity", "unknown"),
                        "file": "系统监控",
                        "line": "N/A",
                        "message": alert.get("message", "unknown"),
                        "tool": "系统监控",
                        "issue_type": alert.get("type", "unknown")
                    })
        
        # 运行时分析问题
        if "runtime_analysis" in results:
            runtime = results["runtime_analysis"]
            if runtime.get("error"):
                severe_issues.append({
                    "type": "运行时分析",
                    "severity": "error",
                    "file": runtime.get("main_file", "unknown"),
                    "line": "N/A",
                    "message": runtime.get("error"),
                    "tool": "运行时分析",
                    "issue_type": "execution_error"
                })
        
        # 动态检测问题
        if "dynamic_detection" in results:
            dynamic_issues = results["dynamic_detection"].get("issues", [])
            for issue in dynamic_issues:
                if self._is_severe_dynamic_issue(issue):
                    severe_issues.append({
                        "type": "动态检测",
                        "severity": issue.get("severity", "unknown"),
                        "file": issue.get("file", "unknown"),
                        "line": issue.get("line", "N/A"),
                        "message": issue.get("message", "unknown"),
                        "tool": issue.get("test", "unknown"),
                        "issue_type": issue.get("type", "unknown")
                    })
        
        # 按严重程度和文件分组
        if severe_issues:
            # 按严重程度排序
            severity_order = {"error": 0, "critical": 0, "warning": 1, "info": 2}
            severe_issues.sort(key=lambda x: severity_order.get(x["severity"], 3))
            
            # 按文件分组
            issues_by_file = {}
            for issue in severe_issues:
                file_path = issue["file"]
                if file_path not in issues_by_file:
                    issues_by_file[file_path] = []
                issues_by_file[file_path].append(issue)
            
            # 生成报告内容
            report_lines.extend([
                f"**发现严重问题总数**: {len(severe_issues)}",
                "",
                "## 问题详情",
                ""
            ])
            
            # 按文件输出问题
            for file_path, file_issues in issues_by_file.items():
                report_lines.extend([
                    f"### 📁 {file_path}",
                    ""
                ])
                
                for issue in file_issues:
                    severity_emoji = {
                        "error": "❌",
                        "critical": "🚨",
                        "warning": "⚠️",
                        "info": "ℹ️"
                    }.get(issue["severity"], "❓")
                    
                    report_lines.extend([
                        f"**{severity_emoji} {issue['severity'].upper()}** - 第 {issue['line']} 行",
                        f"- **问题类型**: {issue['issue_type']}",
                        f"- **检测工具**: {issue['tool']}",
                        f"- **问题描述**: {issue['message']}",
                        ""
                    ])
            
            # 添加修复建议
            report_lines.extend([
                "## 修复建议",
                "",
                "### 优先级排序",
                "1. **立即修复**: 错误和严重问题",
                "2. **尽快修复**: 警告问题",
                "3. **计划修复**: 信息类问题",
                "",
                "### 修复步骤",
                "1. 按文件逐个处理问题",
                "2. 优先处理影响功能的关键问题",
                "3. 修复后重新运行检测验证",
                "4. 建立代码质量检查流程",
                ""
            ])
            
        else:
            report_lines.extend([
                "## 检测结果",
                "",
                "✅ **未发现严重问题**",
                "",
                "项目代码质量良好，未发现需要立即处理的严重问题。",
                "建议继续保持代码质量，定期进行代码审查。",
                ""
            ])
        
        # 添加统计信息
        summary = results.get("summary", {})
        report_lines.extend([
            "## 检测统计",
            "",
            f"- **总文件数**: {summary.get('total_files', 0)}",
            f"- **总问题数**: {summary.get('total_issues', 0)}",
            f"- **严重问题**: {summary.get('critical_issues', 0)}",
            f"- **警告问题**: {summary.get('warning_issues', 0)}",
            f"- **信息问题**: {summary.get('info_issues', 0)}",
            f"- **整体状态**: {summary.get('overall_status', 'unknown')}",
            "",
            "---",
            f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])
        
        return "\n".join(report_lines)
    
    def _is_severe_issue(self, issue: Dict[str, Any]) -> bool:
        """判断静态分析问题是否为严重问题"""
        # 排除格式化和风格问题
        excluded_types = {
            "import_style", "line_length", "trailing_whitespace", 
            "missing_whitespace", "extra_whitespace", "indentation",
            "blank_line", "spacing", "quotes", "docstring"
        }
        
        issue_type = issue.get("type", "").lower()
        severity = issue.get("severity", "").lower()
        
        # 如果是格式或风格问题，直接排除
        if issue_type in excluded_types:
            return False
        
        # 只保留错误和严重问题
        if severity in ["error", "critical"]:
            return True
        
        # 对于警告，只保留重要的类型
        if severity == "warning":
            important_warning_types = {
                "security", "performance", "logic_error", "unused_variable",
                "undefined_variable", "import_error", "syntax_error"
            }
            return issue_type in important_warning_types
        
        return False
    
    def _is_severe_alert(self, alert: Dict[str, Any]) -> bool:
        """判断动态监控告警是否为严重问题"""
        severity = alert.get("severity", "").lower()
        return severity in ["error", "critical", "warning"]
    
    def _is_severe_dynamic_issue(self, issue: Dict[str, Any]) -> bool:
        """判断动态检测问题是否为严重问题"""
        severity = issue.get("severity", "").lower()
        issue_type = issue.get("type", "").lower()
        
        # 只保留错误和严重问题
        if severity in ["error", "critical"]:
            return True
        
        # 对于警告，只保留重要的类型
        if severity == "warning":
            important_types = {
                "security", "performance", "functionality", "compatibility"
            }
            return issue_type in important_types
        
        return False

async def generate_ai_comprehensive_report(results: Dict[str, Any], filename: str) -> str:
    """生成AI综合检测报告"""
    try:
        if not deepseek_config.is_configured():
            print("⚠️ DeepSeek API未配置，使用基础报告")
            return generate_fallback_report(results, filename)
        
        prompt = build_comprehensive_analysis_prompt(results, filename)
        
        print("🤖 正在生成AI综合报告...")
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{deepseek_config.base_url}/chat/completions",
                headers=deepseek_config.get_headers(),
                json={
                    "model": deepseek_config.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": deepseek_config.max_tokens,
                    "temperature": deepseek_config.temperature
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_content = result["choices"][0]["message"]["content"]
                print("✅ AI综合报告生成成功")
                return ai_content
            else:
                print(f"❌ AI API调用失败: {response.status_code}")
                return generate_fallback_report(results, filename)
                
    except httpx.TimeoutException:
        print("❌ AI API调用超时")
        return generate_fallback_report(results, filename)
    except httpx.RequestError as e:
        print(f"❌ AI API请求失败: {e}")
        return generate_fallback_report(results, filename)
    except Exception as e:
        print(f"❌ AI报告生成异常: {e}")
        return generate_fallback_report(results, filename)

def build_comprehensive_analysis_prompt(results: Dict[str, Any], filename: str) -> str:
    """构建综合分析提示词"""
    summary = results.get("summary", {})
    
    prompt = f"""请分析以下综合检测结果，生成一份详细的自然语言报告：

## 项目信息
- 文件名: {filename}
- 检测时间: {results.get('timestamp', 'unknown')}
- 检测类型: {results.get('detection_type', 'unknown')}
- 总文件数: {summary.get('total_files', 0)}

## 检测统计
- 总问题数: {summary.get('total_issues', 0)}
- 严重问题: {summary.get('critical_issues', 0)}
- 警告问题: {summary.get('warning_issues', 0)}
- 信息问题: {summary.get('info_issues', 0)}
- 整体状态: {summary.get('overall_status', 'unknown')}

## 静态分析结果
"""
    
    if "static_analysis" in results:
        static = results["static_analysis"]
        statistics = static.get("statistics", {})
        
        prompt += f"- 分析类型: {static.get('analysis_type', 'unknown')}\n"
        prompt += f"- 分析文件数: {static.get('files_analyzed', 0)}\n"
        prompt += f"- 总文件数: {statistics.get('total_files', 0)}\n"
        prompt += f"- 总代码行数: {statistics.get('total_lines', 0)}\n"
        prompt += f"- 平均复杂度: {statistics.get('average_complexity', 0)}\n"
        prompt += f"- 可维护性评分: {statistics.get('maintainability_score', 0)}\n"
        prompt += f"- 发现问题数: {len(static.get('issues', []))}\n"
        
        # 添加问题统计
        issues_by_severity = statistics.get("issues_by_severity", {})
        issues_by_tool = statistics.get("issues_by_tool", {})
        
        if issues_by_severity:
            prompt += "\n### 问题严重程度分布:\n"
            for severity, count in issues_by_severity.items():
                prompt += f"- {severity}: {count}个\n"
        
        if issues_by_tool:
            prompt += "\n### 分析工具统计:\n"
            for tool, count in issues_by_tool.items():
                prompt += f"- {tool}: {count}个问题\n"
    
    prompt += "\n## 动态监控结果\n"
    if "dynamic_monitoring" in results:
        dynamic = results["dynamic_monitoring"]
        prompt += f"- 监控时长: {dynamic.get('duration', 0)}秒\n"
        prompt += f"- 告警数量: {len(dynamic.get('alerts', []))}\n"
    
    prompt += "\n## 运行时分析结果（独立检测模块）\n"
    prompt += "注意：运行时分析仅用于检查项目主文件能否直接执行，与动态检测的测试成功率是独立的。\n"
    if "runtime_analysis" in results:
        runtime = results["runtime_analysis"]
        prompt += f"- 主文件: {runtime.get('main_file', 'N/A')}\n"
        prompt += f"- 执行状态: {'成功' if runtime.get('execution_successful', False) else '失败'}\n"
        if runtime.get("error"):
            prompt += f"- 错误信息: {runtime.get('error')}\n"
    
    prompt += "\n## 动态检测结果（Flask功能测试）\n"
    prompt += "注意：动态检测通过实际运行Flask应用并执行功能测试来检测缺陷，与运行时分析是独立的检测模块。\n"
    if "dynamic_detection" in results:
        dynamic_detection = results["dynamic_detection"]
        prompt += f"- 状态: {dynamic_detection.get('status', 'unknown')}\n"
        prompt += f"- 是Flask项目: {dynamic_detection.get('is_flask_project', False)}\n"
        prompt += f"- 测试完成: {dynamic_detection.get('tests_completed', False)}\n"
        prompt += f"- 测试成功率: {dynamic_detection.get('success_rate', 0)}%\n"
        prompt += f"- 发现问题数: {len(dynamic_detection.get('issues', []))}\n"
        prompt += "重要说明：\n"
        prompt += "- 如果测试完成且成功率为100%，说明动态检测测试执行成功\n"
        prompt += "- 运行时分析失败不影响动态检测的成功（两者检测方式不同）\n"
        prompt += "- 动态检测的成功率反映的是功能测试的通过率，而不是检测本身的失败\n"
    
    prompt += """
请生成一份详细的自然语言分析报告，包括：
1. 项目概述
2. 问题分析（请明确区分运行时分析失败和动态检测失败，它们是不同的检测模块）
3. 风险评估
4. 改进建议
5. 总结

报告应该专业、详细且易于理解。
特别注意：
- 如果动态检测显示"测试完成: True, 成功率: 100%"，说明动态检测本身是成功的
- 运行时分析失败只表示主文件无法直接执行，不代表动态检测失败
- 请在报告中明确说明这两个检测模块的区别和各自的检测结果"""
    
    return prompt

def generate_fallback_report(results: Dict[str, Any], filename: str) -> str:
    """生成基础报告（当AI API不可用时）"""
    summary = results.get("summary", {})
    
    report = f"""# 综合检测报告

## 项目概述
- **项目名称**: {filename}
- **检测时间**: {results.get('timestamp', 'unknown')}
- **检测类型**: {results.get('detection_type', 'unknown')}
- **总文件数**: {summary.get('total_files', 0)}

## 检测结果摘要
- **总问题数**: {summary.get('total_issues', 0)}
- **严重问题**: {summary.get('critical_issues', 0)}
- **警告问题**: {summary.get('warning_issues', 0)}
- **信息问题**: {summary.get('info_issues', 0)}
- **整体状态**: {summary.get('overall_status', 'unknown')}

## 问题分析
"""
    
    if summary.get('critical_issues', 0) > 0:
        report += "⚠️ **发现严重问题**，需要立即处理\n"
    if summary.get('warning_issues', 0) > 0:
        report += "⚠️ **发现警告问题**，建议及时处理\n"
    if summary.get('info_issues', 0) > 0:
        report += "ℹ️ **发现信息问题**，可选择性处理\n"
    
    if summary.get('total_issues', 0) == 0:
        report += "✅ **未发现明显问题**\n"
    
    # 添加建议
    recommendations = summary.get('recommendations', [])
    if recommendations:
        report += "\n## 改进建议\n"
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
    
    report += "\n## 总结\n"
    if summary.get('overall_status') == 'good':
        report += "项目整体质量良好，未发现严重问题。建议继续保持代码质量，定期进行代码审查。"
    elif summary.get('overall_status') == 'warning':
        report += "项目存在一些警告问题，建议及时处理。重点关注代码质量和可维护性。"
    elif summary.get('overall_status') == 'error':
        report += "项目存在严重问题，需要立即修复。建议优先处理严重问题，然后逐步改进代码质量。"
    else:
        report += "请根据具体问题情况进行相应处理。建议定期进行代码质量检查。"
    
    return report

# API端点
@router.get("/")
async def root():
    """根路径"""
    return {
        "message": "综合检测API运行中",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "comprehensive_detection"
    }

@router.post("/detect", response_model=BaseResponse)
async def comprehensive_detect(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(None),
    files: List[UploadFile] = File(None),
    static_analysis: str = Form("true"),
    dynamic_monitoring: str = Form("true"),
    runtime_analysis: str = Form("true"),
    enable_web_app_test: str = Form("false"),
    enable_dynamic_detection: str = Form("true"),
    enable_flask_specific_tests: str = Form("true"),
    enable_server_testing: str = Form("true"),
    upload_type: str = Form("file"),
    # 静态检测工具选择参数
    enable_pylint: str = Form("true"),
    enable_mypy: str = Form("true"),
    enable_semgrep: str = Form("true"),
    enable_ruff: str = Form("true"),
    enable_bandit: str = Form("true"),
    enable_llm_filter: str = Form("true")
):
    """综合检测 - 并行执行静态检测和动态检测"""
    
    # 确保所有布尔参数都是布尔值
    def convert_to_bool(value, param_name):
        if isinstance(value, str):
            result = value.lower() in ('true', '1', 'yes', 'on')
            return result
        elif isinstance(value, bool):
            return value
        else:
            return bool(value)
    
    static_analysis = convert_to_bool(static_analysis, 'static_analysis')
    dynamic_monitoring = convert_to_bool(dynamic_monitoring, 'dynamic_monitoring')
    runtime_analysis = convert_to_bool(runtime_analysis, 'runtime_analysis')
    enable_web_app_test = convert_to_bool(enable_web_app_test, 'enable_web_app_test')
    enable_dynamic_detection = convert_to_bool(enable_dynamic_detection, 'enable_dynamic_detection')
    enable_flask_specific_tests = convert_to_bool(enable_flask_specific_tests, 'enable_flask_specific_tests')
    enable_server_testing = convert_to_bool(enable_server_testing, 'enable_server_testing')
    # 静态检测工具选择
    enable_pylint = convert_to_bool(enable_pylint, 'enable_pylint')
    enable_mypy = convert_to_bool(enable_mypy, 'enable_mypy')
    enable_semgrep = convert_to_bool(enable_semgrep, 'enable_semgrep')
    enable_ruff = convert_to_bool(enable_ruff, 'enable_ruff')
    enable_bandit = convert_to_bool(enable_bandit, 'enable_bandit')
    enable_llm_filter = convert_to_bool(enable_llm_filter, 'enable_llm_filter')
    
    # 验证输入
    if not file and not files:
        raise HTTPException(status_code=400, detail="请提供文件或文件列表")
    
    if file and files:
        raise HTTPException(status_code=400, detail="请选择单文件上传或目录上传，不能同时使用")
    
    # 处理单文件上传（压缩包）
    if file:
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="只支持ZIP格式的压缩包")
        upload_files = [file]
        filename = file.filename
    else:
        # 处理多文件上传（目录）
        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="目录上传需要至少一个文件")
        upload_files = files
        filename = f"directory_{len(files)}_files"
    
    temp_file_path = None
    temp_dir = None
    
    try:
        print(f"开始处理上传文件: {filename}")
        
        if upload_type == "file":
            # 单文件上传（压缩包）
            file = upload_files[0]
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                temp_file_path = tmp_file.name
            print(f"压缩包已保存到临时位置: {temp_file_path}")
        else:
            # 目录上传（多文件）
            temp_dir = tempfile.mkdtemp(prefix="comprehensive_detection_")
            print(f"创建临时目录: {temp_dir}")
            
            # 保存所有文件到临时目录
            for file in upload_files:
                if file.filename:
                    # 处理文件路径结构
                    if '/' in file.filename or '\\' in file.filename:
                        file_path = os.path.join(temp_dir, file.filename)
                    else:
                        file_path = os.path.join(temp_dir, file.filename)
                    
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    with open(file_path, "wb") as f:
                        content = await file.read()
                        f.write(content)
                    print(f"保存文件: {file.filename} -> {file_path}")
            
            # 创建ZIP文件
            temp_file_path = os.path.join(temp_dir, "project.zip")
            with zipfile.ZipFile(temp_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file != "project.zip":  # 避免包含自己
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zipf.write(file_path, arcname)
            
            print(f"目录已打包为ZIP: {temp_file_path}")
        
        # 为每个请求创建独立的检测器实例
        detector = ComprehensiveDetector(static_agent, dynamic_agent)
        detector.enable_web_app_test = enable_web_app_test
        detector.enable_dynamic_detection = enable_dynamic_detection
        detector.enable_flask_specific_tests = enable_flask_specific_tests
        detector.enable_server_testing = enable_server_testing
        
        # 执行检测（添加超时处理）
        print("=" * 60)
        print("🚀 [API] 开始执行综合检测...")
        print(f"📁 [API] 文件路径: {temp_file_path}")
        print(f"⚙️  [API] 检测选项:")
        print(f"   - static_analysis: {static_analysis}")
        print(f"   - dynamic_monitoring: {dynamic_monitoring}")
        print(f"   - runtime_analysis: {runtime_analysis}")
        print(f"   - enable_dynamic_detection: {enable_dynamic_detection}")
        print(f"   - enable_flask_specific_tests: {enable_flask_specific_tests}")
        print(f"   - enable_server_testing: {enable_server_testing}")
        print(f"   - enable_pylint: {enable_pylint}")
        print(f"   - enable_mypy: {enable_mypy}")
        print(f"   - enable_semgrep: {enable_semgrep}")
        print(f"   - enable_ruff: {enable_ruff}")
        print(f"   - enable_bandit: {enable_bandit}")
        print(f"   - enable_llm_filter: {enable_llm_filter}")
        print("=" * 60)
        
        if enable_web_app_test or enable_server_testing:
            print("⚠️ 已启用Web应用测试，检测时间可能较长...")
        
        try:
            results = await asyncio.wait_for(
                detector.detect_defects(
                    zip_file_path=temp_file_path,
                    static_analysis=static_analysis,
                    dynamic_monitoring=dynamic_monitoring,
                    runtime_analysis=runtime_analysis,
                    enable_web_app_test=enable_web_app_test,
                    enable_dynamic_detection=enable_dynamic_detection,
                    enable_flask_specific_tests=enable_flask_specific_tests,
                    enable_server_testing=enable_server_testing,
                    # 静态检测工具选择
                    enable_pylint=enable_pylint,
                    enable_mypy=enable_mypy,
                    enable_semgrep=enable_semgrep,
                    enable_ruff=enable_ruff,
                    enable_bandit=enable_bandit,
                    enable_llm_filter=enable_llm_filter
                ),
                timeout=1800  # 30分钟超时（1800秒）
            )
        except asyncio.TimeoutError:
            return BaseResponse(
                success=False,
                error="检测超时（30分钟）",
                message="检测过程超时，请尝试上传较小的项目"
            )
        except Exception as e:
            print(f"❌ [API] 检测过程发生异常: {e}")
            import traceback
            traceback.print_exc()
            return BaseResponse(
                success=False,
                error=f"检测过程发生异常: {str(e)}",
                message="检测失败，请查看错误信息"
            )
        
            print("=" * 60)
            print("✅ [API] 检测完成")
            print(f"📊 [API] 检测结果摘要:")
            if results.get("summary"):
                summary = results["summary"]
                print(f"   - 总文件数: {summary.get('total_files', 0)}")
                print(f"   - 总问题数: {summary.get('total_issues', 0)}")
                print(f"   - 严重问题: {summary.get('critical_issues', 0)}")
                print(f"   - 警告问题: {summary.get('warning_issues', 0)}")
            if results.get("merged_defects"):
                print(f"   - 合并缺陷数: {len(results['merged_defects'])}")
            if results.get("task_info_file"):
                print(f"   - 任务信息文件: {results['task_info_file']}")
            if results.get("task_info"):
                print(f"   - 任务数量: {len(results['task_info'])}")
            print("=" * 60)
        
        print("\n📝 [API] 检测完成，生成报告...")
        
        # 生成文本报告
        report = detector.generate_report(results)
        print("✅ [API] 文本报告已生成")
        
        # 生成AI报告
        try:
            filename = file.filename if file else (files[0].filename if files else "unknown")
            ai_report = await generate_ai_comprehensive_report(results, filename)
            print("✅ [API] AI报告生成成功")
        except Exception as e:
            print(f"⚠️ [API] AI报告生成失败: {e}")
            ai_report = {
                "success": False,
                "error": str(e),
                "summary": "AI报告生成失败，请查看详细检测结果"
            }
        
        # 保存结果到文件（使用绝对路径）
        try:
            results_file = f"comprehensive_detection_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            # 获取项目根目录（API文件所在目录的父目录）
            api_dir = Path(__file__).parent
            project_root = api_dir.parent
            results_dir = project_root / "comprehensive_detection_results"
            results_dir.mkdir(exist_ok=True)
            results_path = results_dir / results_file
            results_path_abs = results_path.resolve()
            detector.save_results(results, str(results_path_abs))
            print(f"✅ [API] 结果已保存到:")
            print(f"   相对路径: {results_path}")
            print(f"   绝对路径: {results_path_abs}")
            print(f"📊 [API] 文件大小: {results_path_abs.stat().st_size / 1024:.2f} KB")
        except Exception as e:
            print(f"⚠️ [API] 保存结果文件失败: {e}")
            import traceback
            traceback.print_exc()
            results_file = None
        
        # 检查任务信息文件
        if results.get("task_info_file"):
            task_info_path = Path(results["task_info_file"])
            task_info_path_abs = task_info_path.resolve()
            if task_info_path_abs.exists():
                print(f"✅ [API] 任务信息文件已保存:")
                print(f"   相对路径: {task_info_path}")
                print(f"   绝对路径: {task_info_path_abs}")
                print(f"📊 [API] 任务数量: {len(results.get('task_info', []))}")
                print(f"📊 [API] 文件大小: {task_info_path_abs.stat().st_size / 1024:.2f} KB")
            else:
                print(f"⚠️ [API] 警告: 任务信息文件路径存在但文件不存在:")
                print(f"   相对路径: {task_info_path}")
                print(f"   绝对路径: {task_info_path_abs}")
                print(f"   当前工作目录: {os.getcwd()}")
        else:
            print("⚠️ [API] 警告: 未生成任务信息文件")
        
        # 返回结果
        return BaseResponse(
            success=True,
            message="综合检测完成",
            data={
                "results": results,
                "report": report,
                "ai_report": ai_report,
                "results_file": results_file,
                "filename": file.filename,
                "detection_time": datetime.now().isoformat()
            }
        )
    
    finally:
        # 注意：临时文件保留，不删除上传的文件，以便修复Agent使用
        # 只删除上传的ZIP压缩包（如果存在）
        if temp_file_path and os.path.exists(temp_file_path):
            # 检查是否是ZIP文件（上传的压缩包可以删除）
            # 解压后的目录保留在extract_dir中，不在这里删除
            try:
                # 只删除ZIP文件，不删除解压后的目录
                if temp_file_path.endswith('.zip'):
                    os.unlink(temp_file_path)
                    print(f"✅ [API] 已清理上传的ZIP文件: {temp_file_path}")
                else:
                    print(f"📝 [API] 保留文件: {temp_file_path}")
            except Exception as e:
                print(f"⚠️ [API] 清理ZIP文件失败: {e}")
        
        # 不清理临时目录，保留解压后的项目文件
        # extract_dir中的文件需要保留供修复Agent使用
        if temp_dir and os.path.exists(temp_dir):
            print(f"📝 [API] 保留临时目录（解压后的项目文件）: {temp_dir}")
            print(f"⚠️ [API] 注意: 临时目录未删除，需要定期清理以释放磁盘空间")

@router.get("/status")
async def get_detection_status():
    """获取检测状态"""
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
        "supported_formats": [".zip"],
        "features": {
            "static_analysis": True,
            "dynamic_monitoring": True,
            "runtime_analysis": True,
            "comprehensive_detection": True
        }
    }

@router.post("/generate-severe-issues-report")
async def generate_severe_issues_report(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(None),
    files: List[UploadFile] = File(None),
    static_analysis: str = Form("true"),
    dynamic_monitoring: str = Form("true"),
    runtime_analysis: str = Form("true"),
    enable_web_app_test: str = Form("false"),
    enable_dynamic_detection: str = Form("true"),
    enable_flask_specific_tests: str = Form("true"),
    enable_server_testing: str = Form("true"),
    upload_type: str = Form("file")
):
    """生成严重问题汇总文档"""
    
    # 确保所有布尔参数都是布尔值
    def convert_to_bool(value, param_name):
        if isinstance(value, str):
            result = value.lower() in ('true', '1', 'yes', 'on')
            return result
        elif isinstance(value, bool):
            return value
        else:
            return bool(value)
    
    static_analysis = convert_to_bool(static_analysis, 'static_analysis')
    dynamic_monitoring = convert_to_bool(dynamic_monitoring, 'dynamic_monitoring')
    runtime_analysis = convert_to_bool(runtime_analysis, 'runtime_analysis')
    enable_web_app_test = convert_to_bool(enable_web_app_test, 'enable_web_app_test')
    enable_dynamic_detection = convert_to_bool(enable_dynamic_detection, 'enable_dynamic_detection')
    enable_flask_specific_tests = convert_to_bool(enable_flask_specific_tests, 'enable_flask_specific_tests')
    enable_server_testing = convert_to_bool(enable_server_testing, 'enable_server_testing')
    
    # 验证输入
    if not file and not files:
        raise HTTPException(status_code=400, detail="请提供文件或文件列表")
    
    if file and files:
        raise HTTPException(status_code=400, detail="请选择单文件上传或目录上传，不能同时使用")
    
    # 处理单文件上传（压缩包）
    if file:
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="只支持ZIP格式的压缩包")
        upload_files = [file]
        filename = file.filename
    else:
        # 处理多文件上传（目录）
        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="目录上传需要至少一个文件")
        upload_files = files
        filename = f"directory_{len(files)}_files"
    
    temp_file_path = None
    temp_dir = None
    
    try:
        print(f"开始处理上传文件: {filename}")
        
        if upload_type == "file":
            # 单文件上传（压缩包）
            file = upload_files[0]
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                temp_file_path = tmp_file.name
            print(f"压缩包已保存到临时位置: {temp_file_path}")
        else:
            # 目录上传（多文件）
            temp_dir = tempfile.mkdtemp(prefix="comprehensive_detection_")
            print(f"创建临时目录: {temp_dir}")
            
            # 保存所有文件到临时目录
            for file in upload_files:
                if file.filename:
                    # 处理文件路径结构
                    if '/' in file.filename or '\\' in file.filename:
                        file_path = os.path.join(temp_dir, file.filename)
                    else:
                        file_path = os.path.join(temp_dir, file.filename)
                    
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    with open(file_path, "wb") as f:
                        content = await file.read()
                        f.write(content)
                    print(f"保存文件: {file.filename} -> {file_path}")
            
            # 创建ZIP文件
            temp_file_path = os.path.join(temp_dir, "project.zip")
            with zipfile.ZipFile(temp_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file != "project.zip":  # 避免包含自己
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zipf.write(file_path, arcname)
            
            print(f"目录已打包为ZIP: {temp_file_path}")
        
        # 为每个请求创建独立的检测器实例
        detector = ComprehensiveDetector(static_agent, dynamic_agent)
        detector.enable_web_app_test = enable_web_app_test
        detector.enable_dynamic_detection = enable_dynamic_detection
        detector.enable_flask_specific_tests = enable_flask_specific_tests
        detector.enable_server_testing = enable_server_testing
        
        # 执行检测
        print("开始执行综合检测...")
        try:
            results = await asyncio.wait_for(
                detector.detect_defects(
                    zip_file_path=temp_file_path,
                    static_analysis=static_analysis,
                    dynamic_monitoring=dynamic_monitoring,
                    runtime_analysis=runtime_analysis,
                    enable_dynamic_detection=enable_dynamic_detection,
                    enable_flask_specific_tests=enable_flask_specific_tests,
                    enable_server_testing=enable_server_testing,
                    enable_web_app_test=enable_web_app_test
                ),
                timeout=1800  # 30分钟超时（1800秒）
            )
        except asyncio.TimeoutError:
            return BaseResponse(
                success=False,
                error="检测超时（30分钟）",
                message="检测过程超时，请尝试上传较小的项目"
            )
        
        print("检测完成，生成严重问题汇总文档...")
        
        # 生成严重问题汇总文档
        severe_issues_report = detector.generate_severe_issues_report(results, filename)
        
        # 保存文档到result文件夹
        try:
            report_filename = f"severe_issues_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            result_dir = Path("result")
            result_dir.mkdir(exist_ok=True)
            report_path = result_dir / report_filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(severe_issues_report)
            
            print(f"✅ 严重问题汇总文档已保存到: {report_path}")
        except Exception as e:
            print(f"⚠️ 保存文档文件失败: {e}")
            report_filename = None
        
        # 返回结果
        return BaseResponse(
            success=True,
            message="严重问题汇总文档生成完成",
            data={
                "severe_issues_report": severe_issues_report,
                "report_filename": report_filename,
                "report_path": str(report_path) if report_filename else None,
                "filename": filename,
                "generation_time": datetime.now().isoformat(),
                "summary": results.get("summary", {})
            }
        )
    
    finally:
        # 清理临时文件
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                print(f"已清理临时文件: {temp_file_path}")
            except Exception as e:
                print(f"清理临时文件失败: {e}")
        
        # 清理临时目录
        if temp_dir and os.path.exists(temp_dir):
            try:
                import shutil
                shutil.rmtree(temp_dir)
                print(f"已清理临时目录: {temp_dir}")
            except Exception as e:
                print(f"清理临时目录失败: {e}")
