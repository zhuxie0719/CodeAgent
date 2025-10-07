"""
简化版代码分析API接口
移除AI服务依赖，提供基本的代码分析功能
"""

import os
import json
import asyncio
import time
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import tempfile
import shutil
from pathlib import Path

# 创建API路由器
router = APIRouter(prefix="/api/simple-code-analysis", tags=["简化代码分析"])

# 请求模型
class SimpleAnalysisRequest(BaseModel):
    """简化分析请求模型"""
    project_path: str
    include_ai_analysis: bool = False
    analysis_depth: str = "basic"

class SimpleAnalysisResponse(BaseModel):
    """简化分析响应模型"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str = ""

def analyze_file_basic(file_path: str) -> Dict[str, Any]:
    """基础文件分析"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        total_lines = len(lines)
        non_empty_lines = len([line for line in lines if line.strip()])
        
        # 基础统计
        stats = {
            'file_name': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path),
            'total_lines': total_lines,
            'non_empty_lines': non_empty_lines,
            'file_extension': os.path.splitext(file_path)[1],
            'has_functions': 'def ' in content,
            'has_classes': 'class ' in content,
            'has_imports': 'import ' in content or 'from ' in content
        }
        
        return stats
    except Exception as e:
        return {'error': f'分析文件失败: {str(e)}'}

def analyze_project_basic(project_path: str) -> Dict[str, Any]:
    """基础项目分析"""
    try:
        if not os.path.exists(project_path):
            return {'error': f'项目路径不存在: {project_path}'}
        
        files = []
        total_files = 0
        total_lines = 0
        file_types = {}
        
        for root, dirs, filenames in os.walk(project_path):
            # 跳过隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for filename in filenames:
                if filename.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, filename)
                file_ext = os.path.splitext(filename)[1]
                
                if file_ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h']:
                    file_stats = analyze_file_basic(file_path)
                    if 'error' not in file_stats:
                        files.append(file_stats)
                        total_files += 1
                        total_lines += file_stats.get('total_lines', 0)
                        
                        if file_ext not in file_types:
                            file_types[file_ext] = 0
                        file_types[file_ext] += 1
        
        return {
            'project_path': project_path,
            'total_files': total_files,
            'total_lines': total_lines,
            'file_types': file_types,
            'files': files[:10],  # 只返回前10个文件
            'project_type': 'code_project',
            'analysis_type': 'basic'
        }
    except Exception as e:
        return {'error': f'分析项目失败: {str(e)}'}

@router.post("/analyze-upload", response_model=SimpleAnalysisResponse)
async def analyze_uploaded_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    include_ai_analysis: bool = False,
    analysis_depth: str = "basic"
):
    """分析上传的文件（简化版）"""
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp(prefix="simple_code_analysis_")
        
        try:
            # 保存上传的文件
            for file in files:
                if file.filename:
                    file_path = os.path.join(temp_dir, file.filename)
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(file.file, buffer)
            
            # 执行基础分析
            result = analyze_project_basic(temp_dir)
            
            if 'error' in result:
                return SimpleAnalysisResponse(
                    success=False,
                    error=result['error'],
                    timestamp=str(time.time())
                )
            
            # 添加简单的AI摘要（不调用外部API）
            ai_summary = {
                'success': True,
                'summary': f"项目分析完成。共发现 {result['total_files']} 个代码文件，总计 {result['total_lines']} 行代码。主要文件类型: {', '.join(result['file_types'].keys())}。"
            }
            
            result['ai_summary'] = ai_summary
            
            return SimpleAnalysisResponse(
                success=True,
                data=result,
                timestamp=str(time.time())
            )
            
        finally:
            # 清理临时目录
            background_tasks.add_task(cleanup_temp_dir, temp_dir)
            
    except Exception as e:
        return SimpleAnalysisResponse(
            success=False,
            error=f"分析失败: {str(e)}",
            timestamp=asyncio.get_event_loop().time()
        )

@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "simple_code_analysis"}

def cleanup_temp_dir(temp_dir: str):
    """清理临时目录"""
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"清理临时目录失败: {e}")
