"""
简化版动态监控Agent
专注于核心功能，确保3周内能完成
"""

import asyncio
import psutil
import time
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

class SimpleMonitorAgent:
    """
    简化版动态监控Agent
    只实现核心功能：系统监控、简单告警、数据存储
    """
    
    def __init__(self):
        self.monitoring = False
        self.metrics = []
        self.alerts = []
        self.alert_thresholds = {
            "cpu_threshold": 80,
            "memory_threshold": 85,
            "disk_threshold": 90
        }
        
    async def start_monitoring(self, duration: int = 300) -> Dict[str, Any]:
        """
        启动监控
        
        Args:
            duration: 监控持续时间（秒）
            
        Returns:
            监控结果
        """
        self.monitoring = True
        start_time = time.time()
        
        print(f"开始监控，持续时间: {duration}秒")
        
        while self.monitoring and (time.time() - start_time) < duration:
            try:
                # 收集指标
                metrics = self._collect_metrics()
                self.metrics.append(metrics)
                
                # 检查告警
                alerts = self._check_alerts(metrics)
                if alerts:
                    self.alerts.extend(alerts)
                    print(f"发现告警: {len(alerts)}个")
                
                # 等待下一个监控周期
                await asyncio.sleep(5)  # 5秒间隔
                
            except Exception as e:
                print(f"监控过程中出错: {e}")
                await asyncio.sleep(5)
        
        self.monitoring = False
        
        return {
            "metrics": self.metrics,
            "alerts": self.alerts,
            "duration": duration,
            "total_metrics": len(self.metrics),
            "total_alerts": len(self.alerts)
        }
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        try:
            # CPU指标
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存指标
            memory = psutil.virtual_memory()
            
            # 磁盘指标
            disk = psutil.disk_usage('/')
            
            # 网络指标（简化）
            try:
                net_io = psutil.net_io_counters()
                network_data = {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv
                }
            except:
                network_data = {"bytes_sent": 0, "bytes_recv": 0}
            
            return {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used": memory.used,
                "memory_available": memory.available,
                "disk_percent": disk.percent,
                "disk_used": disk.used,
                "disk_free": disk.free,
                "network": network_data
            }
            
        except Exception as e:
            print(f"收集指标失败: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查告警条件"""
        alerts = []
        
        try:
            # CPU使用率告警
            if metrics.get("cpu_percent", 0) > self.alert_thresholds["cpu_threshold"]:
                alerts.append({
                    "type": "cpu_high",
                    "severity": "warning",
                    "message": f"CPU使用率过高: {metrics['cpu_percent']:.1f}%",
                    "threshold": self.alert_thresholds["cpu_threshold"],
                    "current_value": metrics["cpu_percent"],
                    "timestamp": metrics["timestamp"]
                })
            
            # 内存使用率告警
            if metrics.get("memory_percent", 0) > self.alert_thresholds["memory_threshold"]:
                alerts.append({
                    "type": "memory_high",
                    "severity": "warning",
                    "message": f"内存使用率过高: {metrics['memory_percent']:.1f}%",
                    "threshold": self.alert_thresholds["memory_threshold"],
                    "current_value": metrics["memory_percent"],
                    "timestamp": metrics["timestamp"]
                })
            
            # 磁盘使用率告警
            if metrics.get("disk_percent", 0) > self.alert_thresholds["disk_threshold"]:
                alerts.append({
                    "type": "disk_high",
                    "severity": "warning",
                    "message": f"磁盘使用率过高: {metrics['disk_percent']:.1f}%",
                    "threshold": self.alert_thresholds["disk_threshold"],
                    "current_value": metrics["disk_percent"],
                    "timestamp": metrics["timestamp"]
                })
                
        except Exception as e:
            print(f"检查告警失败: {e}")
        
        return alerts
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        print("监控已停止")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """获取监控状态"""
        return {
            "monitoring": self.monitoring,
            "total_metrics": len(self.metrics),
            "total_alerts": len(self.alerts),
            "alert_thresholds": self.alert_thresholds,
            "recent_alerts": self.alerts[-5:] if self.alerts else []
        }
    
    def update_alert_thresholds(self, new_thresholds: Dict[str, Any]):
        """更新告警阈值"""
        self.alert_thresholds.update(new_thresholds)
        print(f"告警阈值已更新: {new_thresholds}")
    
    def save_results(self, file_path: str):
        """保存监控结果到文件"""
        try:
            results = {
                "metrics": self.metrics,
                "alerts": self.alerts,
                "summary": self._generate_summary(),
                "timestamp": datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"监控结果已保存到: {file_path}")
            
        except Exception as e:
            print(f"保存结果失败: {e}")
    
    def _generate_summary(self) -> Dict[str, Any]:
        """生成监控摘要"""
        if not self.metrics:
            return {"error": "没有监控数据"}
        
        try:
            # 计算平均值
            cpu_values = [m.get("cpu_percent", 0) for m in self.metrics if "cpu_percent" in m]
            memory_values = [m.get("memory_percent", 0) for m in self.metrics if "memory_percent" in m]
            disk_values = [m.get("disk_percent", 0) for m in self.metrics if "disk_percent" in m]
            
            summary = {
                "monitoring_duration": len(self.metrics) * 5,  # 假设5秒间隔
                "total_metrics": len(self.metrics),
                "total_alerts": len(self.alerts),
                "average_cpu": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                "max_cpu": max(cpu_values) if cpu_values else 0,
                "average_memory": sum(memory_values) / len(memory_values) if memory_values else 0,
                "max_memory": max(memory_values) if memory_values else 0,
                "average_disk": sum(disk_values) / len(disk_values) if disk_values else 0,
                "max_disk": max(disk_values) if disk_values else 0
            }
            
            # 按类型统计告警
            alert_by_type = {}
            for alert in self.alerts:
                alert_type = alert.get("type", "unknown")
                alert_by_type[alert_type] = alert_by_type.get(alert_type, 0) + 1
            
            summary["alerts_by_type"] = alert_by_type
            
            return summary
            
        except Exception as e:
            return {"error": f"生成摘要失败: {e}"}
    
    def clear_data(self):
        """清空监控数据"""
        self.metrics.clear()
        self.alerts.clear()
        print("监控数据已清空")

# 测试代码
if __name__ == "__main__":
    async def test_monitor():
        monitor = SimpleMonitorAgent()
        
        print("开始测试监控功能...")
        
        # 启动监控
        results = await monitor.start_monitoring(30)  # 监控30秒
        
        print(f"监控完成:")
        print(f"- 收集指标: {results['total_metrics']}个")
        print(f"- 发现告警: {results['total_alerts']}个")
        
        # 保存结果
        monitor.save_results("monitor_results.json")
        
        # 显示摘要
        summary = monitor._generate_summary()
        print(f"监控摘要: {summary}")
    
    # 运行测试
    asyncio.run(test_monitor())
