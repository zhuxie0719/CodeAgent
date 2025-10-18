#!/usr/bin/env python3
"""
Flask 2.0.0 完整测试流程
1. 创建测试项目
2. 运行检测系统
3. 对比分析结果
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import json

class FlaskTestRunner:
    """Flask测试运行器"""
    
    def __init__(self):
        self.project_dir = Path("flask_test_project")
        self.reports_dir = Path("api/reports")
        
    def create_test_project(self):
        """创建测试项目"""
        print("🔧 创建Flask 2.0.0测试项目...")
        
        # 运行快速测试脚本
        result = subprocess.run([sys.executable, "flask_quick_test.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 测试项目创建成功")
            return True
        else:
            print(f"❌ 测试项目创建失败: {result.stderr}")
            return False
    
    def start_detection_system(self):
        """启动检测系统"""
        print("🚀 启动检测系统...")
        
        # 检查start_api.py是否存在
        if not Path("start_api.py").exists():
            print("❌ 未找到start_api.py，请确保在正确的目录中运行")
            return False
        
        # 启动API服务（后台运行）
        print("📡 启动API服务...")
        self.api_process = subprocess.Popen([sys.executable, "start_api.py"],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
        
        # 等待服务启动
        print("⏳ 等待服务启动...")
        time.sleep(5)
        
        return True
    
    def run_detection(self):
        """运行检测"""
        print("🔍 运行检测系统...")
        
        # 检查测试项目是否存在
        if not self.project_dir.exists():
            print("❌ 测试项目不存在，请先创建")
            return False
        
        # 这里需要根据你的检测系统API来调用
        # 假设有一个API端点可以上传项目并运行检测
        print("📤 上传测试项目到检测系统...")
        print("💡 请手动打开 frontend/index.html 并上传 flask_test_project 目录")
        print("💡 或者使用API调用检测系统")
        
        return True
    
    def wait_for_detection_complete(self):
        """等待检测完成"""
        print("⏳ 等待检测完成...")
        print("💡 请等待检测系统完成分析")
        
        # 检查报告目录
        if not self.reports_dir.exists():
            print("❌ 报告目录不存在")
            return False
        
        # 等待报告生成
        max_wait = 300  # 最多等待5分钟
        wait_time = 0
        
        while wait_time < max_wait:
            json_files = list(self.reports_dir.glob("*.json"))
            if json_files:
                print("✅ 检测报告已生成")
                return True
            
            time.sleep(10)
            wait_time += 10
            print(f"⏳ 等待中... ({wait_time}s)")
        
        print("❌ 检测超时")
        return False
    
    def run_comparison(self):
        """运行对比分析"""
        print("📊 运行对比分析...")
        
        # 检查对比脚本是否存在
        if not Path("compare_flask_bugs.py").exists():
            print("❌ 未找到compare_flask_bugs.py")
            return False
        
        # 运行对比脚本
        result = subprocess.run([sys.executable, "compare_flask_bugs.py"],
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 对比分析完成")
            print("\n" + "="*70)
            print("📊 对比分析结果:")
            print("="*70)
            print(result.stdout)
            return True
        else:
            print(f"❌ 对比分析失败: {result.stderr}")
            return False
    
    def cleanup(self):
        """清理资源"""
        print("🧹 清理资源...")
        
        # 停止API服务
        if hasattr(self, 'api_process'):
            self.api_process.terminate()
            print("✅ API服务已停止")
    
    def run_full_test(self):
        """运行完整测试流程"""
        print("🎯 开始Flask 2.0.0完整测试流程")
        print("="*70)
        
        try:
            # 1. 创建测试项目
            if not self.create_test_project():
                return False
            
            # 2. 启动检测系统
            if not self.start_detection_system():
                return False
            
            # 3. 运行检测
            if not self.run_detection():
                return False
            
            # 4. 等待检测完成
            if not self.wait_for_detection_complete():
                return False
            
            # 5. 运行对比分析
            if not self.run_comparison():
                return False
            
            print("\n🎉 完整测试流程完成！")
            print("📊 请查看对比分析结果")
            
            return True
            
        except KeyboardInterrupt:
            print("\n⏹️ 测试被用户中断")
            return False
        except Exception as e:
            print(f"\n❌ 测试过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.cleanup()

def main():
    """主函数"""
    print("🚀 Flask 2.0.0 测试流程启动器")
    print("="*70)
    
    runner = FlaskTestRunner()
    
    # 检查必要文件
    required_files = ["start_api.py", "compare_flask_bugs.py", "flask_quick_test.py"]
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"❌ 缺少必要文件: {missing_files}")
        print("💡 请确保在正确的项目目录中运行")
        return
    
    print("✅ 所有必要文件检查通过")
    
    # 运行完整测试
    success = runner.run_full_test()
    
    if success:
        print("\n🎉 测试完成！")
        print("📊 请查看对比分析结果")
    else:
        print("\n❌ 测试失败")
        print("💡 请检查错误信息并重试")

if __name__ == "__main__":
    main()




