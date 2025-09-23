// test_c.c - C语言测试文件
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 硬编码的密码
#define PASSWORD "admin123"

int main() {
    // 缓冲区溢出风险
    char buffer[10];
    char input[100];
    printf("Enter input: ");
    gets(input); // 危险的函数，可能导致缓冲区溢出
    strcpy(buffer, input);
    
    // 内存泄漏
    int* ptr = malloc(sizeof(int) * 100);
    *ptr = 42;
    // 忘记释放内存
    
    // 空指针解引用
    int* null_ptr = NULL;
    *null_ptr = 42; // 段错误
    
    return 0;
}
