"""
性能监控模块
"""

import os
import psutil
import time
from typing import Dict, List, Any, Optional


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def collect_metrics(self, project_path: str) -> Dict[str, Any]:
        """收集性能指标"""
        try:
            # 系统资源使用情况
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 进程信息
            process = psutil.Process()
            process_cpu = process.cpu_percent()
            process_memory = process.memory_info()
            
            return {
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent
                },
                'process': {
                    'cpu_percent': process_cpu,
                    'memory_rss': process_memory.rss,
                    'memory_vms': process_memory.vms
                },
                'timestamp': time.time()
            }
        except Exception as e:
            return {'error': str(e)}


class BottleneckAnalyzer:
    """瓶颈分析器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def analyze(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析性能瓶颈"""
        bottlenecks = []
        
        # 分析CPU瓶颈
        if metrics.get('system', {}).get('cpu_percent', 0) > 80:
            bottlenecks.append({
                'type': 'cpu',
                'severity': 'high',
                'message': 'CPU使用率过高',
                'value': metrics['system']['cpu_percent']
            })
        
        # 分析内存瓶颈
        if metrics.get('system', {}).get('memory_percent', 0) > 80:
            bottlenecks.append({
                'type': 'memory',
                'severity': 'high',
                'message': '内存使用率过高',
                'value': metrics['system']['memory_percent']
            })
        
        # 分析磁盘瓶颈
        if metrics.get('system', {}).get('disk_percent', 0) > 90:
            bottlenecks.append({
                'type': 'disk',
                'severity': 'critical',
                'message': '磁盘空间不足',
                'value': metrics['system']['disk_percent']
            })
        
        return bottlenecks


class ResourceOptimizer:
    """资源优化器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def optimize(self, project_path: str, bottlenecks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """执行优化"""
        optimizations = []
        
        for bottleneck in bottlenecks:
            if bottleneck['type'] == 'cpu':
                optimizations.append(await self._optimize_cpu(project_path))
            elif bottleneck['type'] == 'memory':
                optimizations.append(await self._optimize_memory(project_path))
            elif bottleneck['type'] == 'disk':
                optimizations.append(await self._optimize_disk(project_path))
        
        return optimizations
    
    async def _optimize_cpu(self, project_path: str) -> Dict[str, Any]:
        """优化CPU使用"""
        return {
            'type': 'cpu_optimization',
            'message': 'CPU优化建议已生成',
            'actions': ['启用多进程', '优化算法复杂度']
        }
    
    async def _optimize_memory(self, project_path: str) -> Dict[str, Any]:
        """优化内存使用"""
        return {
            'type': 'memory_optimization',
            'message': '内存优化建议已生成',
            'actions': ['启用内存缓存', '优化数据结构']
        }
    
    async def _optimize_disk(self, project_path: str) -> Dict[str, Any]:
        """优化磁盘使用"""
        return {
            'type': 'disk_optimization',
            'message': '磁盘优化建议已生成',
            'actions': ['清理临时文件', '压缩日志文件']
        }
