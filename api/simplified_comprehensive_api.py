"""
简化的综合检测API - 用于测试
"""

import asyncio
import tempfile
import os
import json
import sys
import httpx
import shutil
import zipfile
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from pydantic import BaseModel, Field
import uvicorn

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 数据模型
class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(True, description="是否成功")
    message: str = Field("", description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息")

# 创建FastAPI应用
app = FastAPI(
    title="简化综合检测API",
    description="用于测试的简化检测服务",
    version="1.0.0"
)

# 任务状态存储
tasks_state = {}

@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "简化检测API运行正常"
    }

@app.post("/api/comprehensive/detect", response_model=BaseResponse)
async def comprehensive_detect(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    static_analysis: bool = Form(True),
    dynamic_monitoring: bool = Form(True),
    runtime_analysis: bool = Form(True)
):
    """综合检测接口"""
    try:
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 创建任务状态
        tasks_state[task_id] = {
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "progress": 0,
            "results": {}
        }
        
        # 后台处理任务
        background_tasks.add_task(
            process_comprehensive_detection,
            task_id,
            file,
            static_analysis,
            dynamic_monitoring,
            runtime_analysis
        )
        
        return BaseResponse(
            success=True,
            message="检测任务已启动",
            data={"task_id": task_id}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测启动失败: {str(e)}")

@app.get("/api/comprehensive/status/{task_id}")
async def get_detection_status(task_id: str):
    """获取检测状态"""
    if task_id not in tasks_state:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return tasks_state[task_id]

async def process_comprehensive_detection(
    task_id: str,
    file: UploadFile,
    static_analysis: bool,
    dynamic_monitoring: bool,
    runtime_analysis: bool
):
    """处理综合检测任务"""
    try:
        # 更新进度
        tasks_state[task_id]["progress"] = 10
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 保存上传的文件
            file_path = temp_path / file.filename
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            tasks_state[task_id]["progress"] = 20
            
            # 解压文件
            extract_path = temp_path / "extracted"
            extract_path.mkdir()
            
            if file.filename.endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
            
            tasks_state[task_id]["progress"] = 30
            
            # 模拟检测过程
            await asyncio.sleep(2)  # 模拟处理时间
            
            # 生成模拟结果
            mock_results = {
                "flask_issues": [
                    {
                        "id": "flask_2_0_0_issue_1",
                        "title": "Flask 2.0.0 兼容性问题",
                        "severity": "high",
                        "description": "检测到Flask 2.0.0版本兼容性问题",
                        "file": "app.py",
                        "line": 1
                    }
                ],
                "static_analysis": {
                    "issues_found": 1,
                    "files_analyzed": 1
                },
                "dynamic_analysis": {
                    "runtime_issues": 0,
                    "performance_issues": 0
                }
            }
            
            tasks_state[task_id]["progress"] = 100
            tasks_state[task_id]["status"] = "completed"
            tasks_state[task_id]["completed_at"] = datetime.now().isoformat()
            tasks_state[task_id]["results"] = mock_results
            
            # 保存结果到文件
            result_file = Path("comprehensive_detection_results") / f"comprehensive_detection_results_{task_id}.json"
            result_file.parent.mkdir(exist_ok=True)
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_state[task_id], f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        tasks_state[task_id]["status"] = "failed"
        tasks_state[task_id]["error"] = str(e)
        tasks_state[task_id]["failed_at"] = datetime.now().isoformat()

if __name__ == "__main__":
    print("Starting Simplified Comprehensive Detection API...")
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")

