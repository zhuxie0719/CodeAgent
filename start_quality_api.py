#!/usr/bin/env python3
"""
启动代码质量分析API服务器
"""

import uvicorn
from fastapi import FastAPI
from api.code_quality_api import router as quality_router

# 创建FastAPI应用
app = FastAPI(
    title="代码质量分析API",
    description="专注于单文件代码质量分析的AI Agent服务",
    version="1.0.0"
)

# 注册路由
app.include_router(quality_router)

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "代码质量分析API服务",
        "version": "1.0.0",
        "docs": "/docs",
        "capabilities": [
            "单文件代码风格检查",
            "代码质量指标计算", 
            "AI驱动的质量评分报告生成"
        ]
    }

@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "code-quality-api",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    print("启动代码质量分析API服务器...")
    print("服务地址: http://localhost:8001")
    print("API文档: http://localhost:8001/docs")
    print("质量分析接口: http://localhost:8001/api/code-quality")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
