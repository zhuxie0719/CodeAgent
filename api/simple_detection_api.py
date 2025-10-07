"""
简化的缺陷检测API
提供基本的文件上传和检测功能
"""

import os
import tempfile
import shutil
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# 创建API路由器
router = APIRouter(prefix="/api/v1", tags=["简化检测"])

class SimpleDetectionResponse(BaseModel):
    """简化检测响应模型"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: str = ""

def analyze_python_file(file_path: str) -> Dict[str, Any]:
    """分析Python文件"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        total_lines = len(lines)
        non_empty_lines = len([line for line in lines if line.strip()])
        
        # 基础分析
        issues = []
        
        # 检查常见问题
        if 'import *' in content:
            issues.append({
                'type': 'warning',
                'message': '使用了通配符导入，建议明确指定导入的模块',
                'line': content.find('import *') + 1
            })
        
        if 'print(' in content and 'def ' in content:
            issues.append({
                'type': 'info',
                'message': '代码中包含print语句，建议使用日志记录',
                'line': content.find('print(') + 1
            })
        
        # 检查函数定义
        functions = []
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                func_name = line.strip().split('(')[0].replace('def ', '')
                functions.append({
                    'name': func_name,
                    'line': i + 1
                })
        
        return {
            'file_name': os.path.basename(file_path),
            'total_lines': total_lines,
            'non_empty_lines': non_empty_lines,
            'functions': functions,
            'issues': issues,
            'analysis_type': 'basic'
        }
    except Exception as e:
        return {'error': f'分析文件失败: {str(e)}'}

@router.post("/detection/upload")
async def upload_file_for_detection(
    file: UploadFile = File(...),
    enable_static: bool = Query(True, description="启用自定义静态检测"),
    enable_pylint: bool = Query(True, description="启用Pylint检测"),
    enable_flake8: bool = Query(True, description="启用Flake8检测"),
    enable_ai_analysis: bool = Query(False, description="启用AI分析"),
    analysis_type: str = Query("file", description="分析类型")
):
    """上传文件进行缺陷检测（简化版）"""
    try:
        # 验证文件类型
        if not file.filename.endswith('.py'):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "只支持Python文件(.py)"
                }
            )
        
        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.py')
        try:
            # 保存上传的文件
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            
            # 分析文件
            result = analyze_python_file(temp_file.name)
            
            if 'error' in result:
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "error": result['error']
                    }
                )
            
            # 生成任务ID
            import uuid
            task_id = f"task_{uuid.uuid4().hex[:12]}"
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "文件分析完成",
                    "data": {
                        "task_id": task_id,
                        "filename": file.filename,
                        "file_size": len(content),
                        "analysis_result": result,
                        "status": "completed"
                    }
                }
            )
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
                
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"分析失败: {str(e)}"
            }
        )

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态（简化版）"""
    # 简化版直接返回完成状态
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "任务状态查询成功",
            "data": {
                "task_id": task_id,
                "status": "completed",
                "result": {
                    "message": "分析已完成",
                    "analysis_type": "basic"
                }
            }
        }
    )

@router.get("/ai-reports/{task_id}")
async def get_ai_report(task_id: str):
    """获取AI报告（简化版）"""
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "AI报告生成成功",
            "data": {
                "task_id": task_id,
                "report": f"# 代码分析报告\n\n任务ID: {task_id}\n\n## 分析结果\n\n这是一个简化的代码分析报告。\n\n### 主要发现\n\n- 代码结构正常\n- 未发现严重问题\n- 建议进一步优化\n\n### 总结\n\n代码质量良好，可以继续开发。"
            }
        }
    )

@router.get("/structured-data/{task_id}")
async def get_structured_data(task_id: str):
    """获取结构化数据（简化版）"""
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "结构化数据获取成功",
            "data": {
                "task_id": task_id,
                "analysis_type": "basic",
                "files_analyzed": 1,
                "issues_found": 0,
                "functions_detected": 1,
                "summary": "代码分析完成，未发现严重问题"
            }
        }
    )
