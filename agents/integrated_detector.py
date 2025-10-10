"""
集成检测器
结合静态检测和动态监控，生成综合检测报告
"""

import asyncio
import json
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# 导入现有组件
from agents.simple_monitor_agent import SimpleMonitorAgent
from utils.project_runner import ProjectRunner

class IntegratedDetector:
    """
    集成检测器
    结合静态检测和动态监控，提供完整的缺陷检测方案
    """
    
    def __init__(self):
        self.monitor_agent = SimpleMonitorAgent()
        self.project_runner = ProjectRunner()
        
    async def detect_defects(self, zip_file_path: str, 
                           static_analysis: bool = True,
                           dynamic_monitoring: bool = True,
                           runtime_analysis: bool = True) -> Dict[str, Any]:
        """
        综合缺陷检测
        
        Args:
            zip_file_path: 项目压缩包路径
            static_analysis: 是否进行静态分析
            dynamic_monitoring: 是否进行动态监控
            runtime_analysis: 是否进行运行时分析
            
        Returns:
            综合检测结果
        """
        results = {
            "static_results": {},
            "dynamic_results": {},
            "runtime_results": {},
            "summary": {},
            "timestamp": datetime.now().isoformat(),
            "project_info": {}
        }
        
        try:
            print("开始综合缺陷检测...")
            
            # 1. 解压项目
            print("解压项目...")
            project_path = self.project_runner.extract_project(zip_file_path)
            results["project_info"]["project_path"] = project_path
            results["project_info"]["files"] = self._list_project_files(project_path)
            
            # 2. 静态分析（如果启用）
            if static_analysis:
                print("进行静态分析...")
                results["static_results"] = await self._perform_static_analysis(project_path)
            
            # 3. 运行时分析（如果启用）
            if runtime_analysis:
                print("进行运行时分析...")
                runtime_result = await self._perform_runtime_analysis(project_path)
                results["runtime_results"] = runtime_result
            
            # 4. 动态监控（如果启用）
            if dynamic_monitoring:
                print("进行动态监控...")
                dynamic_result = await self._perform_dynamic_monitoring()
                results["dynamic_results"] = dynamic_result
            
            # 5. 生成综合摘要
            print("生成综合摘要...")
            results["summary"] = self._generate_comprehensive_summary(results)
            
            print("综合缺陷检测完成")
            
        except Exception as e:
            print(f"检测过程中出错: {e}")
            results["error"] = str(e)
            results["success"] = False
        
        finally:
            # 清理临时文件
            self.project_runner.cleanup()
        
        return results
    
    def _list_project_files(self, project_path: str) -> List[str]:
        """列出项目文件"""
        files = []
        try:
            for root, dirs, filenames in os.walk(project_path):
                for filename in filenames:
                    file_path = os.path.relpath(os.path.join(root, filename), project_path)
                    files.append(file_path)
        except Exception as e:
            print(f"列出文件失败: {e}")
        return files
    
    async def _perform_static_analysis(self, project_path: str) -> Dict[str, Any]:
        """执行静态分析"""
        try:
            # 这里可以集成现有的静态分析功能
            # 目前返回模拟结果
            static_results = {
                "analysis_type": "static",
                "files_analyzed": 0,
                "issues_found": 0,
                "issues": [],
                "summary": "静态分析完成"
            }
            
            # 简单的静态分析
            python_files = []
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
            
            static_results["files_analyzed"] = len(python_files)
            
            # 简单的代码检查
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # 检查常见问题
                        if 'eval(' in content:
                            static_results["issues"].append({
                                "file": os.path.relpath(py_file, project_path),
                                "type": "security_issue",
                                "severity": "warning",
                                "message": "使用了不安全的eval函数",
                                "line": content.find('eval(') + 1
                            })
                        
                        if 'import *' in content:
                            static_results["issues"].append({
                                "file": os.path.relpath(py_file, project_path),
                                "type": "code_quality",
                                "severity": "info",
                                "message": "使用了通配符导入",
                                "line": content.find('import *') + 1
                            })
                        
                        if len(content.split('\n')) > 500:
                            static_results["issues"].append({
                                "file": os.path.relpath(py_file, project_path),
                                "type": "code_quality",
                                "severity": "info",
                                "message": "文件过长，建议拆分",
                                "line": 1
                            })
                            
                except Exception as e:
                    print(f"分析文件失败 {py_file}: {e}")
            
            static_results["issues_found"] = len(static_results["issues"])
            return static_results
            
        except Exception as e:
            return {"error": f"静态分析失败: {e}"}
    
    async def _perform_runtime_analysis(self, project_path: str) -> Dict[str, Any]:
        """执行运行时分析"""
        try:
            # 运行项目
            run_result = self.project_runner.run_project(project_path)
            if "error" in run_result:
                return {
                    "success": False,
                    "error": run_result["error"],
                    "analysis": {
                        "issues": [{
                            "type": "execution_error",
                            "severity": "error",
                            "message": f"项目无法运行: {run_result['error']}"
                        }]
                    }
                }
            
            # 监控执行
            monitor_result = self.project_runner.monitor_execution(60)  # 监控60秒
            
            # 分析执行结果
            analysis = self.project_runner.analyze_execution_results(monitor_result)
            
            return {
                "success": True,
                "run_result": run_result,
                "monitor_result": monitor_result,
                "analysis": analysis
            }
            
        except Exception as e:
            return {"error": f"运行时分析失败: {e}"}
    
    async def _perform_dynamic_monitoring(self) -> Dict[str, Any]:
        """执行动态监控"""
        try:
            # 启动系统监控
            monitor_result = await self.monitor_agent.start_monitoring(60)  # 监控60秒
            
            return {
                "monitoring_type": "system",
                "result": monitor_result
            }
            
        except Exception as e:
            return {"error": f"动态监控失败: {e}"}
    
    def _generate_comprehensive_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成综合摘要"""
        summary = {
            "total_issues": 0,
            "critical_issues": 0,
            "warning_issues": 0,
            "info_issues": 0,
            "issues_by_type": {},
            "recommendations": [],
            "overall_status": "good"
        }
        
        try:
            # 统计静态分析问题
            static_results = results.get("static_results", {})
            static_issues = static_results.get("issues", [])
            
            for issue in static_issues:
                severity = issue.get("severity", "info")
                issue_type = issue.get("type", "unknown")
                
                summary["total_issues"] += 1
                
                if severity == "error":
                    summary["critical_issues"] += 1
                elif severity == "warning":
                    summary["warning_issues"] += 1
                else:
                    summary["info_issues"] += 1
                
                summary["issues_by_type"][issue_type] = summary["issues_by_type"].get(issue_type, 0) + 1
            
            # 统计运行时问题
            runtime_results = results.get("runtime_results", {})
            if runtime_results.get("success") == False:
                summary["total_issues"] += 1
                summary["critical_issues"] += 1
                summary["issues_by_type"]["execution_error"] = summary["issues_by_type"].get("execution_error", 0) + 1
            
            runtime_analysis = runtime_results.get("analysis", {})
            runtime_issues = runtime_analysis.get("issues", [])
            
            for issue in runtime_issues:
                severity = issue.get("severity", "info")
                issue_type = issue.get("type", "unknown")
                
                summary["total_issues"] += 1
                
                if severity == "error":
                    summary["critical_issues"] += 1
                elif severity == "warning":
                    summary["warning_issues"] += 1
                else:
                    summary["info_issues"] += 1
                
                summary["issues_by_type"][issue_type] = summary["issues_by_type"].get(issue_type, 0) + 1
            
            # 统计动态监控问题
            dynamic_results = results.get("dynamic_results", {})
            dynamic_monitor_result = dynamic_results.get("result", {})
            dynamic_alerts = dynamic_monitor_result.get("alerts", [])
            
            for alert in dynamic_alerts:
                severity = alert.get("severity", "info")
                alert_type = alert.get("type", "unknown")
                
                summary["total_issues"] += 1
                
                if severity == "error":
                    summary["critical_issues"] += 1
                elif severity == "warning":
                    summary["warning_issues"] += 1
                else:
                    summary["info_issues"] += 1
                
                summary["issues_by_type"][alert_type] = summary["issues_by_type"].get(alert_type, 0) + 1
            
            # 生成建议
            if summary["critical_issues"] > 0:
                summary["recommendations"].append("发现严重问题，建议立即修复")
                summary["overall_status"] = "critical"
            elif summary["warning_issues"] > 0:
                summary["recommendations"].append("发现警告问题，建议尽快修复")
                summary["overall_status"] = "warning"
            elif summary["info_issues"] > 0:
                summary["recommendations"].append("发现信息问题，建议优化代码")
                summary["overall_status"] = "info"
            else:
                summary["recommendations"].append("未发现明显问题，代码质量良好")
                summary["overall_status"] = "good"
            
            # 具体建议
            if "security_issue" in summary["issues_by_type"]:
                summary["recommendations"].append("发现安全问题，建议加强安全防护")
            
            if "execution_error" in summary["issues_by_type"]:
                summary["recommendations"].append("项目无法正常运行，请检查代码错误")
            
            if "high_cpu_usage" in summary["issues_by_type"]:
                summary["recommendations"].append("CPU使用率过高，建议优化性能")
            
            if "high_memory_usage" in summary["issues_by_type"]:
                summary["recommendations"].append("内存使用率过高，建议优化内存使用")
            
        except Exception as e:
            summary["error"] = f"生成摘要失败: {e}"
        
        return summary
    
    def save_results(self, results: Dict[str, Any], file_path: str):
        """保存检测结果"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"检测结果已保存到: {file_path}")
        except Exception as e:
            print(f"保存结果失败: {e}")
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """生成文本报告"""
        try:
            summary = results.get("summary", {})
            project_info = results.get("project_info", {})
            
            report = f"""
# 代码缺陷检测报告

## 项目信息
- 检测时间: {results.get('timestamp', 'N/A')}
- 项目文件数: {len(project_info.get('files', []))}

## 检测摘要
- 总问题数: {summary.get('total_issues', 0)}
- 严重问题: {summary.get('critical_issues', 0)}
- 警告问题: {summary.get('warning_issues', 0)}
- 信息问题: {summary.get('info_issues', 0)}
- 整体状态: {summary.get('overall_status', 'unknown')}

## 问题分类
"""
            
            for issue_type, count in summary.get("issues_by_type", {}).items():
                report += f"- {issue_type}: {count}个\n"
            
            report += "\n## 修复建议\n"
            for recommendation in summary.get("recommendations", []):
                report += f"- {recommendation}\n"
            
            # 详细问题列表
            static_issues = results.get("static_results", {}).get("issues", [])
            if static_issues:
                report += "\n## 静态分析问题\n"
                for issue in static_issues:
                    report += f"- {issue.get('file', 'N/A')}: {issue.get('message', 'N/A')}\n"
            
            runtime_analysis = results.get("runtime_results", {}).get("analysis", {})
            runtime_issues = runtime_analysis.get("issues", [])
            if runtime_issues:
                report += "\n## 运行时问题\n"
                for issue in runtime_issues:
                    report += f"- {issue.get('type', 'N/A')}: {issue.get('message', 'N/A')}\n"
            
            return report
            
        except Exception as e:
            return f"生成报告失败: {e}"

# 测试代码
if __name__ == "__main__":
    async def test_integrated_detector():
        detector = IntegratedDetector()
        
        # 这里需要提供一个测试用的zip文件
        # zip_file = "test_project.zip"
        # 
        # try:
        #     results = await detector.detect_defects(zip_file)
        #     print("检测结果:")
        #     print(json.dumps(results, indent=2, ensure_ascii=False))
        #     
        #     # 生成报告
        #     report = detector.generate_report(results)
        #     print("\n检测报告:")
        #     print(report)
        #     
        #     # 保存结果
        #     detector.save_results(results, "detection_results.json")
        #     
        # except Exception as e:
        #     print(f"测试失败: {e}")
        
        print("集成检测器测试完成")
    
    asyncio.run(test_integrated_detector())
