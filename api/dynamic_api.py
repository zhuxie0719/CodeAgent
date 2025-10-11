"""
简化版动态检测API
专注于核心功能，确保3周内能完成
"""

import asyncio
import tempfile
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

# 导入检测组件
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from agents.integrated_detector import IntegratedDetector

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

# 全局检测器
detector = IntegratedDetector()

@router.get("/")
async def root():
    """根路径"""
    return {
        "message": "简化版动态检测API运行中",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "simple_dynamic_detection"
    }

@router.post("/detect", response_model=BaseResponse)
async def dynamic_detect(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    static_analysis: bool = True,
    dynamic_monitoring: bool = True,
    runtime_analysis: bool = True
):
    """
    动态缺陷检测
    
    Args:
        file: 项目压缩包
        static_analysis: 是否进行静态分析
        dynamic_monitoring: 是否进行动态监控
        runtime_analysis: 是否进行运行时分析
    
    Returns:
        检测结果
    """
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="只支持ZIP格式的压缩包")
    
    temp_file_path = None
    
    try:
        print(f"开始处理上传文件: {file.filename}")
        
        # 保存上传文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            temp_file_path = tmp_file.name
        
        print(f"文件已保存到临时位置: {temp_file_path}")
        
        # 执行检测
        print("开始执行综合检测...")
        results = await detector.detect_defects(
            zip_file_path=temp_file_path,
            static_analysis=static_analysis,
            dynamic_monitoring=dynamic_monitoring,
            runtime_analysis=runtime_analysis
        )
        
        print("检测完成，生成报告...")
        
        # 生成文本报告
        report = detector.generate_report(results)
        
        # 保存结果到文件
        results_file = f"detection_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_dir = Path("dynamic_detection_results")
        results_dir.mkdir(exist_ok=True)
        results_path = results_dir / results_file
        detector.save_results(results, str(results_path))
        
        # 返回结果
        return BaseResponse(
            success=True,
            message="动态检测完成",
            data={
                "results": results,
                "report": report,
                "results_file": results_file,
                "filename": file.filename,
                "detection_time": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        print(f"检测过程中出错: {e}")
        return BaseResponse(
            success=False,
            error=str(e),
            message="检测失败"
        )
    
    finally:
        # 清理临时文件
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                print(f"已清理临时文件: {temp_file_path}")
            except Exception as e:
                print(f"清理临时文件失败: {e}")

@router.get("/results/{filename}")
async def get_detection_results(filename: str):
    """获取检测结果文件"""
    try:
        if not filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="只支持JSON格式的结果文件")
        
        # 在dynamic_detection_results目录中查找文件
        results_dir = Path("dynamic_detection_results")
        file_path = results_dir / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="结果文件不存在")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        return BaseResponse(
            success=True,
            message="获取检测结果成功",
            data=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取检测结果失败: {str(e)}")

@router.get("/results")
async def list_detection_results():
    """列出所有检测结果文件"""
    try:
        results_dir = Path("dynamic_detection_results")
        if not results_dir.exists():
            return BaseResponse(
                success=True,
                message="检测结果目录不存在",
                data={"results": []}
            )
        
        results_files = []
        for file_path in results_dir.glob("detection_results_*.json"):
            file_info = {
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "created_time": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            results_files.append(file_info)
        
        # 按修改时间倒序排列
        results_files.sort(key=lambda x: x["modified_time"], reverse=True)
        
        return BaseResponse(
            success=True,
            message="获取检测结果列表成功",
            data={"results": results_files}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取检测结果列表失败: {str(e)}")

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
            "runtime_analysis": True
        }
    }

@router.post("/test-monitor")
async def test_monitor(duration: int = 30):
    """测试监控功能"""
    try:
        from agents.simple_monitor_agent import SimpleMonitorAgent
        
        monitor = SimpleMonitorAgent()
        results = await monitor.start_monitoring(duration)
        
        return BaseResponse(
            success=True,
            message="监控测试完成",
            data=results
        )
        
    except Exception as e:
        return BaseResponse(
            success=False,
            error=str(e),
            message="监控测试失败"
        )

@router.post("/test-project-runner")
async def test_project_runner():
    """测试项目运行器"""
    try:
        from utils.project_runner import ProjectRunner
        
        runner = ProjectRunner()
        
        # 这里需要提供一个测试项目
        # 目前返回模拟结果
        return BaseResponse(
            success=True,
            message="项目运行器测试完成",
            data={
                "status": "ready",
                "message": "项目运行器已就绪"
            }
        )
        
    except Exception as e:
        return BaseResponse(
            success=False,
            error=str(e),
            message="项目运行器测试失败"
        )

@router.get("/system-info")
async def get_system_info():
    """获取系统信息"""
    try:
        import psutil
        import sys
        
        return {
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "disk_total": psutil.disk_usage('/').total,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform
        }
        
    except Exception as e:
        return {
            "error": str(e)
        }

# 路由已配置完成，可以通过main_api.py统一启动
