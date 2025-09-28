// test_java.java - Java测试文件
import java.util.*;
import java.io.*;

public class TestJava {
    // 硬编码的API密钥
    private static final String API_KEY = "sk-1234567890abcdef";
    
    public static void main(String[] args) {
        // 空指针解引用风险
        String str = null;
        System.out.println(str.length()); // 潜在的空指针异常
        
        // 资源泄漏
        FileInputStream fis = null;
        try {
            fis = new FileInputStream("test.txt");
            // 处理文件
        } catch (IOException e) {
            e.printStackTrace();
        }
        // 忘记关闭文件流
        
        // 内存泄漏风险
        List<String> list = new ArrayList<>();
        for (int i = 0; i < 1000000; i++) {
            list.add("item" + i);
        }
        // 没有清理list
    }
}