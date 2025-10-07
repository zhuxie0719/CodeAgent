#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    // 缓冲区溢出风险
    char buffer[10];
    strcpy(buffer, "This is a very long string that will cause buffer overflow");
    
    // 内存泄漏
    char* ptr = malloc(100);
    // 忘记调用free(ptr)
    
    printf("Buffer: %s\n", buffer);
    return 0;
}
