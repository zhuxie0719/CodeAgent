import sys
import os
import unittest
from datetime import datetime
from unittest.mock import patch

# 添加导入路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import test_python_good

class TestCalculateSum(unittest.TestCase):
    
    def test_calculate_sum_normal(self):
        """测试正常情况下的求和功能"""
        numbers = [1, 2, 3, 4, 5]
        result = test_python_good.calculate_sum(numbers)
        self.assertEqual(result, 15)
    
    def test_calculate_sum_empty_list(self):
        """测试空列表"""
        numbers = []
        result = test_python_good.calculate_sum(numbers)
        self.assertEqual(result, 0)
    
    def test_calculate_sum_single_element(self):
        """测试单个元素"""
        numbers = [10]
        result = test_python_good.calculate_sum(numbers)
        self.assertEqual(result, 10)
    
    def test_calculate_sum_negative_numbers(self):
        """测试负数"""
        numbers = [-1, -2, -3, 4, 5]
        result = test_python_good.calculate_sum(numbers)
        self.assertEqual(result, 3)

class TestProcessData(unittest.TestCase):
    
    def test_process_data_success(self):
        """测试数据处理成功的情况"""
        data = {'value': 10}
        result = test_python_good.process_data(data)
        self.assertTrue(result)
    
    def test_process_data_empty_dict(self):
        """测试空字典"""
        data = {}
        result = test_python_good.process_data(data)
        self.assertFalse(result)
    
    def test_process_data_none(self):
        """测试None输入"""
        data = None
        result = test_python_good.process_data(data)
        self.assertFalse(result)
    
    def test_process_data_zero_value(self):
        """测试值为0的情况"""
        data = {'value': 0}
        result = test_python_good.process_data(data)
        self.assertFalse(result)
    
    def test_process_data_negative_value(self):
        """测试负数值"""
        data = {'value': -5}
        result = test_python_good.process_data(data)
        self.assertFalse(result)
    
    def test_process_data_no_value_key(self):
        """测试没有value键的情况"""
        data = {'other_key': 10}
        result = test_python_good.process_data(data)
        self.assertFalse(result)

class TestDataProcessor(unittest.TestCase):
    
    def setUp(self):
        """测试前的准备工作"""
        self.config = {'timeout': 30, 'max_retries': 3}
        self.processor = test_python_good.DataProcessor(self.config)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.processor.config, self.config)
        self.assertEqual(self.processor.processed_count, 0)
    
    def test_validate_item_valid(self):
        """测试验证有效数据项"""
        item = {'id': 1, 'value': 10}
        result = self.processor._validate_item(item)
        self.assertTrue(result)
    
    def test_validate_item_none(self):
        """测试验证None数据项"""
        item = None
        result = self.processor._validate_item(item)
        self.assertFalse(result)
    
    def test_validate_item_not_dict(self):
        """测试验证非字典数据项"""
        item = [1, 2, 3]
        result = self.processor._validate_item(item)
        self.assertFalse(result)
    
    def test_process_item_valid(self):
        """测试处理单个有效数据项"""
        item = {'id': 1, 'value': 10}
        result = self.processor._process_item(item)
        
        self.assertEqual(result['id'], 1)
        self.assertTrue(result['processed'])
        self.assertIsInstance(result['timestamp'], str)
        
        # 验证时间戳格式
        try:
            datetime.fromisoformat(result['timestamp'])
        except ValueError:
            self.fail("时间戳格式不正确")
    
    def test_process_item_missing_id(self):
        """测试处理缺少id的数据项"""
        item = {'value': 10}
        result = self.processor._process_item(item)
        
        self.assertIsNone(result['id'])
        self.assertTrue(result['processed'])
        self.assertIsInstance(result['timestamp'], str)
    
    def test_process_batch_valid(self):
        """测试批量处理有效数据"""
        data = [
            {'id': 1, 'value': 10},
            {'id': 2, 'value': 20},
            {'id': 3, 'value': 30}
        ]
        
        results = self.processor.process(data)
        
        self.assertEqual(len(results), 3)
        self.assertEqual(self.processor.processed_count, 3)
        
        for i, result in enumerate(results):
            self.assertEqual(result['id'], i + 1)
            self.assertTrue(result['processed'])
            self.assertIsInstance(result['timestamp'], str)
    
    def test_process_batch_mixed(self):
        """测试批量处理混合数据（包含无效数据）"""
        data = [
            {'id': 1, 'value': 10},
            None,  # 无效数据
            {'id': 3, 'value': 30},
            "invalid",  # 无效数据
            {'id': 5, 'value': 50}
        ]
        
        results = self.processor.process(data)
        
        self.assertEqual(len(results), 3)
        self.assertEqual(self.processor.processed_count, 3)
        
        expected_ids = [1, 3, 5]
        for i, result in enumerate(results):
            self.assertEqual(result['id'], expected_ids[i])
            self.assertTrue(result['processed'])
    
    def test_process_batch_empty(self):
        """测试批量处理空列表"""
        data = []
        results = self.processor.process(data)
        
        self.assertEqual(len(results), 0)
        self.assertEqual(self.processor.processed_count, 0)
    
    def test_process_batch_all_invalid(self):
        """测试批量处理全部无效数据"""
        data = [None, "invalid", 123]
        results = self.processor.process(data)
        
        self.assertEqual(len(results), 0)
        self.assertEqual(self.processor.processed_count, 0)

class TestConstants(unittest.TestCase):
    
    def test_constants_values(self):
        """测试常量值"""
        self.assertEqual(test_python_good.MAX_RETRIES, 3)
        self.assertEqual(test_python_good.DEFAULT_TIMEOUT, 30)

if __name__ == '__main__':
    unittest.main()