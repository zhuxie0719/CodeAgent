"""
项目运行器
负责解压项目、运行项目、监控执行过程
"""

import zipfile
import subprocess
import os
import tempfile
import shutil
import time
import psutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

class ProjectRunner:
    """
    项目运行器
    简化版实现，专注于核心功能
    """
    
    def __init__(self):
        self.temp_dir = None
        self.process = None
        self.execution_logs = []
        self.execution_metrics = []
        
    def extract_project(self, zip_file_path: str) -> str:
        """
        解压项目
        
        Args:
            zip_file_path: 压缩包路径
            
        Returns:
            解压后的项目路径
        """
        try:
            # 创建临时目录
            self.temp_dir = tempfile.mkdtemp(prefix="project_")
            print(f"解压项目到: {self.temp_dir}")
            
            # 解压文件
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            print(f"项目解压完成，文件数: {len(os.listdir(self.temp_dir))}")
            return self.temp_dir
            
        except Exception as e:
            print(f"解压项目失败: {e}")
            raise
    
    def run_project(self, project_path: str) -> Dict[str, Any]:
        """
        运行项目
        
        Args:
            project_path: 项目路径
            
        Returns:
            运行结果
        """
        try:
            # 查找主文件
            main_file = self._find_main_file(project_path)
            if not main_file:
                return {"error": "未找到可执行的主文件"}
            
            print(f"找到主文件: {main_file}")
            
            # 运行项目
            self.process = subprocess.Popen(
                ["python", main_file],
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            print(f"项目启动成功，PID: {self.process.pid}")
            
            return {
                "success": True,
                "pid": self.process.pid,
                "main_file": main_file,
                "start_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"运行项目失败: {e}")
            return {"error": str(e)}
    
    def monitor_execution(self, duration: int = 60) -> Dict[str, Any]:
        """
        监控执行过程
        
        Args:
            duration: 监控持续时间（秒）
            
        Returns:
            监控结果
        """
        if not self.process:
            return {"error": "进程未启动"}
        
        print(f"开始监控执行过程，持续时间: {duration}秒")
        
        start_time = time.time()
        logs = []
        metrics = []
        errors = []
        
        while self.process.poll() is None and (time.time() - start_time) < duration:
            try:
                # 收集标准输出
                if self.process.stdout:
                    line = self.process.stdout.readline()
                    if line:
                        log_entry = {
                            "timestamp": datetime.now().isoformat(),
                            "type": "stdout",
                            "content": line.strip()
                        }
                        logs.append(log_entry)
                        print(f"STDOUT: {line.strip()}")
                
                # 收集标准错误
                if self.process.stderr:
                    line = self.process.stderr.readline()
                    if line:
                        error_entry = {
                            "timestamp": datetime.now().isoformat(),
                            "type": "stderr",
                            "content": line.strip()
                        }
                        errors.append(error_entry)
                        print(f"STDERR: {line.strip()}")
                
                # 收集进程指标
                if self.process.pid:
                    try:
                        proc = psutil.Process(self.process.pid)
                        metric = {
                            "timestamp": datetime.now().isoformat(),
                            "cpu_percent": proc.cpu_percent(),
                            "memory_percent": proc.memory_percent(),
                            "memory_info": proc.memory_info()._asdict(),
                            "status": proc.status(),
                            "num_threads": proc.num_threads()
                        }
                        metrics.append(metric)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                time.sleep(1)  # 1秒间隔
                
            except Exception as e:
                print(f"监控过程中出错: {e}")
                time.sleep(1)
        
        # 等待进程结束
        if self.process.poll() is None:
            print("监控时间到，终止进程")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        
        execution_time = time.time() - start_time
        
        return {
            "logs": logs,
            "errors": errors,
            "metrics": metrics,
            "exit_code": self.process.returncode,
            "execution_time": execution_time,
            "pid": self.process.pid
        }
    
    def _find_main_file(self, project_path: str) -> Optional[str]:
        """
        查找主文件
        
        Args:
            project_path: 项目路径
            
        Returns:
            主文件路径
        """
        # 常见的入口文件
        main_files = ["main.py", "app.py", "run.py", "index.py", "start.py"]
        
        for file in main_files:
            file_path = os.path.join(project_path, file)
            if os.path.exists(file_path):
                print(f"找到入口文件: {file}")
                return file_path
        
        # 查找包含if __name__ == "__main__"的文件
        print("搜索包含主函数的文件...")
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if 'if __name__ == "__main__"' in content:
                                print(f"找到主函数文件: {file_path}")
                                return file_path
                    except Exception as e:
                        print(f"读取文件失败 {file_path}: {e}")
                        continue
        
        # 如果没找到，返回第一个Python文件
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    print(f"使用第一个Python文件: {file_path}")
                    return file_path
        
        return None
    
    def analyze_execution_results(self, execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析执行结果
        
        Args:
            execution_results: 执行结果
            
        Returns:
            分析结果
        """
        analysis = {
            "success": True,
            "issues": [],
            "performance": {},
            "recommendations": []
        }
        
        try:
            # 检查退出码
            exit_code = execution_results.get("exit_code")
            if exit_code != 0:
                analysis["success"] = False
                analysis["issues"].append({
                    "type": "execution_error",
                    "severity": "error",
                    "message": f"程序异常退出，退出码: {exit_code}"
                })
            
            # 分析错误日志
            errors = execution_results.get("errors", [])
            if errors:
                analysis["issues"].append({
                    "type": "runtime_errors",
                    "severity": "error",
                    "message": f"发现 {len(errors)} 个运行时错误",
                    "details": errors[-5:]  # 最近5个错误
                })
            
            # 分析性能指标
            metrics = execution_results.get("metrics", [])
            if metrics:
                performance = self._analyze_performance(metrics)
                analysis["performance"] = performance
                
                # 性能问题检测
                if performance.get("max_cpu_percent", 0) > 80:
                    analysis["issues"].append({
                        "type": "high_cpu_usage",
                        "severity": "warning",
                        "message": f"CPU使用率过高: {performance['max_cpu_percent']:.1f}%"
                    })
                
                if performance.get("max_memory_percent", 0) > 80:
                    analysis["issues"].append({
                        "type": "high_memory_usage",
                        "severity": "warning",
                        "message": f"内存使用率过高: {performance['max_memory_percent']:.1f}%"
                    })
            
            # 生成建议
            if not analysis["success"]:
                analysis["recommendations"].append("检查代码错误，修复程序异常")
            
            if len(errors) > 0:
                analysis["recommendations"].append("检查错误日志，修复运行时错误")
            
            if analysis["performance"].get("max_cpu_percent", 0) > 80:
                analysis["recommendations"].append("优化代码性能，降低CPU使用率")
            
            if analysis["performance"].get("max_memory_percent", 0) > 80:
                analysis["recommendations"].append("优化内存使用，避免内存泄漏")
            
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def _analyze_performance(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析性能指标"""
        if not metrics:
            return {}
        
        try:
            cpu_percentages = [m.get("cpu_percent", 0) for m in metrics]
            memory_percentages = [m.get("memory_percent", 0) for m in metrics]
            memory_infos = [m.get("memory_info", {}) for m in metrics]
            
            return {
                "avg_cpu_percent": sum(cpu_percentages) / len(cpu_percentages),
                "max_cpu_percent": max(cpu_percentages),
                "avg_memory_percent": sum(memory_percentages) / len(memory_percentages),
                "max_memory_percent": max(memory_percentages),
                "peak_memory": max([m.get("rss", 0) for m in memory_infos]),
                "avg_threads": sum([m.get("num_threads", 0) for m in metrics]) / len(metrics)
            }
            
        except Exception as e:
            print(f"性能分析失败: {e}")
            return {}
    
    def cleanup(self):
        """清理临时文件"""
        try:
            # 终止进程
            if self.process and self.process.poll() is None:
                print("终止运行中的进程")
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
            
            # 删除临时目录
            if self.temp_dir and os.path.exists(self.temp_dir):
                print(f"清理临时目录: {self.temp_dir}")
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
            
        except Exception as e:
            print(f"清理失败: {e}")
    
    def __del__(self):
        """析构函数，确保清理"""
        self.cleanup()

# 测试代码
if __name__ == "__main__":
    def test_project_runner():
        runner = ProjectRunner()
        
        # 这里需要提供一个测试用的zip文件
        # zip_file = "test_project.zip"
        # 
        # try:
        #     # 解压项目
        #     project_path = runner.extract_project(zip_file)
        #     
        #     # 运行项目
        #     run_result = runner.run_project(project_path)
        #     print(f"运行结果: {run_result}")
        #     
        #     if run_result.get("success"):
        #         # 监控执行
        #         monitor_result = runner.monitor_execution(30)
        #         print(f"监控结果: {monitor_result}")
        #         
        #         # 分析结果
        #         analysis = runner.analyze_execution_results(monitor_result)
        #         print(f"分析结果: {analysis}")
        #     
        # finally:
        #     runner.cleanup()
        
        print("项目运行器测试完成")
    
    test_project_runner()
