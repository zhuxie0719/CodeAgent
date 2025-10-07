"""
代码分析API接口
提供代码分析Agent的RESTful API服务
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import tempfile
import shutil
from pathlib import Path

# 导入代码分析Agent
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.code_analysis_agent.agent import CodeAnalysisAgent
from api.deepseek_config import deepseek_config

# 创建API路由器
router = APIRouter(prefix="/api/code-analysis", tags=["代码分析"])

# 全局Agent实例
code_analysis_agent = None

# 请求模型
class AnalysisRequest(BaseModel):
    project_path: str
    analysis_depth: str = "comprehensive"  # basic, standard, comprehensive
    include_ai_analysis: bool = True
    include_dependency_graph: bool = True

class FileUploadRequest(BaseModel):
    include_ai_analysis: bool = True
    analysis_depth: str = "comprehensive"

# 响应模型
class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    analysis_id: Optional[str] = None
    timestamp: Optional[float] = None

class ProjectSummary(BaseModel):
    project_name: str
    project_type: str
    main_purpose: str
    key_features: List[str]
    technology_stack: List[str]
    complexity_level: str
    maintainability_score: float
    confidence: float

class CodeQualityMetrics(BaseModel):
    average_complexity: float
    average_maintainability: float
    total_issues: int
    error_count: int
    warning_count: int
    files_analyzed: int

class DependencyInfo(BaseModel):
    python_packages: List[Dict[str, Any]]
    node_modules: List[str]
    external_dependencies: List[Dict[str, Any]]
    internal_dependencies: List[str]
    circular_dependencies: List[List[str]]
    dependency_metrics: Dict[str, Any]

# 初始化Agent
def init_agent():
    global code_analysis_agent
    if code_analysis_agent is None:
        config = {
            'deepseek_api_key': deepseek_config.api_key,
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'supported_languages': ['python', 'javascript', 'typescript', 'java', 'cpp', 'c', 'go', 'rust'],
            'ai_analysis_enabled': True
        }
        code_analysis_agent = CodeAnalysisAgent(config)
        asyncio.create_task(code_analysis_agent.start())

# 启动时初始化
@router.on_event("startup")
async def startup_event():
    init_agent()

# 基础分析接口
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_project(request: AnalysisRequest):
    """分析项目代码"""
    try:
        if not code_analysis_agent:
            init_agent()
        
        # 检查项目路径是否存在
        if not os.path.exists(request.project_path):
            raise HTTPException(status_code=404, detail="项目路径不存在")
        
        # 执行分析
        result = await code_analysis_agent.analyze_project(request.project_path)
        
        if 'error' in result:
            return AnalysisResponse(
                success=False,
                error=result['error']
            )
        
        return AnalysisResponse(
            success=True,
            data=result,
            analysis_id=f"analysis_{int(result['analysis_metadata']['timestamp'])}",
            timestamp=result['analysis_metadata']['timestamp']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

# 文件上传分析接口
@router.post("/analyze-upload", response_model=AnalysisResponse)
async def analyze_uploaded_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    include_ai_analysis: bool = True,
    analysis_depth: str = "comprehensive"
):
    """分析上传的文件"""
    try:
        if not code_analysis_agent:
            init_agent()
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp(prefix="code_analysis_")
        
        try:
            # 保存上传的文件
            for file in files:
                if file.filename:
                    file_path = os.path.join(temp_dir, file.filename)
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(file.file, buffer)
            
            # 执行分析
            result = await code_analysis_agent.analyze_project(temp_dir)
            
            if 'error' in result:
                return AnalysisResponse(
                    success=False,
                    error=result['error']
                )
            
            # 添加清理任务
            background_tasks.add_task(cleanup_temp_dir, temp_dir)
            
            return AnalysisResponse(
                success=True,
                data=result,
                analysis_id=f"upload_analysis_{int(result['analysis_metadata']['timestamp'])}",
                timestamp=result['analysis_metadata']['timestamp']
            )
            
        except Exception as e:
            # 确保清理临时目录
            cleanup_temp_dir(temp_dir)
            raise e
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件分析失败: {str(e)}")

# 获取项目摘要
@router.get("/summary/{analysis_id}", response_model=ProjectSummary)
async def get_project_summary(analysis_id: str):
    """获取项目分析摘要"""
    try:
        # 这里应该从缓存或数据库获取分析结果
        # 暂时返回示例数据
        return ProjectSummary(
            project_name="示例项目",
            project_type="web_application",
            main_purpose="API服务开发",
            key_features=["RESTful API", "用户认证", "数据库集成"],
            technology_stack=["Python", "FastAPI", "SQLAlchemy"],
            complexity_level="中等",
            maintainability_score=75.5,
            confidence=0.85
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取摘要失败: {str(e)}")

# 获取代码质量指标
@router.get("/quality/{analysis_id}", response_model=CodeQualityMetrics)
async def get_code_quality(analysis_id: str):
    """获取代码质量指标"""
    try:
        # 这里应该从缓存或数据库获取分析结果
        return CodeQualityMetrics(
            average_complexity=5.2,
            average_maintainability=78.3,
            total_issues=12,
            error_count=2,
            warning_count=8,
            files_analyzed=25
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取质量指标失败: {str(e)}")

# 获取依赖信息
@router.get("/dependencies/{analysis_id}", response_model=DependencyInfo)
async def get_dependencies(analysis_id: str):
    """获取依赖关系信息"""
    try:
        # 这里应该从缓存或数据库获取分析结果
        return DependencyInfo(
            python_packages=[
                {"name": "fastapi", "version": "0.68.0", "constraint": "=="},
                {"name": "uvicorn", "version": "0.15.0", "constraint": "=="}
            ],
            node_modules=["express", "react", "typescript"],
            external_dependencies=[
                {"file": "main.py", "module": "fastapi"},
                {"file": "main.py", "module": "uvicorn"}
            ],
            internal_dependencies=["models", "services", "utils"],
            circular_dependencies=[],
            dependency_metrics={
                "total_external_deps": 15,
                "total_internal_deps": 8,
                "dependency_coupling": 0.3,
                "dependency_depth": 4
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取依赖信息失败: {str(e)}")

# 获取AI分析结果
@router.get("/ai-analysis/{analysis_id}")
async def get_ai_analysis(analysis_id: str):
    """获取AI分析结果"""
    try:
        # 这里应该从缓存或数据库获取AI分析结果
        # 暂时返回示例数据，实际应该从存储中获取
        return {
            "success": True,
            "ai_analysis": {
                "project_summary": "这是一个基于FastAPI的Web应用程序，具有RESTful API接口和用户认证功能。",
                "key_insights": [
                    "项目结构清晰，遵循了良好的代码组织原则",
                    "使用了现代Python Web框架FastAPI",
                    "代码质量整体良好，但存在一些可以改进的地方"
                ],
                "recommendations": [
                    "建议增加更多的单元测试覆盖",
                    "可以考虑使用依赖注入来降低耦合度",
                    "建议添加API文档和代码注释"
                ],
                "complexity_assessment": "项目复杂度适中，主要业务逻辑清晰，但部分函数可以进一步拆分以提高可读性。"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取AI分析失败: {str(e)}")

# 生成详细AI分析报告
@router.post("/generate-detailed-report")
async def generate_detailed_ai_report(request: AnalysisRequest):
    """生成详细的AI分析报告"""
    try:
        if not code_analysis_agent:
            init_agent()
        
        # 检查项目路径是否存在
        if not os.path.exists(request.project_path):
            raise HTTPException(status_code=404, detail="项目路径不存在")
        
        # 执行完整分析
        result = await code_analysis_agent.analyze_project(request.project_path)
        
        if 'error' in result:
            return AnalysisResponse(
                success=False,
                error=result['error']
            )
        
        # 生成详细的AI报告
        ai_summary = result.get('ai_summary', {})
        
        if ai_summary.get('success'):
            return {
                "success": True,
                "analysis_id": f"detailed_report_{int(result['analysis_metadata']['timestamp'])}",
                "detailed_report": ai_summary['summary'],
                "analysis_metadata": {
                    "timestamp": result['analysis_metadata']['timestamp'],
                    "project_path": request.project_path,
                    "analysis_depth": request.analysis_depth,
                    "ai_analysis_enabled": request.include_ai_analysis
                },
                "summary_data": ai_summary.get('analysis_data', {})
            }
        else:
            return {
                "success": False,
                "error": ai_summary.get('error', 'AI分析生成失败')
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成详细报告失败: {str(e)}")

# 获取单个文件的AI分析
@router.post("/analyze-file")
async def analyze_single_file(
    file_path: str,
    include_ai_analysis: bool = True
):
    """分析单个文件"""
    try:
        if not code_analysis_agent:
            init_agent()
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 执行文件分析
        result = await code_analysis_agent.code_analyzer.analyze_quality(os.path.dirname(file_path))
        
        # 获取该文件的特定分析结果
        file_complexity = result['complexity'].get(file_path)
        file_issues = [issue for issue in result['issues'] if issue.get('file') == file_path]
        
        response = {
            "success": True,
            "file_path": file_path,
            "file_size": len(content),
            "lines_of_code": len(content.splitlines()),
            "complexity_metrics": file_complexity,
            "issues": file_issues,
            "ai_analysis": None
        }
        
        # 如果启用AI分析
        if include_ai_analysis:
            ai_result = await code_analysis_agent.ai_service.analyze_code_intent(
                content, file_path, file_complexity, file_issues
            )
            if ai_result['success']:
                response['ai_analysis'] = ai_result['analysis']
            else:
                response['ai_analysis_error'] = ai_result.get('error')
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件分析失败: {str(e)}")

# 获取分析历史
@router.get("/history")
async def get_analysis_history(limit: int = 10, offset: int = 0):
    """获取分析历史"""
    try:
        # 这里应该从数据库获取分析历史
        return {
            "success": True,
            "history": [
                {
                    "analysis_id": "analysis_1234567890",
                    "project_name": "示例项目",
                    "timestamp": 1234567890.0,
                    "status": "completed",
                    "summary": "项目分析完成"
                }
            ],
            "total": 1,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史失败: {str(e)}")

# 删除分析结果
@router.delete("/analysis/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """删除分析结果"""
    try:
        # 这里应该从数据库删除分析结果
        return {
            "success": True,
            "message": f"分析结果 {analysis_id} 已删除"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

# 导出分析报告
@router.get("/export/{analysis_id}")
async def export_analysis_report(analysis_id: str, format: str = "json"):
    """导出分析报告"""
    try:
        if format not in ["json", "markdown", "html"]:
            raise HTTPException(status_code=400, detail="不支持的导出格式")
        
        # 这里应该生成并返回报告
        if format == "json":
            return JSONResponse(
                content={"message": f"JSON格式报告 {analysis_id}"},
                headers={"Content-Disposition": f"attachment; filename=analysis_{analysis_id}.json"}
            )
        elif format == "markdown":
            return JSONResponse(
                content={"message": f"Markdown格式报告 {analysis_id}"},
                headers={"Content-Disposition": f"attachment; filename=analysis_{analysis_id}.md"}
            )
        else:  # html
            return JSONResponse(
                content={"message": f"HTML格式报告 {analysis_id}"},
                headers={"Content-Disposition": f"attachment; filename=analysis_{analysis_id}.html"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")

# 健康检查
@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "agent_running": code_analysis_agent is not None,
        "ai_service_available": deepseek_config.is_configured(),
        "timestamp": asyncio.get_event_loop().time()
    }

# 工具函数
def cleanup_temp_dir(temp_dir: str):
    """清理临时目录"""
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"清理临时目录失败: {e}")

# 错误处理将在主应用中处理
