"""
良好的代码示例
用于对比和参考
"""

import os
import sys
import json
import hashlib
import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path


class UserManager:
    """用户管理类
    
    负责用户的增删改查操作
    """
    
    def __init__(self):
        """初始化用户管理器"""
        self.users: List[Dict[str, Any]] = []
    
    def add_user(self, user: Dict[str, Any]) -> bool:
        """添加用户
        
        Args:
            user: 用户信息字典
            
        Returns:
            bool: 添加是否成功
        """
        if not self._validate_user(user):
            return False
        
        self.users.append(user)
        return True
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[Dict[str, Any]]: 用户信息，如果不存在返回None
        """
        for user in self.users:
            if user.get('id') == user_id:
                return user
        return None
    
    def _validate_user(self, user: Dict[str, Any]) -> bool:
        """验证用户信息
        
        Args:
            user: 用户信息字典
            
        Returns:
            bool: 验证是否通过
        """
        required_fields = ['id', 'name', 'email']
        return all(field in user for field in required_fields)


def process_data(data: List[int]) -> List[int]:
    """处理数据列表
    
    Args:
        data: 输入数据列表
        
    Returns:
        List[int]: 处理后的数据列表
    """
    if not data:
        return []
    
    result = []
    for item in data:
        if item > 10:
            result.append(item * 2)
    return result


def calculate_expression(expr: str) -> float:
    """安全地计算数学表达式
    
    Args:
        expr: 数学表达式字符串
        
    Returns:
        float: 计算结果
        
    Raises:
        ValueError: 表达式无效时抛出
    """
    # 只允许数字和基本运算符
    allowed_chars = set('0123456789+-*/.() ')
    if not all(c in allowed_chars for c in expr):
        raise ValueError("表达式包含非法字符")
    
    try:
        return eval(expr)
    except Exception as e:
        raise ValueError(f"表达式计算错误: {e}")


def read_file(filename: str) -> Optional[str]:
    """安全地读取文件
    
    Args:
        filename: 文件路径
        
    Returns:
        Optional[str]: 文件内容，读取失败返回None
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"文件不存在: {filename}")
        return None
    except PermissionError:
        print(f"没有权限读取文件: {filename}")
        return None
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None


def check_age(age: int) -> str:
    """检查年龄分类
    
    Args:
        age: 年龄
        
    Returns:
        str: 年龄分类
    """
    MINOR_AGE = 18
    SENIOR_AGE = 65
    
    if age < MINOR_AGE:
        return "未成年"
    elif age < SENIOR_AGE:
        return "成年人"
    else:
        return "老年人"


def create_temp_file(content: str) -> Optional[str]:
    """创建临时文件
    
    Args:
        content: 文件内容
        
    Returns:
        Optional[str]: 临时文件路径，创建失败返回None
    """
    try:
        temp_dir = Path.cwd() / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        temp_file = temp_dir / "temp_file.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(temp_file)
    except Exception as e:
        print(f"创建临时文件失败: {e}")
        return None


def calculate_sum(numbers: List[int]) -> int:
    """计算数字列表的总和
    
    Args:
        numbers: 数字列表
        
    Returns:
        int: 总和
    """
    return sum(numbers)


def process_user_input(user_input: str) -> str:
    """处理用户输入
    
    Args:
        user_input: 用户输入字符串
        
    Returns:
        str: 处理后的字符串
        
    Raises:
        ValueError: 输入无效时抛出
    """
    if not user_input or not user_input.strip():
        raise ValueError("输入不能为空")
    
    if len(user_input) > 1000:
        raise ValueError("输入过长")
    
    return user_input.strip().upper()


def complex_logic(data: List[Dict[str, Any]]) -> List[int]:
    """处理复杂逻辑
    
    Args:
        data: 输入数据列表
        
    Returns:
        List[int]: 处理结果
    """
    result = []
    
    for item in data:
        if not isinstance(item, dict):
            continue
        
        value = item.get('value')
        if not isinstance(value, (int, float)):
            continue
        
        if 0 < value < 100 and value % 2 == 0:
            result.append(int(value))
    
    return result


def generate_secure_token() -> str:
    """生成安全的令牌
    
    Returns:
        str: 安全令牌
    """
    import secrets
    return secrets.token_hex(16)


def process_large_data(size: int) -> int:
    """处理大量数据
    
    Args:
        size: 数据大小
        
    Returns:
        int: 处理结果
    """
    # 使用生成器避免内存问题
    data = (i * 2 for i in range(size))
    return sum(1 for _ in data)


def main():
    """主函数"""
    # 测试用户管理器
    user_manager = UserManager()
    
    user = {
        'id': '1',
        'name': '张三',
        'email': 'zhangsan@example.com'
    }
    
    if user_manager.add_user(user):
        print("用户添加成功")
    
    retrieved_user = user_manager.get_user('1')
    if retrieved_user:
        print(f"找到用户: {retrieved_user['name']}")
    
    # 测试数据处理
    data = [1, 2, 3, 4, 5, 15, 20]
    result = process_data(data)
    print(f"处理结果: {result}")
    
    # 测试安全计算
    try:
        result = calculate_expression("2 + 2 * 3")
        print(f"计算结果: {result}")
    except ValueError as e:
        print(f"计算错误: {e}")


if __name__ == "__main__":
    main()
