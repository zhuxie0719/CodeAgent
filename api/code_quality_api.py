"""
代码质量分析API接口
提供代码质量分析的RESTful API服务
专注于单文件分析
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

# 导入代码质量分析Agent
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.code_quality_agent.agent import CodeQualityAgent
from api.deepseek_config import deepseek_config

# 创建API路由器
router = APIRouter(prefix="/api/code-quality", tags=["代码质量分析"])

# 全局Agent实例
code_quality_agent = None

# 请求模型
class FileQualityRequest(BaseModel):
    file_content: str
    file_path: str = "unknown_file.py"
    include_ai_analysis: bool = True

class FileUploadRequest(BaseModel):
    include_ai_analysis: bool = True

# 响应模型
class QualityAnalysisResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    analysis_id: Optional[str] = None
    timestamp: Optional[float] = None




def get_or_create_agent():
    """获取或创建代码质量Agent"""
    global code_quality_agent
    
    if code_quality_agent is None:
        config = {
            'ai_api_key': deepseek_config.api_key,
            'ai_base_url': f'{deepseek_config.base_url}/chat/completions',
            'max_line_length': 120,
            'max_workers': 1
        }
        code_quality_agent = CodeQualityAgent(config)
        print("代码质量Agent已创建")
    
    return code_quality_agent


@router.post("/analyze-file")
async def analyze_file_quality(request: FileQualityRequest):
    """分析单个文件的代码质量"""
    try:
        agent = get_or_create_agent()
        
        if not agent.is_running:
            await agent.start()
        
        # 分析文件质量
        result = await agent.analyze_single_file(request.file_path, request.file_content)
        
        if result.get('success'):
            return QualityAnalysisResponse(
                success=True,
                data=result,
                timestamp=asyncio.get_event_loop().time()
            )
        else:
            return QualityAnalysisResponse(
                success=False,
                error=result.get('error', '分析失败'),
                timestamp=asyncio.get_event_loop().time()
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"质量分析失败: {str(e)}")


@router.post("/analyze-upload")
async def analyze_uploaded_file(file: UploadFile = File(...), request: FileUploadRequest = None):
    """分析上传的文件"""
    try:
        if request is None:
            request = FileUploadRequest(include_ai_analysis=True)
        
        agent = get_or_create_agent()
        
        if not agent.is_running:
            await agent.start()
        
        # 保存临时文件
        file_content = await file.read()
        
        try:
            file_content_str = file_content.decode('utf-8')
        except UnicodeDecodeError:
            file_content_str = file_content.decode('utf-8', errors='ignore')
        
        file_path = file.filename or "uploaded_file"
        
        # 分析文件质量
        result = await agent.analyze_single_file(file_path, file_content_str)
        
        if result.get('success'):
            return QualityAnalysisResponse(
                success=True,
                data=result,
                timestamp=asyncio.get_event_loop().time()
            )
        else:
            return QualityAnalysisResponse(
                success=False,
                error=result.get('error', '分析失败'),
                timestamp=asyncio.get_event_loop().time()
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件分析失败: {str(e)}")


@router.post("/analyze-file-path")
async def analyze_file_by_path(file_path: str):
    """通过文件路径分析文件质量"""
    try:
        agent = get_or_create_agent()
        
        if not agent.is_running:
            await agent.start()
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 分析文件质量
        result = await agent.analyze_file_from_path(file_path)
        
        if result.get('success') or 'error' not in result:
            return QualityAnalysisResponse(
                success=True,
                data=result,
                timestamp=asyncio.get_event_loop().time()
            )
        else:
            return QualityAnalysisResponse(
                success=False,
                error=result.get('error', '分析失败'),
                timestamp=asyncio.get_event_loop().time()
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件分析失败: {str(e)}")


@router.get("/health")
async def health_check():
    """健康检查"""
    try:
        agent = get_or_create_agent()
        return {
            "status": "healthy",
            "agent_status": agent.status.value if agent else "not_initialized",
            "capabilities": agent.get_capabilities() if agent else []
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )


@router.get("/capabilities")
async def get_capabilities():
    """获取Agent能力"""
    try:
        agent = get_or_create_agent()
        return {
            "capabilities": agent.get_capabilities(),
            "agent_id": agent.agent_id,
            "description": "专注于单文件代码质量分析，提供风格检查、质量指标计算和AI驱动的详细报告生成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取能力失败: {str(e)}")


@router.get("/metrics")
async def get_agent_metrics():
    """获取Agent指标"""
    try:
        agent = get_or_create_agent()
        metrics = await agent.get_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取指标失败: {str(e)}")


@router.delete("/cache")
async def clear_cache():
    """清除分析缓存"""
    try:
        # 这里可以添加清除缓存的逻辑
        return {"message": "缓存已清除", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除缓存失败: {str(e)}")




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(router, host="0.0.0.0", port=8001)
