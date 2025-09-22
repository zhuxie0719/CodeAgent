"""
数据库初始化脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import settings
from sqlalchemy import create_engine, text


async def init_database():
    """初始化数据库"""
    try:
        # 创建数据库引擎
        engine = create_engine(settings.DATABASE_URL)
        
        # 创建数据库表
        with engine.connect() as conn:
            # 创建任务表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id VARCHAR(36) PRIMARY KEY,
                    type VARCHAR(50) NOT NULL,
                    data JSONB,
                    status VARCHAR(20) NOT NULL DEFAULT 'pending',
                    assigned_agent VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    result JSONB,
                    error TEXT
                )
            """))
            
            # 创建AGENT状态表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS agent_status (
                    agent_id VARCHAR(50) PRIMARY KEY,
                    status VARCHAR(20) NOT NULL,
                    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    config JSONB
                )
            """))
            
            # 创建项目分析结果表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS project_analysis (
                    id SERIAL PRIMARY KEY,
                    project_path VARCHAR(500) NOT NULL,
                    analysis_result JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 创建修复历史表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS fix_history (
                    id SERIAL PRIMARY KEY,
                    task_id VARCHAR(36) NOT NULL,
                    issue_type VARCHAR(50) NOT NULL,
                    fix_result JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.commit()
            print("数据库表创建成功")
    
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        return False
    
    return True


if __name__ == "__main__":
    asyncio.run(init_database())
