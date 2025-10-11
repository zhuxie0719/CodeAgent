"""测试修复后的代码文件"""

import sys
import os
import unittest
import tempfile

# 添加修复后的代码路径
output_path = os.path.join(os.path.dirname(__file__), 'output')
sys.path.insert(0, output_path)

# 导入修复后的代码
import test_python_bad_after as fixed_code


class TestFixedBadFunction(unittest.TestCase):
    
    def test_bad_function(self):
        """测试修复后的bad_function"""
        result = fixed_code.bad_function()
        self.assertEqual(result, 3)


class TestFixedUnsafeEval(unittest.TestCase):
    
    def test_unsafe_eval_valid_input(self):
        """测试修复后的unsafe_eval - 有效输入"""
        test_cases = [
            ("1", "1"),
            ("2", "2"),
            ("(1)", "1"),
            ("True", "True")
        ]
        
        for input_expr, expected in test_cases:
            with self.subTest(input=input_expr):
                result = fixed_code.unsafe_eval(input_expr)
                self.assertEqual(result, expected)
    
    def test_unsafe_eval_invalid_input(self):
        """测试修复后的unsafe_eval - 无效输入"""
        invalid_inputs = [
            "import os",  # 包含import
            "exec('print(1)')",  # 包含exec
            "__import__('os')",  # 包含__import__
            "1 + 1; print('hack')",  # 包含分号
        ]
        
        for invalid_input in invalid_inputs:
            with self.subTest(input=invalid_input):
                with self.assertRaises(ValueError):
                    fixed_code.unsafe_eval(invalid_input)


class TestFixedProcessUserData(unittest.TestCase):
    
    def test_process_user_data(self):
        """测试修复后的process_user_data"""
        test_cases = [
            ("hello", "HELLO"),
            ("test123", "TEST123"),
            ("", ""),
        ]
        
        for input_data, expected in test_cases:
            with self.subTest(input=input_data):
                result = fixed_code.process_user_data(input_data)
                self.assertEqual(result, expected)
    
    def test_process_user_data_invalid_input(self):
        """测试修复后的process_user_data - 无效输入"""
        invalid_inputs = [5, 3.5, [1, 2], None]
        
        for invalid_input in invalid_inputs:
            with self.subTest(input=invalid_input):
                with self.assertRaises(TypeError):
                    fixed_code.process_user_data(invalid_input)


class TestFixedDivideNumbers(unittest.TestCase):
    
    def test_divide_numbers(self):
        """测试修复后的divide_numbers"""
        # 正常除法
        result = fixed_code.divide_numbers(10, 2)
        self.assertEqual(result, 5.0)
        
        # 除零错误
        with self.assertRaises(ZeroDivisionError):
            fixed_code.divide_numbers(10, 0)


class TestFixedReadFile(unittest.TestCase):
    
    def test_read_file(self):
        """测试修复后的read_file"""
        # 创建临时文件测试
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
            temp_file.write("test content")
            temp_filename = temp_file.name
        
        try:
            result = fixed_code.read_file(temp_filename)
            self.assertEqual(result, "test content")
        finally:
            os.unlink(temp_filename)
    
    def test_read_file_nonexistent(self):
        """测试文件不存在的情况"""
        with self.assertRaises(FileNotFoundError):
            fixed_code.read_file("nonexistent_file.txt")


class TestEnvironmentVariables(unittest.TestCase):
    
    def test_get_api_key(self):
        """测试API密钥获取"""
        result = fixed_code.get_api_key()
        self.assertIsInstance(result, str)
    
    def test_get_secret_password(self):
        """测试密码获取"""
        result = fixed_code.get_secret_password()
        self.assertIsInstance(result, str)


if __name__ == "__main__":
    unittest.main()
