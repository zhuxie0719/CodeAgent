# test_python_good.py - 良好的Python代码示例
"""
这是一个良好的Python代码示例
"""

from typing import List, Dict, Any
from datetime import datetime

# 常量定义
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

def calculate_sum(number_list: List[int]) -> int:
    """
    计算数字列表的总和
    
    Args:
        number_list: 数字列表
        
    Returns:
        总和
    """
    return sum(number_list)

def process_data(data: Dict[str, Any]) -> bool:
    """
    处理数据
    
    Args:
        data: 输入数据
        
    Returns:
        处理是否成功
    """
    try:
        # 数据验证
        if not data:
            return False
        
        # 处理逻辑
        result = data.get('value', 0) * 2
        return result > 0
        
    except (ValueError, TypeError) as e:
        print(f"处理数据时出错: {e}")
        return False

class DataProcessor:
    """数据处理器类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.processed_count = 0
    
    def process(self, data: List[Dict]) -> List[Dict]:
        """
        批量处理数据
        
        Args:
            data: 数据列表
            
        Returns:
            处理后的数据列表
        """
        processed_results = []
        for item in data:
            if self._validate_item(item):
                processed = self._process_item(item)
                processed_results.append(processed)
                self.processed_count += 1
        
        return processed_results
    
    def _validate_item(self, item: Dict) -> bool:
        """验证单个数据项"""
        return item is not None and isinstance(item, dict)
    
    def _process_item(self, item: Dict) -> Dict:
        """处理单个数据项"""
        return {
            'id': item.get('id'),
            'processed': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_stats(self) -> Dict[str, int]:
        """获取处理统计信息"""
        return {'processed_count': self.processed_count}

if __name__ == "__main__":
    # 测试代码
    number_list = [1, 2, 3, 4, 5]
    total = calculate_sum(number_list)
    print(f"总和: {total}")
    
    processor = DataProcessor({'timeout': DEFAULT_TIMEOUT})
    test_data = [{'id': 1, 'value': 10}, {'id': 2, 'value': 20}]
    processed_results = processor.process(test_data)
    print(f"处理结果: {processed_results}")