# 简单的测试文件
import unittest

class TestSimple(unittest.TestCase):
    def test_basic(self):
        """基本测试"""
        self.assertEqual(1 + 1, 2)
    
    def test_string(self):
        """字符串测试"""
        self.assertEqual("hello", "hello")
    
    def test_boolean(self):
        """布尔值测试"""
        self.assertTrue(True)
        self.assertFalse(False)

if __name__ == '__main__':
    unittest.main()

