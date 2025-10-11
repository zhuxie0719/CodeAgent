import os
import sys


def get_api_key():
    """从环境变量获取API密钥"""
    return os.getenv("API_KEY", "")


def get_secret_password():
    """从环境变量获取密码"""
    return os.getenv("SECRET_PASSWORD", "")


def bad_function():
    """示例函数，返回两个数的和
    
    Returns:
        int: 两个数的和
    """
    x = 1
    y = 2
    z = x + y
    return z


def safe_eval(expression):
    """安全地执行表达式
    
    Args:
        expression (str): 要执行的表达式
        
    Returns:
        str: 执行结果或错误信息
    """
    if not isinstance(expression, str):
        raise ValueError("表达式必须是字符串")
    
    allowed_chars = set("0123456789+-*/(). ")
    if not all(char in allowed_chars for char in expression):
        raise ValueError("表达式包含不安全字符")
    
    try:
        return str(eval(expression))
    except Exception as e:
        return f"计算错误: {e}"


def process_user_data(data):
    """处理用户数据，转换为大写
    
    Args:
        data (str): 输入的用户数据
        
    Returns:
        str: 处理后的数据
        
    Raises:
        TypeError: 如果输入不是字符串
        ValueError: 如果输入为空
    """
    if not isinstance(data, str):
        raise TypeError("输入数据必须是字符串")
    if not data.strip():
        raise ValueError("输入数据不能为空")
    
    processed = data.upper()
    return processed


def divide_numbers(a, b):
    """两个数相除
    
    Args:
        a (float): 被除数
        b (float): 除数
        
    Returns:
        float: 除法结果
        
    Raises:
        TypeError: 如果输入不是数字
        ZeroDivisionError: 如果除数为零
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("输入必须是数字")
    if b == 0:
        raise ZeroDivisionError("除数不能为零")
    
    result = a / b
    return result


class GlobalState:
    """全局状态管理类"""
    _state = "global"
    
    @classmethod
    def get_state(cls):
        """获取全局状态"""
        return cls._state
    
    @classmethod
    def set_state(cls, value):
        """设置全局状态"""
        if not isinstance(value, str):
            raise TypeError("状态值必须是字符串")
        cls._state = value


def use_global():
    """使用全局状态
    
    Returns:
        str: 修改后的全局状态
    """
    GlobalState.set_state("modified")
    return GlobalState.get_state()


def read_file(filename):
    """安全读取文件内容
    
    Args:
        filename (str): 文件名
        
    Returns:
        str: 文件内容
        
    Raises:
        TypeError: 如果文件名不是字符串
        FileNotFoundError: 如果文件不存在
        PermissionError: 如果没有读取权限
        IOError: 其他IO错误
    """
    if not isinstance(filename, str):
        raise TypeError("文件名必须是字符串")
    if not filename.strip():
        raise ValueError("文件名不能为空")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"文件不存在: {filename}")
    except PermissionError:
        raise PermissionError(f"没有读取权限: {filename}")
    except IOError as e:
        raise IOError(f"读取文件错误: {e}")


def create_large_list(size=1000000):
    """创建大型列表
    
    Args:
        size (int): 列表大小，默认1000000
        
    Returns:
        list: 包含指定数量元素的列表
        
    Raises:
        TypeError: 如果大小不是整数
        ValueError: 如果大小小于等于0
    """
    if not isinstance(size, int):
        raise TypeError("大小必须是整数")
    if size <= 0:
        raise ValueError("大小必须大于0")
    
    big_list = []
    for i in range(size):
        big_list.append(f"item_{i}")
    return big_list


def format_string(user_input):
    """安全格式化字符串
    
    Args:
        user_input (str): 用户输入
        
    Returns:
        str: 格式化的查询字符串
        
    Raises:
        TypeError: 如果输入不是字符串
    """
    if not isinstance(user_input, str):
        raise TypeError("用户输入必须是字符串")
    
    safe_input = user_input.replace("'", "''")
    query = f"SELECT * FROM users WHERE name = '{safe_input}'"
    return query


def risky_operation():
    """安全的数据访问操作
    
    Returns:
        str: 键对应的值或默认值
    """
    data = {"key": "value"}
    return data.get("nonexistent_key", "default_value")


def unreachable_code():
    """示例函数，演示可达代码"""
    return "reached"


class BadClass:
    """示例类"""
    
    def __init__(self):
        """初始化方法"""
        self.value = None
    
    def method_without_docstring(self):
        """获取值的方法
        
        Returns:
            any: 存储的值
        """
        return self.value


if __name__ == "__main__":
    try:
        result = divide_numbers(10, 2)
        print(result)
    except (ZeroDivisionError, TypeError) as e:
        print(f"错误: {e}")