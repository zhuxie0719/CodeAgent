"""
动态监控Agent
负责实时监控系统运行状态，检测动态缺陷和异常
"""

import asyncio
import psutil
import time
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import sys

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from ..base_agent import BaseAgent, TaskStatus

class DynamicMonitorAgent(BaseAgent):
    """
    动态监控Agent
    负责实时监控系统运行状态，检测动态缺陷和异常
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("dynamic_monitor_agent", config)
        
        # 监控配置
        self.monitor_interval = config.get("monitor_interval", 5)  # 监控间隔(秒)
        self.alert_thresholds = config.get("alert_thresholds", {
            "cpu_threshold": 80,
            "memory_threshold": 85,
            "disk_threshold": 90,
            "network_threshold": 80
        })
        
        # 监控状态
        self.monitoring = False
        self.metrics_buffer = []
        self.alert_history = []
        
        # 初始化日志
        self.logger = logging.getLogger(__name__)
        
    def get_capabilities(self) -> List[str]:
        """获取Agent能力列表"""
        return [
            "system_monitoring",
            "performance_monitoring", 
            "resource_monitoring",
            "anomaly_detection",
            "alert_management"
        ]
    
    async def process_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理动态监控任务"""
        try:
            self.logger.info(f"开始处理动态监控任务: {task_id}")
            
            # 获取任务参数
            monitor_type = task_data.get("monitor_type", "comprehensive")
            duration = task_data.get("duration", 300)  # 默认5分钟
            target_systems = task_data.get("target_systems", ["system", "performance"])
            
            # 开始监控
            self.monitoring = True
            start_time = time.time()
            metrics = []
            alerts = []
            
            while self.monitoring and (time.time() - start_time) < duration:
                # 收集监控指标
                if monitor_type == "comprehensive":
                    metric = await self._collect_comprehensive_metrics(target_systems)
                elif monitor_type == "system":
                    metric = await self._collect_system_metrics()
                elif monitor_type == "performance":
                    metric = await self._collect_performance_metrics()
                else:
                    metric = await self._collect_default_metrics()
                
                metrics.append(metric)
                
                # 检查告警条件
                task_alerts = await self._check_alerts(metric)
                if task_alerts:
                    alerts.extend(task_alerts)
                    await self._send_alerts(task_alerts)
                
                # 等待下一个监控周期
                await asyncio.sleep(self.monitor_interval)
            
            # 生成监控报告
            report = await self._generate_monitoring_report(metrics, alerts, duration)
            
            self.logger.info(f"动态监控任务完成: {task_id}")
            
            return {
                "task_id": task_id,
                "monitor_type": monitor_type,
                "duration": duration,
                "metrics_count": len(metrics),
                "alerts_count": len(alerts),
                "report": report,
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"动态监控任务失败: {task_id}, 错误: {e}")
            return {
                "task_id": task_id,
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _collect_comprehensive_metrics(self, target_systems: List[str]) -> Dict[str, Any]:
        """收集综合监控指标"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "system": {},
            "performance": {},
            "network": {},
            "processes": {}
        }
        
        for system in target_systems:
            if system == "system":
                metrics["system"] = await self._collect_system_metrics()
            elif system == "performance":
                metrics["performance"] = await self._collect_performance_metrics()
            elif system == "network":
                metrics["network"] = await self._collect_network_metrics()
            elif system == "processes":
                metrics["processes"] = await self._collect_process_metrics()
        
        return metrics
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        try:
            # CPU指标
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # 内存指标
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # 磁盘指标
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "frequency": cpu_freq.current if cpu_freq else 0,
                    "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free
                },
                "swap": {
                    "total": swap.total,
                    "used": swap.used,
                    "free": swap.free,
                    "percent": swap.percent
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                },
                "disk_io": {
                    "read_count": disk_io.read_count if disk_io else 0,
                    "write_count": disk_io.write_count if disk_io else 0,
                    "read_bytes": disk_io.read_bytes if disk_io else 0,
                    "write_bytes": disk_io.write_bytes if disk_io else 0
                }
            }
        except Exception as e:
            self.logger.error(f"收集系统指标失败: {e}")
            return {"error": str(e)}
    
    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """收集性能指标"""
        try:
            # 这里可以集成具体的性能监控工具
            # 目前返回模拟数据
            return {
                "response_time": 0,  # 需要根据具体应用实现
                "throughput": 0,     # 需要根据具体应用实现
                "error_rate": 0,     # 需要根据具体应用实现
                "active_connections": 0,  # 需要根据具体应用实现
                "queue_length": 0,   # 需要根据具体应用实现
                "cache_hit_rate": 0  # 需要根据具体应用实现
            }
        except Exception as e:
            self.logger.error(f"收集性能指标失败: {e}")
            return {"error": str(e)}
    
    async def _collect_network_metrics(self) -> Dict[str, Any]:
        """收集网络指标"""
        try:
            net_io = psutil.net_io_counters()
            net_connections = psutil.net_connections()
            
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errin": net_io.errin,
                "errout": net_io.errout,
                "dropin": net_io.dropin,
                "dropout": net_io.dropout,
                "active_connections": len(net_connections)
            }
        except Exception as e:
            self.logger.error(f"收集网络指标失败: {e}")
            return {"error": str(e)}
    
    async def _collect_process_metrics(self) -> Dict[str, Any]:
        """收集进程指标"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                "total_processes": len(processes),
                "top_cpu_processes": sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:5],
                "top_memory_processes": sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:5]
            }
        except Exception as e:
            self.logger.error(f"收集进程指标失败: {e}")
            return {"error": str(e)}
    
    async def _collect_default_metrics(self) -> Dict[str, Any]:
        """收集默认指标"""
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "monitoring",
            "uptime": time.time()
        }
    
    async def _check_alerts(self, metric: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查告警条件"""
        alerts = []
        
        try:
            # 检查系统指标告警
            if "system" in metric:
                system_metrics = metric["system"]
                
                # CPU使用率告警
                if "cpu" in system_metrics:
                    cpu_percent = system_metrics["cpu"].get("percent", 0)
                    if cpu_percent > self.alert_thresholds["cpu_threshold"]:
                        alerts.append({
                            "type": "cpu_high",
                            "severity": "warning",
                            "message": f"CPU使用率过高: {cpu_percent}%",
                            "threshold": self.alert_thresholds["cpu_threshold"],
                            "current_value": cpu_percent,
                            "timestamp": metric["timestamp"]
                        })
                
                # 内存使用率告警
                if "memory" in system_metrics:
                    memory_percent = system_metrics["memory"].get("percent", 0)
                    if memory_percent > self.alert_thresholds["memory_threshold"]:
                        alerts.append({
                            "type": "memory_high",
                            "severity": "warning",
                            "message": f"内存使用率过高: {memory_percent}%",
                            "threshold": self.alert_thresholds["memory_threshold"],
                            "current_value": memory_percent,
                            "timestamp": metric["timestamp"]
                        })
                
                # 磁盘使用率告警
                if "disk" in system_metrics:
                    disk_percent = system_metrics["disk"].get("percent", 0)
                    if disk_percent > self.alert_thresholds["disk_threshold"]:
                        alerts.append({
                            "type": "disk_high",
                            "severity": "warning",
                            "message": f"磁盘使用率过高: {disk_percent}%",
                            "threshold": self.alert_thresholds["disk_threshold"],
                            "current_value": disk_percent,
                            "timestamp": metric["timestamp"]
                        })
            
            # 检查性能指标告警
            if "performance" in metric:
                perf_metrics = metric["performance"]
                
                # 响应时间告警
                response_time = perf_metrics.get("response_time", 0)
                if response_time > 1000:  # 1秒阈值
                    alerts.append({
                        "type": "response_time_high",
                        "severity": "warning",
                        "message": f"响应时间过长: {response_time}ms",
                        "threshold": 1000,
                        "current_value": response_time,
                        "timestamp": metric["timestamp"]
                    })
                
                # 错误率告警
                error_rate = perf_metrics.get("error_rate", 0)
                if error_rate > 5:  # 5%阈值
                    alerts.append({
                        "type": "error_rate_high",
                        "severity": "error",
                        "message": f"错误率过高: {error_rate}%",
                        "threshold": 5,
                        "current_value": error_rate,
                        "timestamp": metric["timestamp"]
                    })
            
        except Exception as e:
            self.logger.error(f"检查告警条件失败: {e}")
        
        return alerts
    
    async def _send_alerts(self, alerts: List[Dict[str, Any]]):
        """发送告警"""
        for alert in alerts:
            try:
                # 记录告警历史
                self.alert_history.append(alert)
                
                # 这里可以集成具体的告警通知方式
                # 1. WebSocket实时通知
                await self._send_websocket_alert(alert)
                
                # 2. 邮件通知
                if alert["severity"] in ["error", "critical"]:
                    await self._send_email_alert(alert)
                
                # 3. 短信通知
                if alert["severity"] == "critical":
                    await self._send_sms_alert(alert)
                
                self.logger.info(f"告警发送成功: {alert['type']}")
                
            except Exception as e:
                self.logger.error(f"发送告警失败: {e}")
    
    async def _send_websocket_alert(self, alert: Dict[str, Any]):
        """发送WebSocket告警"""
        # 这里需要集成WebSocket服务
        # 目前只是记录日志
        self.logger.info(f"WebSocket告警: {alert['message']}")
    
    async def _send_email_alert(self, alert: Dict[str, Any]):
        """发送邮件告警"""
        # 这里需要集成邮件服务
        # 目前只是记录日志
        self.logger.info(f"邮件告警: {alert['message']}")
    
    async def _send_sms_alert(self, alert: Dict[str, Any]):
        """发送短信告警"""
        # 这里需要集成短信服务
        # 目前只是记录日志
        self.logger.info(f"短信告警: {alert['message']}")
    
    async def _generate_monitoring_report(self, metrics: List[Dict[str, Any]], 
                                        alerts: List[Dict[str, Any]], 
                                        duration: int) -> Dict[str, Any]:
        """生成监控报告"""
        try:
            # 统计指标
            total_metrics = len(metrics)
            total_alerts = len(alerts)
            
            # 按严重程度分类告警
            alert_by_severity = {}
            for alert in alerts:
                severity = alert["severity"]
                if severity not in alert_by_severity:
                    alert_by_severity[severity] = 0
                alert_by_severity[severity] += 1
            
            # 按类型分类告警
            alert_by_type = {}
            for alert in alerts:
                alert_type = alert["type"]
                if alert_type not in alert_by_type:
                    alert_by_type[alert_type] = 0
                alert_by_type[alert_type] += 1
            
            # 计算平均值
            avg_metrics = {}
            if metrics:
                # CPU平均值
                cpu_values = [m.get("system", {}).get("cpu", {}).get("percent", 0) for m in metrics if "system" in m]
                if cpu_values:
                    avg_metrics["avg_cpu"] = sum(cpu_values) / len(cpu_values)
                    avg_metrics["max_cpu"] = max(cpu_values)
                
                # 内存平均值
                memory_values = [m.get("system", {}).get("memory", {}).get("percent", 0) for m in metrics if "system" in m]
                if memory_values:
                    avg_metrics["avg_memory"] = sum(memory_values) / len(memory_values)
                    avg_metrics["max_memory"] = max(memory_values)
                
                # 磁盘平均值
                disk_values = [m.get("system", {}).get("disk", {}).get("percent", 0) for m in metrics if "system" in m]
                if disk_values:
                    avg_metrics["avg_disk"] = sum(disk_values) / len(disk_values)
                    avg_metrics["max_disk"] = max(disk_values)
            
            # 生成摘要
            summary = {
                "monitoring_duration": duration,
                "total_metrics": total_metrics,
                "total_alerts": total_alerts,
                "alert_by_severity": alert_by_severity,
                "alert_by_type": alert_by_type,
                "average_metrics": avg_metrics,
                "monitoring_status": "completed"
            }
            
            # 生成建议
            recommendations = []
            if total_alerts > 0:
                recommendations.append("发现系统异常，建议检查相关指标")
            if avg_metrics.get("avg_cpu", 0) > 70:
                recommendations.append("CPU使用率较高，建议优化性能")
            if avg_metrics.get("avg_memory", 0) > 80:
                recommendations.append("内存使用率较高，建议增加内存或优化内存使用")
            if avg_metrics.get("avg_disk", 0) > 85:
                recommendations.append("磁盘使用率较高，建议清理磁盘空间")
            
            return {
                "summary": summary,
                "recommendations": recommendations,
                "detailed_metrics": metrics[-10:],  # 最近10个指标
                "recent_alerts": alerts[-5:]  # 最近5个告警
            }
            
        except Exception as e:
            self.logger.error(f"生成监控报告失败: {e}")
            return {"error": str(e)}
    
    async def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        self.logger.info("动态监控已停止")
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """获取监控状态"""
        return {
            "monitoring": self.monitoring,
            "monitor_interval": self.monitor_interval,
            "alert_thresholds": self.alert_thresholds,
            "total_alerts": len(self.alert_history),
            "recent_alerts": self.alert_history[-5:] if self.alert_history else []
        }
    
    async def update_alert_thresholds(self, new_thresholds: Dict[str, Any]):
        """更新告警阈值"""
        self.alert_thresholds.update(new_thresholds)
        self.logger.info(f"告警阈值已更新: {new_thresholds}")
    
    async def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取告警历史"""
        return self.alert_history[-limit:] if self.alert_history else []
