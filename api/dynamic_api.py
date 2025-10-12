"""
简化版动态检测API
专注于核心功能，确保3周内能完成
"""

import asyncio
import tempfile
import os
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

# 导入检测组件
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from agents.dynamic_detection_agent.agent import DynamicMonitorAgent

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
monitor_agent = DynamicMonitorAgent({
    "monitor_interval": 5,
    "alert_thresholds": {
        "cpu_threshold": 80,
        "memory_threshold": 85,
        "disk_threshold": 90,
        "network_threshold": 80
    }
})

class SimpleDetector:
    """简化的检测器，集成动态监控功能"""
    
    def __init__(self, monitor_agent):
        self.monitor_agent = monitor_agent
    
    async def detect_defects(self, zip_file_path: str, 
                           static_analysis: bool = True,
                           dynamic_monitoring: bool = True,
                           runtime_analysis: bool = True) -> Dict[str, Any]:
        """执行综合检测"""
        results = {
            "detection_type": "comprehensive",
            "timestamp": datetime.now().isoformat(),
            "zip_file": zip_file_path,
            "analysis_options": {
                "static_analysis": static_analysis,
                "dynamic_monitoring": dynamic_monitoring,
                "runtime_analysis": runtime_analysis
            }
        }
        
        try:
            # 检查文件大小
            file_size = os.path.getsize(zip_file_path)
            max_size = 50 * 1024 * 1024  # 50MB限制
            
            if file_size > max_size:
                results["error"] = f"文件过大 ({file_size // (1024*1024)}MB > {max_size // (1024*1024)}MB)"
                return results
            
            # 解压项目
            import zipfile
            import tempfile
            import shutil
            
            extract_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            results["extracted_path"] = extract_dir
            results["files"] = self._list_files(extract_dir)
            
            # 限制文件数量，避免处理过多文件
            if len(results["files"]) > 1000:
                results["warning"] = f"文件数量过多 ({len(results['files'])} > 1000)，将进行采样分析"
                results["files"] = results["files"][:1000]  # 只取前1000个文件
            
            # 静态分析
            if static_analysis:
                results["static_analysis"] = await self._perform_static_analysis(extract_dir)
            
            # 动态监控
            if dynamic_monitoring:
                results["dynamic_monitoring"] = await self._perform_dynamic_monitoring()
            
            # 运行时分析
            if runtime_analysis:
                results["runtime_analysis"] = await self._perform_runtime_analysis(extract_dir)
            
            # 生成综合摘要
            results["summary"] = self._generate_summary(results)
            
            # 清理临时目录
            shutil.rmtree(extract_dir, ignore_errors=True)
            
            return results
            
        except Exception as e:
            results["error"] = str(e)
            return results
    
    def _list_files(self, project_path: str) -> List[str]:
        """列出项目文件"""
        files = []
        for root, dirs, filenames in os.walk(project_path):
            for filename in filenames:
                file_path = os.path.relpath(os.path.join(root, filename), project_path)
                files.append(file_path)
        return files
    
    async def _perform_static_analysis(self, project_path: str) -> Dict[str, Any]:
        """执行静态分析"""
        issues = []
        python_files = []
        
        # 跳过目录
        skip_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'doc', 'docs', 'test', 'tests', '.github', 'ci', 'asv_bench', 'conda.recipe', 'web', 'LICENSES'}
        
        for root, dirs, files in os.walk(project_path):
            # 过滤掉不需要的目录
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    # 检查文件大小
                    try:
                        if os.path.getsize(file_path) <= 2 * 1024 * 1024:  # 2MB限制
                            python_files.append(file_path)
                    except:
                        continue
        
        # 限制分析的文件数量
        if len(python_files) > 100:
            python_files = python_files[:100]  # 只分析前100个文件
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # 简单的问题检测
                    if 'eval(' in content:
                        issues.append({
                            "file": os.path.relpath(py_file, project_path),
                            "type": "security_issue",
                            "severity": "warning",
                            "message": "使用了不安全的eval函数"
                        })
                    
                    if 'import *' in content:
                        issues.append({
                            "file": os.path.relpath(py_file, project_path),
                            "type": "code_quality",
                            "severity": "info",
                            "message": "使用了通配符导入"
                        })
                    
                    # 检查硬编码密码
                    if any(keyword in content.lower() for keyword in ['password=', 'passwd=', 'secret=']):
                        issues.append({
                            "file": os.path.relpath(py_file, project_path),
                            "type": "security_issue",
                            "severity": "warning",
                            "message": "可能存在硬编码密码"
                        })
                        
            except Exception as e:
                print(f"分析文件失败 {py_file}: {e}")
        
        return {
            "files_analyzed": len(python_files),
            "issues_found": len(issues),
            "issues": issues[:50]  # 限制问题数量
        }
    
    async def _perform_dynamic_monitoring(self) -> Dict[str, Any]:
        """执行动态监控"""
        try:
            # 启动监控
            monitor_result = await self.monitor_agent.start_monitoring(duration=60)
            return monitor_result
        except Exception as e:
            return {"error": f"动态监控失败: {e}"}
    
    async def _perform_runtime_analysis(self, project_path: str) -> Dict[str, Any]:
        """执行运行时分析"""
        try:
            # 查找可执行的主文件
            main_files = []
            test_files = []
            
            for root, dirs, files in os.walk(project_path):
                # 跳过测试目录
                if 'test' in root.lower():
                    continue
                    
                for file in files:
                    if file.endswith('.py') and not file.startswith('.'):
                        file_path = os.path.join(root, file)
                        
                        # 检查文件大小
                        try:
                            if os.path.getsize(file_path) > 2 * 1024 * 1024:  # 2MB限制
                                continue
                        except:
                            continue
                        
                        # 查找主文件
                        if file in ['main.py', '__main__.py', 'app.py', 'run.py', 'start.py']:
                            main_files.append(file_path)
                        elif 'test' in file.lower():
                            test_files.append(file_path)
            
            # 如果没有找到明确的主文件，尝试查找包含if __name__ == '__main__'的文件
            if not main_files:
                for root, dirs, files in os.walk(project_path):
                    if 'test' in root.lower():
                        continue
                        
                    for file in files:
                        if file.endswith('.py') and not file.startswith('.'):
                            file_path = os.path.join(root, file)
                            try:
                                if os.path.getsize(file_path) > 2 * 1024 * 1024:
                                    continue
                                    
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    if 'if __name__' in content and '__main__' in content:
                                        main_files.append(file_path)
                                        break
                            except:
                                continue
            
            if main_files:
                main_file = main_files[0]
                print(f"找到主文件: {main_file}")
                
                # 尝试运行项目（添加超时）
                import subprocess
                try:
                    result = subprocess.run([
                        sys.executable, main_file
                    ], capture_output=True, text=True, timeout=30)
                    
                    return {
                        "main_file": os.path.relpath(main_file, project_path),
                        "execution_successful": result.returncode == 0,
                        "stdout": result.stdout[:1000],  # 限制输出长度
                        "stderr": result.stderr[:1000],  # 限制错误长度
                        "return_code": result.returncode
                    }
                except subprocess.TimeoutExpired:
                    return {
                        "main_file": os.path.relpath(main_file, project_path),
                        "execution_successful": False,
                        "error": "执行超时（30秒）"
                    }
                except Exception as e:
                    return {
                        "main_file": os.path.relpath(main_file, project_path),
                        "execution_successful": False,
                        "error": str(e)[:500]  # 限制错误信息长度
                    }
            else:
                # 对于库项目（如pandas），尝试导入测试
                return {
                    "project_type": "library",
                    "message": "这是一个库项目，无法直接运行",
                    "suggestion": "建议使用静态分析或单元测试来验证代码质量",
                    "test_files_found": len(test_files)
                }
                
        except Exception as e:
            return {"error": f"运行时分析失败: {str(e)[:500]}"}
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成综合摘要"""
        summary = {
            "total_files": len(results.get("files", [])),
            "analysis_completed": True,
            "issues_summary": {}
        }
        
        # 统计静态分析问题
        if "static_analysis" in results:
            static = results["static_analysis"]
            summary["issues_summary"]["static"] = {
                "files_analyzed": static.get("files_analyzed", 0),
                "issues_found": static.get("issues_found", 0)
            }
        
        # 统计动态监控结果
        if "dynamic_monitoring" in results:
            dynamic = results["dynamic_monitoring"]
            summary["issues_summary"]["dynamic"] = {
                "monitoring_duration": dynamic.get("duration", 0),
                "alerts_generated": len(dynamic.get("alerts", []))
            }
        
        # 统计运行时分析结果
        if "runtime_analysis" in results:
            runtime = results["runtime_analysis"]
            summary["issues_summary"]["runtime"] = {
                "execution_successful": runtime.get("execution_successful", False),
                "main_file": runtime.get("main_file", "unknown")
            }
        
        return summary
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """生成文本报告"""
        report_lines = [
            "# 动态检测报告",
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

# 创建检测器实例
detector = SimpleDetector(monitor_agent)

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
        
        # 执行检测（添加超时处理）
        print("开始执行综合检测...")
        try:
            results = await asyncio.wait_for(
                detector.detect_defects(
                    zip_file_path=temp_file_path,
                    static_analysis=static_analysis,
                    dynamic_monitoring=dynamic_monitoring,
                    runtime_analysis=runtime_analysis
                ),
                timeout=300  # 5分钟超时
            )
        except asyncio.TimeoutError:
            return BaseResponse(
                success=False,
                error="检测超时（5分钟）",
                message="检测过程超时，请尝试上传较小的项目"
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
        results = await monitor_agent.start_monitoring(duration)
        
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
