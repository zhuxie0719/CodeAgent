"""
综合检测API - 完整的检测服务
集成所有检测功能，包括Flask 2.0.0问题检测
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

# 导入检测组件
from agents.dynamic_detection_agent.agent import DynamicDetectionAgent
from agents.bug_detection_agent.agent import BugDetectionAgent
from deepseek_config import deepseek_config
from enhanced_detection import APIChangeDetection

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

# 创建FastAPI应用
app = FastAPI(
    title="综合检测API",
    description="完整的代码检测服务，包括Flask 2.0.0问题检测",
    version="1.0.0"
)

# 全局检测器
dynamic_agent = DynamicDetectionAgent({
    "api_key": deepseek_config.api_key,
    "base_url": deepseek_config.base_url,
    "model": deepseek_config.model
})

bug_agent = BugDetectionAgent({
    "api_key": deepseek_config.api_key,
    "base_url": deepseek_config.base_url,
    "model": deepseek_config.model
})

enhanced_detector = APIChangeDetection()

# 任务状态存储
tasks_state = {}

@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "dynamic_agent": "available",
            "bug_agent": "available", 
            "enhanced_detector": "available"
        }
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
            
            # 执行增强检测
            if static_analysis:
                tasks_state[task_id]["progress"] = 40
                enhanced_results = await enhanced_detector.detect_flask_2_0_0_issues(str(extract_path))
                tasks_state[task_id]["results"]["enhanced_detection"] = enhanced_results
            
            # 执行动态检测
            if dynamic_monitoring:
                tasks_state[task_id]["progress"] = 60
                dynamic_results = await dynamic_agent.detect_issues(extract_path)
                tasks_state[task_id]["results"]["dynamic_detection"] = dynamic_results
            
            # 执行缺陷检测
            if runtime_analysis:
                tasks_state[task_id]["progress"] = 80
                bug_results = await bug_agent.detect_issues(extract_path)
                tasks_state[task_id]["results"]["bug_detection"] = bug_results
            
            tasks_state[task_id]["progress"] = 100
            tasks_state[task_id]["status"] = "completed"
            tasks_state[task_id]["completed_at"] = datetime.now().isoformat()
            
            # 保存结果到文件
            result_file = Path("api/comprehensive_detection_results") / f"comprehensive_detection_results_{task_id}.json"
            result_file.parent.mkdir(exist_ok=True)
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_state[task_id], f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        tasks_state[task_id]["status"] = "failed"
        tasks_state[task_id]["error"] = str(e)
        tasks_state[task_id]["failed_at"] = datetime.now().isoformat()

if __name__ == "__main__":
    print("Starting Comprehensive Detection API...")
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
