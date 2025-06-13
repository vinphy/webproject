#include <stdio.h>

// 输入端口
double 信号输入;

// 输出端口
double 监控输出;

// 属性


int main() {
    // 读取输入
    printf("请输入 信号输入: ");
    scanf("%lf", &信号输入);
    
    // 执行加法运算
    监控输出 = 信号输入;
    
    // 输出结果
    printf("计算结果: %lf\n", 监控输出);
    
    return 0;
}