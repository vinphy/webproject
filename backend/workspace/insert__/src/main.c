#include <stdio.h>

// 输入端口
double 输入1;
double 输入2;

// 输出端口
double 输出1;
double 输出2;

// 属性


int main() {
    // 读取输入
    printf("请输入 输入1: ");
    scanf("%lf", &输入1);
    printf("请输入 输入2: ");
    scanf("%lf", &输入2);
    
    // 执行加法运算
    输出1 = 输入1 + 输入2;
    
    // 输出结果
    printf("计算结果: %lf\n", 输出1);
    
    return 0;
}