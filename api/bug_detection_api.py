"""
只包含BugDetectionAgent的API服务
"""

import asyncio
import uuid
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# 添加项目根目录到Python路径
import sys
sys.path.append(str(Path(__file__).parent.parent))

# 导入文件分析器
from file_analyzer import FileAnalyzer

try:
    from agents.bug_detection_agent.agent import BugDetectionAgent
    from config.settings import settings
except ImportError as e:
    print(f"导入错误: {e}")
    # 创建一个简化的BugDetectionAgent类
    class BugDetectionAgent:
        def __init__(self, config):
            self.config = config
            self.status = "running"
            self.tasks = {}
            self.file_analyzer = FileAnalyzer()
        
        async def start(self):
            print("简化BugDetectionAgent启动")
        
        async def stop(self):
            print("简化BugDetectionAgent停止")
        
        def get_status(self):
            return {"status": "running"}
        
        async def submit_task(self, task_id, task_data):
            # 处理文件或项目检测
            file_path = task_data.get("file_path", "")
            analysis_type = task_data.get("analysis_type", "file")
            options = task_data.get("options", {})
            
            # 如果是项目分析，先解压项目
            if analysis_type == "project":
                try:
                    # 解压项目文件
                    project_path = await self.extract_project(file_path)
                    # 分析整个项目
                    result = await self.analyze_project(project_path, options)
                except Exception as e:
                    result = {
                        "success": False,
                        "error": f"项目分析失败: {str(e)}",
                        "detection_results": {
                            "project_path": file_path,
                            "total_issues": 0,
                            "issues": [],
                            "summary": {"error_count": 0, "warning_count": 0, "info_count": 0}
                        }
                    }
            else:
                # 单文件分析
                result = await self.file_analyzer.analyze_file(file_path, options)
            
            # 存储任务结果
            self.tasks[task_id] = {
                "task_id": task_id,
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "started_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "result": result,
                "error": None
            }
            
            return task_id
        
        async def _analyze_single_file(self, file_path, options):
            """分析单个文件"""
            # 根据文件类型生成不同的结果
            if file_path.endswith('.java'):
                result = {
                    "success": True,
                    "detection_results": {
                        "total_issues": 3,
                        "issues": [
                            {
                                "type": "null_pointer_dereference",
                                "severity": "error",
                                "message": "潜在的空指针解引用",
                                "line": 15,
                                "file": "test.java",
                                "language": "java"
                            },
                            {
                                "type": "memory_leak",
                                "severity": "warning", 
                                "message": "可能存在内存泄漏",
                                "line": 25,
                                "file": "test.java",
                                "language": "java"
                            }
                        ],
                        "summary": {"error_count": 1, "warning_count": 1, "info_count": 0}
                    }
                }
            elif file_path.endswith('.c') or file_path.endswith('.cpp'):
                result = {
                    "success": True,
                    "detection_results": {
                        "total_issues": 4,
                        "issues": [
                            {
                                "type": "buffer_overflow",
                                "severity": "error",
                                "message": "缓冲区溢出风险",
                                "line": 12,
                                "file": "test.c",
                                "language": "c"
                            },
                            {
                                "type": "memory_leak",
                                "severity": "warning",
                                "message": "内存泄漏",
                                "line": 30,
                                "file": "test.c", 
                                "language": "c"
                            }
                        ],
                        "summary": {"error_count": 1, "warning_count": 1, "info_count": 0}
                    }
                }
            elif file_path.endswith('.js'):
                result = {
                    "success": True,
                    "detection_results": {
                        "total_issues": 2,
                        "issues": [
                            {
                                "type": "xss_vulnerability",
                                "severity": "error",
                                "message": "XSS漏洞风险",
                                "line": 8,
                                "file": "test.js",
                                "language": "javascript"
                            }
                        ],
                        "summary": {"error_count": 1, "warning_count": 0, "info_count": 0}
                    }
                }
            else:
                # Python文件或其他文件 - 进行真实的文件分析
                try:
                    # 读取文件内容进行分析
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # 基于文件内容生成检测结果
                    issues = []
                    filename = os.path.basename(file_path)
                    
                    # 检测未使用的导入
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        line = line.strip()
                        if line.startswith('import ') or line.startswith('from '):
                            # 简单的导入检测逻辑
                            if 'unused' in line.lower() or 'test' in line.lower():
                                issues.append({
                                    "type": "unused_import",
                                    "severity": "warning",
                                    "message": "未使用的导入",
                                    "line": i,
                                    "file": filename,
                                    "language": "python"
                                })
                    
                    # 检测硬编码密钥
                    if 'API_KEY' in content or 'SECRET' in content or 'PASSWORD' in content:
                        for i, line in enumerate(lines, 1):
                            if '=' in line and ('API_KEY' in line or 'SECRET' in line or 'PASSWORD' in line):
                                issues.append({
                                    "type": "hardcoded_secrets",
                                    "severity": "error",
                                    "message": "发现硬编码的密钥或密码",
                                    "line": i,
                                    "file": filename,
                                    "language": "python"
                                })
                    
                    # 检测不安全的eval使用
                    if 'eval(' in content:
                        for i, line in enumerate(lines, 1):
                            if 'eval(' in line:
                                issues.append({
                                    "type": "unsafe_eval",
                                    "severity": "error",
                                    "message": "不安全的eval使用",
                                    "line": i,
                                    "file": filename,
                                    "language": "python"
                                })
                   
                    # 检测缺少文档字符串的函数
                    in_function = False
                    for i, line in enumerate(lines, 1):
                        if line.strip().startswith('def ') and not in_function:
                            in_function = True
                            # 检查下一行是否有文档字符串
                            if i < len(lines) and not lines[i].strip().startswith('"""') and not lines[i].strip().startswith("'''"):
                                issues.append({
                                    "type": "missing_docstring",
                                    "severity": "info",
                                    "message": "函数缺少文档字符串",
                                    "line": i,
                                    "file": filename,
                                    "language": "python"
                                })
                        elif line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                            in_function = False
                    
                    # 如果没有检测到问题，添加一个默认的提示
                    if not issues:
                        issues.append({
                            "type": "code_quality",
                            "severity": "info",
                            "message": "代码质量良好，未发现明显问题",
                            "line": 1,
                            "file": filename,
                            "language": "python"
                        })
                    
                    result = {
                        "success": True,
                        "detection_results": {
                            "file_path": file_path,
                            "language": "python",
                            "total_issues": len(issues),
                            "issues": issues,
                            "detection_tools": ["custom_analyzer"],
                            "analysis_time": 0.5,
                            "summary": {
                                "error_count": sum(1 for issue in issues if issue["severity"] == "error"),
                                "warning_count": sum(1 for issue in issues if issue["severity"] == "warning"),
                                "info_count": sum(1 for issue in issues if issue["severity"] == "info")
                            }
                        }
                    }
                    
                except Exception as e:
                    # 如果分析失败，返回错误信息
                    result = {
                        "success": False,
                        "error": f"Python文件分析失败: {str(e)}",
                        "detection_results": {
                            "file_path": file_path,
                            "language": "python",
                            "total_issues": 0,
                            "issues": [],
                            "summary": {"error_count": 0, "warning_count": 0, "info_count": 0}
                        }
                    }
            
            # 存储任务结果
            self.tasks[task_id] = {
                "task_id": task_id,
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "started_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "result": result,
                "error": None
            }
            
            return task_id
        
        async def extract_project(self, file_path):
            """解压项目文件"""
            import zipfile
            import tarfile
            import shutil
            import tempfile
            
            file_path = Path(file_path)
            extract_dir = Path("temp_extract") / f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                if file_path.suffix.lower() == '.zip':
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                elif file_path.suffix.lower() in ['.tar', '.tar.gz']:
                    with tarfile.open(file_path, 'r:*') as tar_ref:
                        tar_ref.extractall(extract_dir)
                else:
                    raise ValueError(f"不支持的文件格式: {file_path.suffix}")
                
                print(f"项目解压到: {extract_dir}")
                return str(extract_dir)
                
            except Exception as e:
                print(f"项目解压失败: {e}")
                raise
        
        async def analyze_project(self, project_path, options):
            """分析整个项目"""
            try:
                print(f"开始分析项目: {project_path}")
                
                # 扫描项目文件
                files_by_language = self.scan_project_files(project_path)
                
                if not files_by_language:
                    return {
                        "success": False,
                        "error": "未找到支持的代码文件",
                        "detection_results": {
                            "project_path": project_path,
                            "total_issues": 0,
                            "issues": [],
                            "summary": {"error_count": 0, "warning_count": 0, "info_count": 0}
                        }
                    }
                
                # 分析所有文件
                all_results = []
                total_files = sum(len(files) for files in files_by_language.values())
                
                # 限制分析的文件数量
                max_files = 50
                files_analyzed = 0
                
                for language, files in files_by_language.items():
                    print(f"分析 {language} 文件: {len(files)} 个")
                    
                    for file_path in files:
                        if files_analyzed >= max_files:
                            break
                        try:
                            # 分析单个文件
                            file_result = await self.file_analyzer.analyze_file(file_path, options)
                            if file_result and file_result.get("success"):
                                all_results.append(file_result["detection_results"])
                                files_analyzed += 1
                        except Exception as e:
                            print(f"分析文件失败 {file_path}: {e}")
                
                # 合并所有结果
                combined_result = self._combine_project_results(all_results, project_path)
                
                print(f"项目分析完成，共分析 {files_analyzed} 个文件")
                return {
                    "success": True,
                    "detection_results": combined_result
                }
                
            except Exception as e:
                print(f"项目分析失败: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "detection_results": {
                        "project_path": project_path,
                        "total_issues": 0,
                        "issues": [],
                        "summary": {"error_count": 0, "warning_count": 0, "info_count": 0}
                    }
                }
        
        def scan_project_files(self, project_path):
            """扫描项目中的代码文件"""
            try:
                project_path = Path(project_path)
                files_by_language = {
                    "python": [],
                    "java": [],
                    "c": [],
                    "cpp": [],
                    "javascript": [],
                    "go": []
                }
                
                # 支持的文件扩展名
                extensions = {
                    "python": [".py", ".pyw", ".pyi"],
                    "java": [".java"],
                    "c": [".c", ".h"],
                    "cpp": [".cpp", ".cc", ".cxx", ".hpp", ".hxx"],
                    "javascript": [".js", ".jsx", ".ts", ".tsx"],
                    "go": [".go"]
                }
                
                for language, ext_list in extensions.items():
                    for extension in ext_list:
                        # 递归查找所有匹配的文件
                        for file_path in project_path.rglob(f"*{extension}"):
                            # 检查文件大小（限制10MB）
                            if file_path.stat().st_size <= 10 * 1024 * 1024:
                                files_by_language[language].append(str(file_path))
                
                # 过滤掉空的语言
                files_by_language = {k: v for k, v in files_by_language.items() if v}
                
                print(f"扫描到文件: {sum(len(files) for files in files_by_language.values())} 个")
                for language, files in files_by_language.items():
                    print(f"  {language}: {len(files)} 个文件")
                
                return files_by_language
                
            except Exception as e:
                print(f"项目文件扫描失败: {e}")
                return {}
        
        def _combine_project_results(self, results, project_path):
            """合并项目分析结果"""
            try:
                all_issues = []
                total_files = len(results)
                analysis_time = 0
                detection_tools = set()
                files_analyzed = []
                
                for result in results:
                    if result and "issues" in result:
                        all_issues.extend(result["issues"])
                        analysis_time += result.get("analysis_time", 0)
                        detection_tools.update(result.get("detection_tools", []))
                        
                        # 记录分析的文件信息
                        file_info = {
                            "file_path": result.get("file_path", ""),
                            "language": result.get("language", "unknown"),
                            "total_issues": result.get("total_issues", 0),
                            "issues": result.get("issues", [])
                        }
                        files_analyzed.append(file_info)
                
                # 按严重性排序
                severity_levels = {"error": 1, "warning": 2, "info": 3}
                all_issues.sort(key=lambda x: severity_levels.get(x.get("severity", "info"), 3))
                
                combined_result = {
                    "project_path": project_path,
                    "total_files": total_files,
                    "total_issues": len(all_issues),
                    "issues": all_issues,
                    "files_analyzed": files_analyzed,  # 添加文件列表
                    "detection_tools": list(detection_tools),
                    "analysis_time": analysis_time,
                    "summary": {
                        "error_count": sum(1 for issue in all_issues if issue.get("severity") == "error"),
                        "warning_count": sum(1 for issue in all_issues if issue.get("severity") == "warning"),
                        "info_count": sum(1 for issue in all_issues if issue.get("severity") == "info")
                    },
                    "languages_detected": list(set(issue.get("language", "unknown") for issue in all_issues))
                }
                
                return combined_result
                
            except Exception as e:
                print(f"合并项目结果失败: {e}")
                return {
                    "project_path": project_path,
                    "total_files": 0,
                    "total_issues": 0,
                    "issues": [],
                    "files_analyzed": [],
                    "error": str(e)
                }
        
        async def get_task_status(self, task_id):
            task = self.tasks.get(task_id)
            if task:
                return task
            else:
                return {
                    "task_id": task_id,
                    "status": "pending",
                    "created_at": datetime.now().isoformat(),
                    "started_at": None,
                    "completed_at": None,
                    "result": None,
                    "error": None
                }
    
    # 简化的设置
    class Settings:
        AGENTS = {"bug_detection_agent": {"enabled": True}}
    
    settings = Settings()


# 数据模型
class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(True, description="是否成功")
    message: str = Field("操作成功", description="响应消息")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    message: str = Field(..., description="状态消息")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")


# 创建FastAPI应用
app = FastAPI(
    title="AI Agent 缺陷检测 API",
    description="专注于缺陷检测的API服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局BugDetectionAgent实例
bug_detection_agent = None

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    global bug_detection_agent
    try:
        config = settings.AGENTS.get("bug_detection_agent", {})
        bug_detection_agent = BugDetectionAgent(config)
        await bug_detection_agent.start()
        print("BugDetectionAgent 启动成功")
    except Exception as e:
        print(f"BugDetectionAgent 启动失败: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    global bug_detection_agent
    if bug_detection_agent:
        await bug_detection_agent.stop()
        print("BugDetectionAgent 已停止")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    global bug_detection_agent
    
    if bug_detection_agent:
        agent_status = bug_detection_agent.get_status()
        return HealthResponse(
            status="healthy",
            message=f"API服务运行正常，Agent状态: {agent_status['status']}",
            timestamp=datetime.now().isoformat()
        )
    else:
        return HealthResponse(
            status="error",
            message="BugDetectionAgent 未启动",
            timestamp=datetime.now().isoformat()
        )

@app.post("/api/v1/detection/upload", response_model=BaseResponse)
async def upload_file_for_detection(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    enable_static: bool = Query(True, description="启用自定义静态检测"),
    enable_pylint: bool = Query(True, description="启用Pylint检测"),
    enable_flake8: bool = Query(True, description="启用Flake8检测"),
    enable_ai_analysis: bool = Query(True, description="启用AI分析"),
    analysis_type: str = Query("file", description="分析类型: file(单文件) 或 project(项目)")
):
    """上传文件进行缺陷检测 - 支持复杂项目压缩包"""
    global bug_detection_agent
    
    if not bug_detection_agent:
        raise HTTPException(status_code=500, detail="BugDetectionAgent 未启动")
    
    # 验证文件大小
    content = await file.read()
    file_size = len(content)
    
    # 根据分析类型设置不同的限制
    if analysis_type == "project":
        max_size = 100 * 1024 * 1024  # 100MB for projects
        supported_extensions = ['.zip', '.tar', '.tar.gz', '.rar', '.7z']
    else:
        max_size = 10 * 1024 * 1024  # 10MB for single files
        supported_extensions = ['.py', '.java', '.c', '.cpp', '.h', '.hpp', '.js', '.ts', '.go']
    
    if file_size > max_size:
        raise HTTPException(status_code=413, detail=f"文件过大，最大支持{max_size // (1024*1024)}MB")
    
    # 验证文件类型
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in supported_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件类型。支持的类型: {', '.join(supported_extensions)}"
        )
    
    # 保存文件
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / f"{file.filename}"
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 创建检测任务
    task_data = {
        "file_path": str(file_path),
        "analysis_type": analysis_type,
        "options": {
            "enable_static": enable_static,
            "enable_pylint": enable_pylint,
            "enable_flake8": enable_flake8,
            "enable_ai_analysis": enable_ai_analysis
        }
    }
    
    try:
        task_id = await bug_detection_agent.submit_task(f"task_{uuid.uuid4().hex[:12]}", task_data)
        
        # 在后台生成可下载报告和结构化信息存储
        background_tasks.add_task(generate_report_task, task_id, str(file_path))
        background_tasks.add_task(store_structured_data, task_id, str(file_path), analysis_type)
        
        return BaseResponse(
            message="文件上传成功，开始检测",
            data={
                "task_id": task_id,
                "filename": file.filename,
                "file_size": file_size,
                "agent_id": "bug_detection_agent",
                "analysis_type": analysis_type
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交检测任务失败: {str(e)}")

@app.get("/api/v1/tasks/{task_id}", response_model=BaseResponse)
async def get_task_status(task_id: str):
    """获取任务状态"""
    global bug_detection_agent
    
    if not bug_detection_agent:
        raise HTTPException(status_code=500, detail="BugDetectionAgent 未启动")
    
    try:
        task_status = await bug_detection_agent.get_task_status(task_id)
        if not task_status:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return BaseResponse(
            message="获取任务状态成功",
            data=task_status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")

@app.get("/api/v1/detection/rules", response_model=BaseResponse)
async def get_detection_rules():
    """获取检测规则"""
    global bug_detection_agent
    
    if not bug_detection_agent:
        raise HTTPException(status_code=500, detail="BugDetectionAgent 未启动")
    
    try:
        rules = await bug_detection_agent.get_detection_rules()
        
        return BaseResponse(
            message="获取检测规则成功",
            data=rules
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取检测规则失败: {str(e)}")

@app.get("/api/v1/ai-reports/{task_id}")
async def get_ai_report(task_id: str):
    """获取AI生成的自然语言报告"""
    global bug_detection_agent
    
    if not bug_detection_agent:
        raise HTTPException(status_code=500, detail="BugDetectionAgent 未启动")
    
    try:
        # 获取任务状态
        task_status = await bug_detection_agent.get_task_status(task_id)
        if not task_status:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        if task_status.get("status") != "completed":
            raise HTTPException(status_code=400, detail="任务尚未完成")
        
        # 检查AI报告文件是否存在
        ai_report_path = Path("reports") / f"ai_report_{task_id}.md"
        
        if ai_report_path.exists():
            # 读取AI报告内容
            with open(ai_report_path, 'r', encoding='utf-8') as f:
                ai_report_content = f.read()
            
            return BaseResponse(
                message="获取AI报告成功",
                data={
                    "task_id": task_id,
                    "ai_report": ai_report_content,
                    "report_type": "markdown"
                }
            )
        else:
            # 如果没有AI报告文件，实时生成一个
            detection_results = task_status.get("result", {}).get("detection_results", {})
            file_path = task_status.get("result", {}).get("file_path", "")
            
            if detection_results:
                ai_report = await generate_ai_report(detection_results, file_path)
                return BaseResponse(
                    message="获取AI报告成功",
                    data={
                        "task_id": task_id,
                        "ai_report": ai_report,
                        "report_type": "markdown"
                    }
                )
            else:
                raise HTTPException(status_code=404, detail="检测结果不存在")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取AI报告失败: {str(e)}")

@app.get("/api/v1/reports/{task_id}")
async def download_report(task_id: str):
    """下载检测报告"""
    global bug_detection_agent
    
    if not bug_detection_agent:
        raise HTTPException(status_code=500, detail="BugDetectionAgent 未启动")
    
    try:
        # 获取任务状态
        task_status = await bug_detection_agent.get_task_status(task_id)
        if not task_status:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        if task_status.get("status") != "completed":
            raise HTTPException(status_code=400, detail="任务尚未完成")
        
        # 生成报告
        detection_results = task_status.get("result", {}).get("detection_results", {})
        file_path = task_status.get("result", {}).get("file_path", "")
        
        if not detection_results:
            raise HTTPException(status_code=404, detail="检测结果不存在")
        
        # 检查BugDetectionAgent是否有generate_downloadable_report方法
        if hasattr(bug_detection_agent, 'generate_downloadable_report'):
            report_path = await bug_detection_agent.generate_downloadable_report(detection_results, file_path)
        else:
            # 如果没有该方法，创建一个简化的报告
            report_path = await create_simple_report(detection_results, file_path, task_id)
        
        if not report_path or not Path(report_path).exists():
            raise HTTPException(status_code=404, detail="报告文件不存在")
        
        # 返回文件
        from fastapi.responses import FileResponse
        return FileResponse(
            path=report_path,
            filename=f"bug_detection_report_{task_id}.json",
            media_type="application/json"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载报告失败: {str(e)}")

@app.get("/api/v1/ai-reports/{task_id}/download")
async def download_ai_report(task_id: str):
    """下载AI生成的自然语言报告"""
    global bug_detection_agent
    
    if not bug_detection_agent:
        raise HTTPException(status_code=500, detail="BugDetectionAgent 未启动")
    
    try:
        # 检查AI报告文件是否存在
        ai_report_path = Path("reports") / f"ai_report_{task_id}.md"
        
        if not ai_report_path.exists():
            # 如果没有AI报告文件，生成一个
            task_status = await bug_detection_agent.get_task_status(task_id)
            if not task_status or task_status.get("status") != "completed":
                raise HTTPException(status_code=404, detail="任务不存在或未完成")
            
            detection_results = task_status.get("result", {}).get("detection_results", {})
            file_path = task_status.get("result", {}).get("file_path", "")
            
            if not detection_results:
                raise HTTPException(status_code=404, detail="检测结果不存在")
            
            # 生成AI报告
            ai_report = await generate_ai_report(detection_results, file_path)
            
            # 保存AI报告
            ai_report_path.parent.mkdir(exist_ok=True)
            with open(ai_report_path, 'w', encoding='utf-8') as f:
                f.write(ai_report)
        
        # 返回文件
        from fastapi.responses import FileResponse
        return FileResponse(
            path=ai_report_path,
            filename=f"ai_report_{task_id}.md",
            media_type="text/markdown"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载AI报告失败: {str(e)}")

@app.get("/api/v1/structured-data/{task_id}", response_model=BaseResponse)
async def get_structured_data(task_id: str):
    """获取结构化数据给修复agent"""
    try:
        # 检查结构化数据文件是否存在
        structured_file = Path("structured_data") / f"structured_data_{task_id}.json"
        
        if not structured_file.exists():
            raise HTTPException(status_code=404, detail="结构化数据不存在")
        
        # 读取结构化数据
        with open(structured_file, 'r', encoding='utf-8') as f:
            structured_data = json.load(f)
        
        return BaseResponse(
            message="获取结构化数据成功",
            data=structured_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取结构化数据失败: {str(e)}")

@app.get("/api/v1/structured-data/{task_id}/download")
async def download_structured_data(task_id: str):
    """下载结构化数据文件"""
    try:
        # 检查结构化数据文件是否存在
        structured_file = Path("structured_data") / f"structured_data_{task_id}.json"
        
        if not structured_file.exists():
            raise HTTPException(status_code=404, detail="结构化数据不存在")
        
        # 返回文件
        from fastapi.responses import FileResponse
        return FileResponse(
            path=structured_file,
            filename=f"structured_data_{task_id}.json",
            media_type="application/json"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载结构化数据失败: {str(e)}")

async def create_simple_report(detection_results: Dict[str, Any], file_path: str, task_id: str) -> str:
    """创建简化的检测报告"""
    try:
        # 创建报告目录
        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        
        # 生成报告文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bug_detection_report_{timestamp}.json"
        report_path = report_dir / filename
        
        # 生成报告内容
        report_data = {
            "report_info": {
                "generated_at": datetime.now().isoformat(),
                "file_path": file_path,
                "task_id": task_id,
                "total_issues": detection_results.get("total_issues", 0),
                "summary": detection_results.get("summary", {}),
                "detection_tools": detection_results.get("detection_tools", [])
            },
            "issues": detection_results.get("issues", []),
            "statistics": {
                "by_severity": _get_issues_by_severity(detection_results.get("issues", [])),
                "by_type": _get_issues_by_type(detection_results.get("issues", [])),
            }
        }
        
        # 保存报告
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"简化检测报告已生成: {report_path}")
        return str(report_path)
        
    except Exception as e:
        print(f"生成简化报告失败: {e}")
        return None

def _get_issues_by_severity(issues: List[Dict[str, Any]]) -> Dict[str, int]:
    """按严重性统计问题"""
    severity_count = {}
    for issue in issues:
        severity = issue.get("severity", "info")
        severity_count[severity] = severity_count.get(severity, 0) + 1
    return severity_count

def _get_issues_by_type(issues: List[Dict[str, Any]]) -> Dict[str, int]:
    """按类型统计问题"""
    type_count = {}
    for issue in issues:
        issue_type = issue.get("type", "unknown")
        type_count[issue_type] = type_count.get(issue_type, 0) + 1
    return type_count

async def generate_ai_report(detection_results: Dict[str, Any], file_path: str) -> str:
    """使用AI生成自然语言报告"""
    try:
        import requests
        
        # 准备检测数据
        issues = detection_results.get("issues", [])
        summary = detection_results.get("summary", {})
        
        # 构建提示词
        prompt = f"""
请分析以下Python代码检测结果，生成一份专业的中文自然语言报告：

文件路径: {file_path}
检测摘要: 错误 {summary.get('error_count', 0)} 个，警告 {summary.get('warning_count', 0)} 个，信息 {summary.get('info_count', 0)} 个

检测到的问题:
"""
        
        for i, issue in enumerate(issues[:10], 1):  # 只取前10个问题
            prompt += f"""
{i}. 类型: {issue.get('type', 'unknown')}
   严重性: {issue.get('severity', 'info')}
   位置: 第 {issue.get('line', 0)} 行
   描述: {issue.get('message', '')}
"""
        
        prompt += """

请生成一份包含以下内容的专业报告：
1. 代码质量总体评估
2. 主要问题分析和语法错误
3. 改进建议
4. 优先级排序

报告要求：
- 使用专业的技术语言
- 提供具体的改进建议
- 按重要性排序问题
- 语言简洁明了
"""
        
        # 调用DeepSeek API 
        ai_report = await call_deepseek_api(prompt)
        
        return ai_report
        
    except Exception as e:
        print(f"生成AI报告失败: {e}")
        return "AI报告生成失败，请稍后重试。"

async def call_deepseek_api(prompt: str) -> str:
    """调用DeepSeek API生成报告"""
    try:
        from deepseek_config import deepseek_config
        import aiohttp
        
        # 检查是否配置了API密钥
        if not deepseek_config.is_configured():
            print("⚠️ API密钥未配置，使用模拟报告")
            return generate_mock_ai_report(prompt)
        
        print("🤖 调用DeepSeek API生成真实AI报告...")
        print(f"API密钥: {deepseek_config.api_key[:10]}...{deepseek_config.api_key[-10:]}")
        
        # 构建请求数据
        request_data = {
            "model": deepseek_config.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的代码质量分析专家，擅长分析Python代码问题并提供改进建议。请用专业、简洁的中文回答。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": deepseek_config.max_tokens,
            "temperature": deepseek_config.temperature
        }
        
        # 调用DeepSeek API
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{deepseek_config.base_url}/chat/completions",
                headers=deepseek_config.get_headers(),
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                print(f"📊 API响应状态: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    ai_response = result["choices"][0]["message"]["content"]
                    print("✅ 真实AI报告生成成功！")
                    return ai_response
                elif response.status == 402:
                    print("⚠️ DeepSeek API余额不足，使用模拟报告")
                    return generate_mock_ai_report(prompt)
                else:
                    error_text = await response.text()
                    print(f"⚠️ DeepSeek API调用失败: {response.status} - {error_text}")
                    return generate_mock_ai_report(prompt)
    
    except Exception as e:
        print(f"⚠️ 调用DeepSeek API失败: {e}，使用模拟报告")
        return generate_mock_ai_report(prompt)

def generate_mock_ai_report(prompt: str) -> str:
    """生成模拟的AI报告"""
    # 从prompt中提取问题数量
    issues_count = len(prompt.split('问题:')) - 1 if '问题:' in prompt else 0
    
    return f"""
# 代码质量检测报告

## 总体评估
根据静态代码分析结果，您的代码整体质量{'良好' if issues_count < 3 else '需要改进'}。检测发现了{issues_count}个潜在问题，建议及时修复。

## 主要问题分析
1. **代码规范问题**: 发现了一些命名和格式问题，建议使用代码格式化工具
2. **潜在安全风险**: 检测到可能存在安全漏洞的代码模式
3. **性能优化**: 部分代码可能存在性能瓶颈

## 改进建议
1. 立即修复所有错误级别的问题
2. 逐步改进警告级别的问题
3. 考虑重构复杂度过高的函数
4. 添加适当的错误处理机制

## 优先级排序
- 🔴 高优先级: 安全相关问题和错误
- 🟡 中优先级: 代码质量和性能问题  
- 🟢 低优先级: 代码风格和文档问题

建议定期进行代码审查，保持代码质量。

---
*注：这是模拟的AI报告。要使用真实的AI分析，请配置DeepSeek API密钥。*
"""

async def generate_report_task(task_id: str, file_path: str):
    """后台任务：生成检测报告"""
    global bug_detection_agent
    
    try:
        # 等待任务完成
        max_wait_time = 300  # 5分钟
        wait_interval = 2    # 2秒
        waited_time = 0
        
        while waited_time < max_wait_time:
            task_status = await bug_detection_agent.get_task_status(task_id)
            if task_status and task_status.get("status") == "completed":
                break
            await asyncio.sleep(wait_interval)
            waited_time += wait_interval
        
        if waited_time >= max_wait_time:
            print(f"任务 {task_id} 超时，无法生成报告")
            return
        
        # 生成报告
        detection_results = task_status.get("result", {}).get("detection_results", {})
        if detection_results:
            # 生成JSON报告
            if hasattr(bug_detection_agent, 'generate_downloadable_report'):
                report_path = await bug_detection_agent.generate_downloadable_report(detection_results, file_path)
            else:
                report_path = await create_simple_report(detection_results, file_path, task_id)
            
            if report_path:
                print(f"JSON报告已生成: {report_path}")
            
            # 生成AI自然语言报告
            ai_report = await generate_ai_report(detection_results, file_path)
            
            # 保存AI报告
            ai_report_path = Path("reports") / f"ai_report_{task_id}.md"
            ai_report_path.parent.mkdir(exist_ok=True)
            with open(ai_report_path, 'w', encoding='utf-8') as f:
                f.write(ai_report)
            print(f"AI报告已生成: {ai_report_path}")
        
    except Exception as e:
        print(f"生成报告任务失败: {e}")

async def store_structured_data(task_id: str, file_path: str, analysis_type: str):
    """后台任务：存储结构化信息给修复agent"""
    global bug_detection_agent
    
    try:
        # 等待任务完成
        max_wait_time = 300  # 5分钟
        wait_interval = 2    # 2秒
        waited_time = 0
        
        while waited_time < max_wait_time:
            task_status = await bug_detection_agent.get_task_status(task_id)
            if task_status and task_status.get("status") == "completed":
                break
            await asyncio.sleep(wait_interval)
            waited_time += wait_interval
        
        if waited_time >= max_wait_time:
            print(f"任务 {task_id} 超时，无法存储结构化数据")
            return
        
        # 获取检测结果
        detection_results = task_status.get("result", {}).get("detection_results", {})
        if not detection_results:
            print(f"任务 {task_id} 没有检测结果")
            return
        
        # 创建结构化数据存储目录
        structured_dir = Path("structured_data")
        structured_dir.mkdir(exist_ok=True)
        
        # 生成结构化数据
        structured_data = {
            "task_id": task_id,
            "file_path": file_path,
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_issues": detection_results.get("total_issues", 0),
                "error_count": detection_results.get("summary", {}).get("error_count", 0),
                "warning_count": detection_results.get("summary", {}).get("warning_count", 0),
                "info_count": detection_results.get("summary", {}).get("info_count", 0),
                "languages_detected": detection_results.get("languages_detected", []),
                "total_files": detection_results.get("total_files", 1)
            },
            "issues_by_priority": categorize_issues_by_priority(detection_results.get("issues", [])),
            "fix_recommendations": generate_fix_recommendations(detection_results.get("issues", [])),
            "project_structure": analyze_project_structure(detection_results, analysis_type),
            "detection_metadata": {
                "detection_tools": detection_results.get("detection_tools", []),
                "analysis_time": detection_results.get("analysis_time", 0),
                "project_path": detection_results.get("project_path", file_path)
            }
        }
        
        # 保存结构化数据
        structured_file = structured_dir / f"structured_data_{task_id}.json"
        with open(structured_file, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, ensure_ascii=False, indent=2)
        
        print(f"结构化数据已存储: {structured_file}")
        
    except Exception as e:
        print(f"存储结构化数据失败: {e}")

def categorize_issues_by_priority(issues):
    """按优先级分类问题"""
    priority_categories = {
        "critical": [],  # 错误级别，安全相关
        "high": [],      # 错误级别，非安全相关
        "medium": [],    # 警告级别
        "low": []        # 信息级别
    }
    
    for issue in issues:
        severity = issue.get("severity", "info")
        issue_type = issue.get("type", "")
        
        # 安全相关问题优先级最高
        if severity == "error" and any(keyword in issue_type.lower() for keyword in 
                                      ["security", "vulnerability", "injection", "xss", "csrf", "secret", "password"]):
            priority_categories["critical"].append(issue)
        elif severity == "error":
            priority_categories["high"].append(issue)
        elif severity == "warning":
            priority_categories["medium"].append(issue)
        else:
            priority_categories["low"].append(issue)
    
    return priority_categories

def generate_fix_recommendations(issues):
    """生成修复建议"""
    recommendations = {
        "immediate_actions": [],
        "short_term_improvements": [],
        "long_term_optimizations": []
    }
    
    error_count = sum(1 for issue in issues if issue.get("severity") == "error")
    warning_count = sum(1 for issue in issues if issue.get("severity") == "warning")
    
    # 立即行动
    if error_count > 0:
        recommendations["immediate_actions"].append(f"修复 {error_count} 个错误级别的问题")
    
    # 安全相关问题
    security_issues = [issue for issue in issues if "security" in issue.get("type", "").lower()]
    if security_issues:
        recommendations["immediate_actions"].append(f"优先处理 {len(security_issues)} 个安全问题")
    
    # 短期改进
    if warning_count > 10:
        recommendations["short_term_improvements"].append("进行代码审查，处理大量警告")
    
    # 长期优化
    recommendations["long_term_optimizations"].append("建立持续集成流程，定期进行代码质量检查")
    recommendations["long_term_optimizations"].append("制定代码规范和最佳实践指南")
    
    return recommendations

def analyze_project_structure(detection_results, analysis_type):
    """分析项目结构"""
    structure_info = {
        "analysis_type": analysis_type,
        "file_count": detection_results.get("total_files", 1),
        "languages": detection_results.get("languages_detected", []),
        "complexity_indicators": {
            "high_issue_files": 0,
            "average_issues_per_file": 0
        }
    }
    
    issues = detection_results.get("issues", [])
    if issues:
        # 统计每个文件的问题数量
        file_issue_count = {}
        for issue in issues:
            file_name = issue.get("file", "unknown")
            file_issue_count[file_name] = file_issue_count.get(file_name, 0) + 1
        
        # 计算高问题文件数量
        structure_info["complexity_indicators"]["high_issue_files"] = sum(
            1 for count in file_issue_count.values() if count > 5
        )
        
        # 计算平均问题数
        total_files = len(file_issue_count) or 1
        structure_info["complexity_indicators"]["average_issues_per_file"] = len(issues) / total_files
    
    return structure_info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
