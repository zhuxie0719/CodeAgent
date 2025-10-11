import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import test_python_bad

class TestPythonBad(unittest.TestCase):
    """测试test_python_bad模块中的函数"""
    
    def test_bad_function(self):
        """测试bad_function函数"""
        result = test_python_bad.bad_function(5)
        self.assertEqual(result, 10)
        
        result = test_python_bad.bad_function(0)
        self.assertEqual(result, 0)
        
        result = test_python_bad.bad_function(-3)
        self.assertEqual(result, -6)
    
    def test_divide_numbers(self):
        """测试divide_numbers函数"""
        result = test_python_bad.divide_numbers(10, 2)
        self.assertEqual(result, 5.0)
        
        result = test_python_bad.divide_numbers(15, 3)
        self.assertEqual(result, 5.0)
        
        # 测试除零异常
        with self.assertRaises(ZeroDivisionError):
            test_python_bad.divide_numbers(10, 0)
    
    def test_use_global(self):
        """测试use_global函数"""
        result = test_python_bad.use_global()
        self.assertEqual(result, "I'm global")
    
    def test_format_string(self):
        """测试format_string函数"""
        result = test_python_bad.format_string("Hello {}", "World")
        self.assertEqual(result, "Hello World")
        
        result = test_python_bad.format_string("Number: {}", 42)
        self.assertEqual(result, "Number: 42")
    
    def test_convert_to_int(self):
        """测试convert_to_int函数"""
        result = test_python_bad.convert_to_int("123")
        self.assertEqual(result, 123)
        
        result = test_python_bad.convert_to_int("0")
        self.assertEqual(result, 0)
        
        # 测试无效输入
        with self.assertRaises(ValueError):
            test_python_bad.convert_to_int("abc")
    
    def test_create_large_list(self):
        """测试create_large_list函数"""
        result = test_python_bad.create_large_list(5)
        self.assertEqual(result, [0, 1, 2, 3, 4])
        
        result = test_python_bad.create_large_list(0)
        self.assertEqual(result, [])
        
        result = test_python_bad.create_large_list(1)
        self.assertEqual(result, [0])

if __name__ == '__main__':
    unittest.main()


