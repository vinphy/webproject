#include <stdio.h>

// 输入端口
double 数据输入;

// 输出端口
double 分析结果;

// 属性


int main() {
    // 读取输入
    printf("请输入 数据输入: ");
    scanf("%lf", &数据输入);
    
    // 执行加法运算
    分析结果 = 数据输入;
    
    // 输出结果
    printf("计算结果: %lf\n", 分析结果);
    
    return 0;
}