#!/usr/bin/env python3
"""
启动代码分析API服务
"""

import uvicorn
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api.code_analysis_api import router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_app():
    """创建FastAPI应用"""
    app = FastAPI(
        title="代码分析API",
        description="提供代码分析Agent的RESTful API服务",
        version="2.0.0"
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 包含代码分析路由
    app.include_router(router)
    
    return app

def main():
    """主函数"""
    print("🚀 启动代码分析API服务...")
    print("📡 API文档地址: http://localhost:8002/docs")
    print("🔍 代码分析接口: http://localhost:8002/api/code-analysis/")
    print("💡 健康检查: http://localhost:8002/api/code-analysis/health")
    
    app = create_app()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
