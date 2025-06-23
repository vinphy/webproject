#include <stdio.h>
#include <stdlib.h>
#include <mysql/mysql.h>

#define DB_HOST "localhost"
#define DB_USER "username"
#define DB_PASS "password"
#define DB_NAME "database_name"
#define DB_PORT 3306

void finish_with_error(MYSQL *con) {
    fprintf(stderr, "%s\n", mysql_error(con));
    mysql_close(con);
    exit(1);
}

int main() {
    MYSQL *con = mysql_init(NULL);
    MYSQL_RES *result;
    MYSQL_ROW row;
    int num_fields;
    int i;
    
    if (con == NULL) {
        fprintf(stderr, "mysql_init() failed\n");
        exit(1);
    }
    
    // 连接数据库
    if (mysql_real_connect(con, DB_HOST, DB_USER, DB_PASS, DB_NAME, DB_PORT, NULL, 0) == NULL) {
        finish_with_error(con);
    }
    
    // 执行SQL查询
    if (mysql_query(con, "SELECT name,age FROM person")) {
        finish_with_error(con);
    }
    
    result = mysql_store_result(con);
    if (result == NULL) {
        finish_with_error(con);
    }
    
    num_fields = mysql_num_fields(result);
    
    // 输出查询结果
    while ((row = mysql_fetch_row(result))) {
        for(i = 0; i < num_fields; i++) {
            printf("%s ", row[i] ? row[i] : "NULL");
        }
        printf("\n");
    }
    
    // 释放资源
    mysql_free_result(result);
    mysql_close(con);
    
    return 0;
}