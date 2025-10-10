# 简化版动态缺陷检测方案（3周实现）

## 项目背景
- 开发时间：3周
- 开发人员：1人
- 目标：用户上传项目压缩包，实现缺陷动态检测

## 核心功能（必须实现）

### 1. 基础动态监控（第1周）
- 系统资源监控：CPU、内存、磁盘
- 简单告警机制：阈值告警
- 基础API接口

### 2. 项目运行监控（第2周）
- 解压项目并运行
- 监控运行状态
- 检测运行时错误

### 3. 缺陷检测集成（第3周）
- 结合静态检测结果
- 生成综合报告
- 前端展示

## 技术栈选择（简化）

### 后端
- Python + FastAPI（现有）
- psutil（系统监控）
- asyncio（异步处理）

### 前端
- 现有HTML界面（不重新开发）
- 简单JavaScript增强

### 存储
- 文件存储（不使用数据库）
- JSON格式数据

## 详细实施计划

### 第1周：基础监控系统

#### 目标
实现基础的系统资源监控和告警

#### 具体任务
1. **创建简化监控Agent**（2天）
   ```python
   # agents/simple_monitor_agent.py
   class SimpleMonitorAgent:
       def monitor_system(self):
           # 监控CPU、内存、磁盘
           pass
       
       def check_alerts(self, metrics):
           # 简单阈值告警
           pass
   ```

2. **创建监控API**（2天）
   ```python
   # api/simple_monitor_api.py
   @app.post("/monitor/start")
   async def start_monitoring():
       # 启动监控
       pass
   
   @app.get("/monitor/status")
   async def get_status():
       # 获取监控状态
       pass
   ```

3. **集成到现有系统**（1天）
   - 修改现有API
   - 添加监控端点

#### 交付物
- 基础监控功能
- 简单告警机制
- API接口

### 第2周：项目运行监控

#### 目标
实现项目解压、运行和监控

#### 具体任务
1. **项目解压和运行**（3天）
   ```python
   # utils/project_runner.py
   class ProjectRunner:
       def extract_project(self, zip_file):
           # 解压项目
           pass
       
       def run_project(self, project_path):
           # 运行项目
           pass
       
       def monitor_execution(self, process):
           # 监控执行过程
           pass
   ```

2. **运行时错误检测**（2天）
   ```python
   # agents/runtime_error_detector.py
   class RuntimeErrorDetector:
       def detect_errors(self, logs):
           # 检测运行时错误
           pass
       
       def analyze_performance(self, metrics):
           # 分析性能问题
           pass
   ```

#### 交付物
- 项目运行功能
- 运行时监控
- 错误检测

### 第3周：集成和优化

#### 目标
集成静态和动态检测，完善用户体验

#### 具体任务
1. **检测结果集成**（2天）
   ```python
   # agents/integrated_detector.py
   class IntegratedDetector:
       def combine_results(self, static_results, dynamic_results):
           # 合并检测结果
           pass
       
       def generate_report(self, results):
           # 生成综合报告
           pass
   ```

2. **前端界面优化**（2天）
   - 添加监控状态显示
   - 显示动态检测结果
   - 优化用户体验

3. **测试和优化**（1天）
   - 功能测试
   - 性能优化
   - 文档整理

#### 交付物
- 完整的检测系统
- 用户界面
- 使用文档

## 核心代码实现

### 1. 简化监控Agent

```python
# agents/simple_monitor_agent.py
import asyncio
import psutil
import time
from datetime import datetime
from typing import Dict, Any, List

class SimpleMonitorAgent:
    def __init__(self):
        self.monitoring = False
        self.metrics = []
        self.alerts = []
        
    async def start_monitoring(self, duration: int = 300):
        """启动监控"""
        self.monitoring = True
        start_time = time.time()
        
        while self.monitoring and (time.time() - start_time) < duration:
            # 收集指标
            metrics = self._collect_metrics()
            self.metrics.append(metrics)
            
            # 检查告警
            alerts = self._check_alerts(metrics)
            if alerts:
                self.alerts.extend(alerts)
            
            await asyncio.sleep(5)  # 5秒间隔
        
        return {
            "metrics": self.metrics,
            "alerts": self.alerts,
            "duration": duration
        }
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    
    def _check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查告警"""
        alerts = []
        
        if metrics["cpu_percent"] > 80:
            alerts.append({
                "type": "cpu_high",
                "message": f"CPU使用率过高: {metrics['cpu_percent']}%",
                "timestamp": metrics["timestamp"]
            })
        
        if metrics["memory_percent"] > 85:
            alerts.append({
                "type": "memory_high", 
                "message": f"内存使用率过高: {metrics['memory_percent']}%",
                "timestamp": metrics["timestamp"]
            })
        
        return alerts
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
```

### 2. 项目运行器

```python
# utils/project_runner.py
import zipfile
import subprocess
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

class ProjectRunner:
    def __init__(self):
        self.temp_dir = None
        self.process = None
        
    def extract_project(self, zip_file_path: str) -> str:
        """解压项目"""
        self.temp_dir = tempfile.mkdtemp()
        
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
        
        return self.temp_dir
    
    def run_project(self, project_path: str) -> Dict[str, Any]:
        """运行项目"""
        try:
            # 查找主文件
            main_file = self._find_main_file(project_path)
            if not main_file:
                return {"error": "未找到主文件"}
            
            # 运行项目
            self.process = subprocess.Popen(
                ["python", main_file],
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            return {
                "success": True,
                "pid": self.process.pid,
                "main_file": main_file
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def monitor_execution(self, duration: int = 60) -> Dict[str, Any]:
        """监控执行过程"""
        if not self.process:
            return {"error": "进程未启动"}
        
        start_time = time.time()
        logs = []
        metrics = []
        
        while self.process.poll() is None and (time.time() - start_time) < duration:
            # 收集日志
            if self.process.stdout:
                line = self.process.stdout.readline()
                if line:
                    logs.append(line.strip())
            
            # 收集指标
            if self.process.pid:
                try:
                    proc = psutil.Process(self.process.pid)
                    metrics.append({
                        "timestamp": datetime.now().isoformat(),
                        "cpu_percent": proc.cpu_percent(),
                        "memory_percent": proc.memory_percent(),
                        "status": proc.status()
                    })
                except:
                    pass
            
            time.sleep(1)
        
        return {
            "logs": logs,
            "metrics": metrics,
            "exit_code": self.process.returncode,
            "duration": time.time() - start_time
        }
    
    def _find_main_file(self, project_path: str) -> Optional[str]:
        """查找主文件"""
        # 常见的入口文件
        main_files = ["main.py", "app.py", "run.py", "index.py"]
        
        for file in main_files:
            file_path = os.path.join(project_path, file)
            if os.path.exists(file_path):
                return file_path
        
        # 查找包含if __name__ == "__main__"的文件
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if 'if __name__ == "__main__"' in content:
                                return file_path
                    except:
                        continue
        
        return None
    
    def cleanup(self):
        """清理临时文件"""
        if self.process:
            self.process.terminate()
        
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
```

### 3. 集成检测器

```python
# agents/integrated_detector.py
from typing import Dict, Any, List
from agents.simple_monitor_agent import SimpleMonitorAgent
from utils.project_runner import ProjectRunner

class IntegratedDetector:
    def __init__(self):
        self.monitor_agent = SimpleMonitorAgent()
        self.project_runner = ProjectRunner()
    
    async def detect_defects(self, zip_file_path: str) -> Dict[str, Any]:
        """综合缺陷检测"""
        results = {
            "static_results": {},
            "dynamic_results": {},
            "runtime_results": {},
            "summary": {}
        }
        
        try:
            # 1. 解压项目
            project_path = self.project_runner.extract_project(zip_file_path)
            
            # 2. 运行项目
            run_result = self.project_runner.run_project(project_path)
            if "error" in run_result:
                results["runtime_results"] = run_result
                return results
            
            # 3. 监控运行
            monitor_result = self.project_runner.monitor_execution(60)
            results["runtime_results"] = monitor_result
            
            # 4. 系统监控
            system_monitor = await self.monitor_agent.start_monitoring(60)
            results["dynamic_results"] = system_monitor
            
            # 5. 生成摘要
            results["summary"] = self._generate_summary(results)
            
        except Exception as e:
            results["error"] = str(e)
        
        finally:
            # 清理
            self.project_runner.cleanup()
        
        return results
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成检测摘要"""
        summary = {
            "total_issues": 0,
            "critical_issues": 0,
            "warnings": 0,
            "recommendations": []
        }
        
        # 统计运行时问题
        runtime_results = results.get("runtime_results", {})
        if runtime_results.get("exit_code") != 0:
            summary["critical_issues"] += 1
            summary["recommendations"].append("项目运行失败，请检查代码错误")
        
        # 统计系统问题
        dynamic_results = results.get("dynamic_results", {})
        alerts = dynamic_results.get("alerts", [])
        summary["warnings"] = len(alerts)
        
        if alerts:
            summary["recommendations"].append("系统资源使用率较高，建议优化性能")
        
        summary["total_issues"] = summary["critical_issues"] + summary["warnings"]
        
        return summary
```

### 4. 简化API

```python
# api/simple_dynamic_api.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from agents.integrated_detector import IntegratedDetector
import tempfile
import os

app = FastAPI()

@app.post("/api/dynamic-detect")
async def dynamic_detect(file: UploadFile = File(...)):
    """动态缺陷检测"""
    try:
        # 保存上传文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # 执行检测
        detector = IntegratedDetector()
        results = await detector.detect_defects(tmp_file_path)
        
        # 清理临时文件
        os.unlink(tmp_file_path)
        
        return {
            "success": True,
            "results": results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/monitor/status")
async def get_monitor_status():
    """获取监控状态"""
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }
```

## 前端集成（最小改动）

### 修改现有上传页面

```javascript
// 在现有index.html中添加
async function uploadForDynamicDetection() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('请选择文件');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/dynamic-detect', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayDynamicResults(result.results);
        } else {
            alert('检测失败: ' + result.error);
        }
    } catch (error) {
        alert('上传失败: ' + error.message);
    }
}

function displayDynamicResults(results) {
    const resultsDiv = document.getElementById('results');
    
    let html = '<h3>动态检测结果</h3>';
    
    // 显示摘要
    const summary = results.summary;
    html += `<div class="summary">
        <p>总问题数: ${summary.total_issues}</p>
        <p>严重问题: ${summary.critical_issues}</p>
        <p>警告: ${summary.warnings}</p>
    </div>`;
    
    // 显示建议
    if (summary.recommendations.length > 0) {
        html += '<h4>建议</h4><ul>';
        summary.recommendations.forEach(rec => {
            html += `<li>${rec}</li>`;
        });
        html += '</ul>';
    }
    
    // 显示运行时结果
    const runtime = results.runtime_results;
    if (runtime.logs) {
        html += '<h4>运行日志</h4>';
        html += '<pre>' + runtime.logs.join('\n') + '</pre>';
    }
    
    resultsDiv.innerHTML = html;
}
```

## 部署和测试

### 1. 安装依赖
```bash
pip install psutil
```

### 2. 启动服务
```bash
python api/simple_dynamic_api.py
```

### 3. 测试流程
1. 上传项目压缩包
2. 系统自动解压和运行
3. 监控运行状态
4. 生成检测报告

## 风险控制

### 1. 时间风险
- 优先实现核心功能
- 简化非必要特性
- 预留测试时间

### 2. 技术风险
- 使用成熟技术栈
- 避免复杂架构
- 充分测试

### 3. 安全风险
- 限制运行时间
- 隔离运行环境
- 清理临时文件

## 成功标准

### 功能标准
- [ ] 用户能上传项目压缩包
- [ ] 系统能解压和运行项目
- [ ] 能监控运行状态
- [ ] 能生成检测报告

### 性能标准
- [ ] 检测时间 < 5分钟
- [ ] 系统资源消耗 < 50%
- [ ] 支持并发用户数 > 5

### 质量标准
- [ ] 基本功能稳定
- [ ] 错误处理完善
- [ ] 用户体验良好

## 总结

这个简化方案专注于核心功能，确保3周内能完成：

1. **第1周**：基础监控系统
2. **第2周**：项目运行监控  
3. **第3周**：集成和优化

通过简化架构和功能，降低开发复杂度，确保项目能按时交付。
