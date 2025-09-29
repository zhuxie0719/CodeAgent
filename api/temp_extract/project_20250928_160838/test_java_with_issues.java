public class TestJavaWithIssues {
    
    public static void main(String[] args) {
        // 空指针解引用风险
        String str = null;
        if (str == null) {
            System.out.println("String is null");
        }
        
        // 内存泄漏风险
        Object obj = new Object();
        // 忘记调用close()方法
        
        // 未处理的异常
        try {
            int result = 10 / 0;
        } catch (ArithmeticException e) {
            // 没有处理异常
        }
    }
    
    public void unusedMethod() {
        // 未使用的方法
        System.out.println("This method is never called");
    }
}
