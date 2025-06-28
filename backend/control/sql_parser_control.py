from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import re
import json
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

class SqlParseRequest(BaseModel):
    sql: str

class Column(BaseModel):
    name: str
    type: str
    nullable: bool = True
    default: Optional[str] = None
    comment: Optional[str] = None

class ForeignKey(BaseModel):
    column: str
    referencedTable: str
    referencedColumn: str

class Table(BaseModel):
    name: str
    columns: List[Column]
    primaryKey: Optional[List[str]] = None
    foreignKeys: Optional[List[ForeignKey]] = None

class SqlParseResponse(BaseModel):
    success: bool
    message: str
    tables: List[Table]

class SqlParser:
    def __init__(self):
        self.tables = []
        self.current_table = None
        
    def parse_sql(self, sql: str) -> List[Table]:
        """解析SQL语句，提取表结构信息"""
        self.tables = []
        self.current_table = None
        
        # 清理SQL语句
        sql = self._clean_sql(sql)
        
        # 分割多个SQL语句
        statements = self._split_statements(sql)
        
        for statement in statements:
            statement = statement.strip()
            if not statement:
                continue
                
            # 解析CREATE TABLE语句
            if self._is_create_table(statement):
                self._parse_create_table(statement)
            # 解析ALTER TABLE语句
            elif self._is_alter_table(statement):
                self._parse_alter_table(statement)
        
        return self.tables
    
    def _clean_sql(self, sql: str) -> str:
        """清理SQL语句"""
        # 移除注释
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        
        # 标准化换行符和空格
        sql = re.sub(r'\s+', ' ', sql)
        sql = sql.replace(';', ';\n')
        
        return sql
    
    def _split_statements(self, sql: str) -> List[str]:
        """分割多个SQL语句"""
        statements = []
        current_statement = ""
        paren_count = 0
        
        for char in sql:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            elif char == ';' and paren_count == 0:
                current_statement += char
                statements.append(current_statement.strip())
                current_statement = ""
                continue
            
            current_statement += char
        
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        return statements
    
    def _is_create_table(self, statement: str) -> bool:
        """判断是否为CREATE TABLE语句"""
        return re.match(r'CREATE\s+TABLE\s+', statement, re.IGNORECASE) is not None
    
    def _is_alter_table(self, statement: str) -> bool:
        """判断是否为ALTER TABLE语句"""
        return re.match(r'ALTER\s+TABLE\s+', statement, re.IGNORECASE) is not None
    
    def _parse_create_table(self, statement: str):
        """解析CREATE TABLE语句"""
        # 提取表名
        table_match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:`?(\w+)`?\.)?`?(\w+)`?', statement, re.IGNORECASE)
        if not table_match:
            return
        
        table_name = table_match.group(2)
        
        # 提取列定义部分
        columns_match = re.search(r'\((.*)\)', statement, re.DOTALL | re.IGNORECASE)
        if not columns_match:
            return
        
        columns_text = columns_match.group(1)
        
        # 创建表对象
        table = Table(
            name=table_name,
            columns=[],
            primaryKey=None,
            foreignKeys=[]
        )
        
        # 解析列定义
        self._parse_columns(columns_text, table)
        
        # 解析主键和外键约束
        self._parse_constraints(columns_text, table)
        
        self.tables.append(table)
    
    def _parse_columns(self, columns_text: str, table: Table):
        """解析列定义"""
        # 分割列定义
        column_definitions = self._split_column_definitions(columns_text)
        
        for col_def in column_definitions:
            col_def = col_def.strip()
            if not col_def or col_def.startswith(('PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'INDEX', 'KEY')):
                continue
            
            column = self._parse_column_definition(col_def)
            if column:
                table.columns.append(column)
    
    def _split_column_definitions(self, columns_text: str) -> List[str]:
        """分割列定义"""
        definitions = []
        current_def = ""
        paren_count = 0
        
        for char in columns_text:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            elif char == ',' and paren_count == 0:
                definitions.append(current_def.strip())
                current_def = ""
                continue
            
            current_def += char
        
        if current_def.strip():
            definitions.append(current_def.strip())
        
        return definitions
    
    def _parse_column_definition(self, col_def: str) -> Optional[Column]:
        """解析单个列定义"""
        # 提取列名
        name_match = re.match(r'`?(\w+)`?', col_def)
        if not name_match:
            return None
        
        column_name = name_match.group(1)
        
        # 提取数据类型
        type_match = re.search(r'`?\w+`?\s+([A-Za-z]+(?:\s*\(\s*\d+(?:\s*,\s*\d+)?\s*\))?)', col_def)
        if not type_match:
            return None
        
        column_type = type_match.group(1).upper()
        
        # 检查是否允许空值
        nullable = 'NOT NULL' not in col_def.upper()
        
        # 提取默认值
        default_match = re.search(r'DEFAULT\s+([^,\s]+)', col_def, re.IGNORECASE)
        default_value = default_match.group(1) if default_match else None
        
        # 提取注释
        comment_match = re.search(r"COMMENT\s+'([^']*)'", col_def, re.IGNORECASE)
        comment = comment_match.group(1) if comment_match else None
        
        return Column(
            name=column_name,
            type=column_type,
            nullable=nullable,
            default=default_value,
            comment=comment
        )
    
    def _parse_constraints(self, columns_text: str, table: Table):
        """解析约束定义"""
        # 解析主键
        pk_match = re.search(r'PRIMARY\s+KEY\s*\(\s*([^)]+)\s*\)', columns_text, re.IGNORECASE)
        if pk_match:
            pk_columns = [col.strip().strip('`') for col in pk_match.group(1).split(',')]
            table.primaryKey = pk_columns
        
        # 解析外键
        fk_matches = re.finditer(r'FOREIGN\s+KEY\s*\(\s*`?(\w+)`?\s*\)\s+REFERENCES\s+`?(\w+)`?\s*\(\s*`?(\w+)`?\s*\)', columns_text, re.IGNORECASE)
        for fk_match in fk_matches:
            fk = ForeignKey(
                column=fk_match.group(1),
                referencedTable=fk_match.group(2),
                referencedColumn=fk_match.group(3)
            )
            table.foreignKeys.append(fk)
    
    def _parse_alter_table(self, statement: str):
        """解析ALTER TABLE语句"""
        # 提取表名
        table_match = re.search(r'ALTER\s+TABLE\s+`?(\w+)`?', statement, re.IGNORECASE)
        if not table_match:
            return
        
        table_name = table_match.group(1)
        
        # 查找对应的表
        table = next((t for t in self.tables if t.name == table_name), None)
        if not table:
            return
        
        # 解析ADD COLUMN
        add_column_matches = re.finditer(r'ADD\s+COLUMN\s+`?(\w+)`?\s+([A-Za-z]+(?:\s*\(\s*\d+(?:\s*,\s*\d+)?\s*\))?)', statement, re.IGNORECASE)
        for match in add_column_matches:
            column_name = match.group(1)
            column_type = match.group(2).upper()
            
            # 检查是否已存在
            if not any(col.name == column_name for col in table.columns):
                column = Column(
                    name=column_name,
                    type=column_type,
                    nullable=True
                )
                table.columns.append(column)
        
        # 解析ADD PRIMARY KEY
        pk_match = re.search(r'ADD\s+PRIMARY\s+KEY\s*\(\s*([^)]+)\s*\)', statement, re.IGNORECASE)
        if pk_match:
            pk_columns = [col.strip().strip('`') for col in pk_match.group(1).split(',')]
            table.primaryKey = pk_columns
        
        # 解析ADD FOREIGN KEY
        fk_matches = re.finditer(r'ADD\s+FOREIGN\s+KEY\s*\(\s*`?(\w+)`?\s*\)\s+REFERENCES\s+`?(\w+)`?\s*\(\s*`?(\w+)`?\s*\)', statement, re.IGNORECASE)
        for fk_match in fk_matches:
            fk = ForeignKey(
                column=fk_match.group(1),
                referencedTable=fk_match.group(2),
                referencedColumn=fk_match.group(3)
            )
            table.foreignKeys.append(fk)

@router.post("/parse", response_model=SqlParseResponse)
async def parse_sql(request: SqlParseRequest):
    logger.info("解析sql")
    """解析SQL语句并返回表结构信息"""
    try:
        parser = SqlParser()
        tables = parser.parse_sql(request.sql)

        logger.info("解析sql结束")
        
        return SqlParseResponse(
            success=True,
            message=f"成功解析 {len(tables)} 个表",
            tables=tables
        )
    except Exception as e:
        import traceback
        print(f"SQL解析错误: {str(e)}")
        print(f"错误详情: {traceback.format_exc()}")
        raise HTTPException(
            status_code=400,
            detail=f"SQL解析失败: {str(e)}"
        )

@router.get("/test")
async def test_sql_parser():
    """测试SQL解析器"""
    test_sql = """
    CREATE TABLE users (
        id INT PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(100) UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status ENUM('active', 'inactive') DEFAULT 'active'
    );
    
    CREATE TABLE orders (
        id INT PRIMARY KEY,
        user_id INT,
        order_date DATETIME,
        total_amount DECIMAL(10,2),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    
    ALTER TABLE users ADD COLUMN phone VARCHAR(20);
    """
    
    parser = SqlParser()
    tables = parser.parse_sql(test_sql)
    
    return {
        "success": True,
        "message": "测试SQL解析成功",
        "tables": [table.dict() for table in tables]
    } 