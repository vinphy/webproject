from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
from util.FileUtil import FileUtil
import traceback
import logging
import os
import json
from datetime import datetime
import time
from typing import Any

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/test")
async def test_route():
    print("=== 测试路由被调用 ===")
    logger.info("=== 测试路由被调用 ===")
    return {"message": "测试路由正常工作"}

@router.post("/test_post")
async def test_post_route(data: dict):
    print(f"=== 测试POST路由被调用，数据: {data} ===")
    logger.info(f"=== 测试POST路由被调用，数据: {data} ===")
    return {"message": "测试POST路由正常工作", "received_data": data}

class FileContent(BaseModel):
    name: str
    content: str

class ModuleFiles(BaseModel):
    module_name: str
    files: List[FileContent]

class ModelFile(BaseModel):
    filename: str
    content: str

class Parameter(BaseModel):
    name: str
    value: Any

class NodeData(BaseModel):
    name: str
    type: str
    tableName: str
    databaseName: Optional[str] = None
    parameters: Optional[List[Parameter]] = None  # 改为可选，支持动态表单数据
    condition: Optional[str] = None
    icon: Optional[str] = None
    sql: Optional[str] = None  # 新增：可选的sql字段
    # 新增：支持动态表单的字段数据
    fields: Optional[List[Dict[str, Any]]] = None  # 表格编辑器数据
    charset: Optional[str] = None
    collation: Optional[str] = None
    # 其他可能的动态字段
    class Config:
        extra = "allow"  # 允许额外字段
        # 添加调试信息
        @classmethod
        def __get_validators__(cls):
            yield cls.validate_to_json
            
        @classmethod
        def validate_to_json(cls, value):
            print(f"=== NodeData验证: {value} ===")
            logger.info(f"=== NodeData验证: {value} ===")
            return value

class DraggableModelRequest(BaseModel):
    file_content: str

@router.post("/write_module_files")
async def write_module_files(module_files: ModuleFiles):
    """写入模块文件"""
    try:
        logger.debug(f"开始写入模块文件: {module_files.module_name}")
        logger.debug(f"文件列表: {[f.name for f in module_files.files]}")
        
        # 转换文件列表格式
        files = [{"name": file.name, "content": file.content} for file in module_files.files]
        
        result = FileUtil.write_module_files(module_files.module_name, files)
        logger.debug(f"写入结果: {result}")
        
        if result['status'] == 'error':
            raise HTTPException(status_code=500, detail=result['message'])
        return result
    except Exception as e:
        logger.error(f"写入文件失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_all_modules")
async def get_all_modules():
    """获取所有模块的文件结构"""
    try:
        modules = FileUtil.get_all_modules()
        return {
            'status': 'success',
            'data': modules
        }
    except Exception as e:
        logger.error(f"获取模块列表失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_module_structure/{module_name}")
async def get_module_structure(module_name: str):
    """获取指定模块的文件结构"""
    try:
        structure = FileUtil.get_module_structure(module_name)
        if structure is None:
            raise HTTPException(status_code=404, detail=f"Module {module_name} not found")
        return {
            'status': 'success',
            'data': structure
        }
    except Exception as e:
        logger.error(f"获取模块结构失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/write_model_file")
async def write_model_file(model_file: ModelFile):
    """
    保存模型文件到 workspace/app 目录
    """
    try:
        workspace_path = FileUtil.get_workspace_path()
        app_dir = os.path.join(workspace_path, 'app')
        
        # 确保app目录存在
        if not os.path.exists(app_dir):
            os.makedirs(app_dir)
        
        # 构建文件路径，确保使用.json扩展名
        filename = model_file.filename
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        file_path = os.path.join(app_dir, filename)
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(model_file.content)
        
        logger.info(f"模型文件已保存到: {file_path}")
        
        return {
            'status': 'success',
            'message': '模型文件保存成功',
            'file_path': file_path
        }
        
    except Exception as e:
        logger.error(f"保存模型文件失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_file_structure")
async def get_file_structure():
    """
    获取workspace目录下的文件结构
    """
    try:
        workspace_path = FileUtil.get_workspace_path()
        
        def get_directory_structure(path):
            result = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                is_dir = os.path.isdir(item_path)
                result.append({
                    'name': item,
                    'type': 'directory' if is_dir else 'file',
                    'path': os.path.relpath(item_path, workspace_path),
                    'children': get_directory_structure(item_path) if is_dir else None
                })
            return result

        files = get_directory_structure(workspace_path)
        
        return {
            'status': 'success',
            'files': files
        }
        
    except Exception as e:
        logger.error(f"获取文件结构失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/read_file")
async def read_file(path: str):
    """
    读取文件内容
    """
    try:
        workspace_path = FileUtil.get_workspace_path()
        file_path = os.path.join(workspace_path, path)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
            
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=400, detail="路径不是文件")
            
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return {
            'status': 'success',
            'content': content
        }
        
    except Exception as e:
        logger.error(f"读取文件失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

def generate_sql(node_data: NodeData) -> str:
    """生成SQL插入语句"""
    
    # 如果节点数据中包含sql字段，直接使用该SQL
    type = node_data.type
    if node_data.sql:
        if type == 'create':
            if node_data.databaseName and node_data.tableName :
                if node_data.parameters and isinstance(node_data.parameters, list):
                    for param in node_data.parameters:
                        logger.info('-----')
                        logger.info(param)
                        pvalue = param.value
                        logger.info(pvalue)
                        if isinstance(pvalue, list):
                            fieldName = [field['fieldName'] for field in pvalue]
                save_table_name(node_data.databaseName, node_data.tableName, fieldName)
        return node_data.sql

    
    # 处理不同的数据结构
    if type == 'create':
        return generate_create_sql(node_data)
    elif type == 'insert':
        return generate_insert_sql(node_data)
    elif type == 'update':
        return generate_update_sql(node_data)
    elif type == 'select':
        return generate_select_sql(node_data)
    elif type == 'delete':
        return generate_delete_sql(node_data)
    else:
        return f"-- 未支持的操作类型: {type}"

def generate_create_sql(node_data: NodeData) -> str:
    """生成CREATE语句，并保存表结构到tables.json"""
    sql_parts = []
    columns_for_save = []  # 用于保存到tables.json

    logger.info("--生成sql")
    
    # 如果有数据库名，先创建数据库
    if node_data.databaseName:
        sql_parts.append(f"CREATE DATABASE IF NOT EXISTS {node_data.databaseName};")
        sql_parts.append(f"USE {node_data.databaseName};")
    
    # 处理表创建
    if node_data.tableName:
        
        # 构建字段定义
        field_definitions = []
        
        # 优先使用fields数据（动态表单的table-editor）
        if node_data.fields and isinstance(node_data.fields, list):
            for field in node_data.fields:
                field_name = field.get('fieldName', '')
                field_type = field.get('fieldType', 'VARCHAR(255)')
                is_primary = field.get('isPrimary', False)
                not_null = field.get('notNull', False)
                
                if field_name:
                    field_def = f"{field_name} {field_type}"
                    if is_primary:
                        field_def += " PRIMARY KEY"
                    if not_null:
                        field_def += " NOT NULL"
                    field_definitions.append(field_def)
                    columns_for_save.append(field_name)
        
        # 如果没有fields数据，使用parameters数据
        elif node_data.parameters and isinstance(node_data.parameters, list):
            for param in node_data.parameters:
               
                if hasattr(param, 'name') and hasattr(param, 'value'):
                    value = str(param.value).lower()
                    if value in ['int', 'integer']:
                        field_type = 'INT'
                    elif value in ['varchar', 'char', 'string', 'text']:
                        field_type = 'VARCHAR(255)'
                    elif value in ['float', 'double', 'decimal']:
                        field_type = 'DECIMAL(10,2)'
                    elif value in ['date', 'datetime', 'timestamp']:
                        field_type = 'DATETIME'
                    elif value in ['bool', 'boolean']:
                        field_type = 'BOOLEAN'
                    else:
                        field_type = 'VARCHAR(255)'  # 默认类型
                    field_definitions.append(f"{param.name} {field_type}")
                    columns_for_save.append(param.name)
        
        # 构建CREATE TABLE语句
        if field_definitions:
            create_table_sql = f"CREATE TABLE {node_data.tableName} (\n    " + \
                              ",\n    ".join(field_definitions) + \
                              "\n);"
            sql_parts.append(create_table_sql)
        logger.info("f'是否存储表数据'")
        logger.info(f'数据库：',node_data.databaseName)
        logger.info(f'数据表：',node_data.tableName)
        logger.info(f'数据列：',columns_for_save)
        # 保存表结构到tables.json
        if node_data.databaseName and node_data.tableName and columns_for_save:
            logger.info(f'是否存储表数据')
            save_table_name(node_data.databaseName, node_data.tableName, columns_for_save)
    
    return "\n".join(sql_parts)

def generate_insert_sql(node_data: NodeData) -> str:
    """生成INSERT语句"""
    # 获取列名和值
    columns, values = extract_columns_and_values(node_data)
    
    # 如果有数据库名和表名，保存表名对应关系
    if node_data.databaseName and node_data.tableName:
        save_table_name(node_data.databaseName, node_data.tableName, columns)
    
    if columns and values:
        sql = f"INSERT INTO {node_data.tableName} ({', '.join(columns)}) VALUES ({', '.join(values)});"
        return sql
    else:
        return f"-- INSERT语句生成失败: 缺少列数据"

def generate_update_sql(node_data: NodeData) -> str:
    """生成UPDATE语句"""
    # 获取列名和值
    columns, values = extract_columns_and_values(node_data)
    
    if columns and values:
        # 构建SET子句
        set_clauses = [f"{col} = {val}" for col, val in zip(columns, values)]
        # 添加WHERE条件（如果有）
        where_clause = f" WHERE {node_data.condition}" if node_data.condition else ""
        sql = f"UPDATE {node_data.tableName} SET {', '.join(set_clauses)}{where_clause};"
        return sql
    else:
        return f"-- UPDATE语句生成失败: 缺少列数据"

def generate_select_sql(node_data: NodeData) -> str:
    """生成SELECT语句"""
    # 获取列名
    columns, _ = extract_columns_and_values(node_data)
    
    # 构建SELECT子句
    select_clause = ', '.join(columns) if columns else '*'
    # 添加WHERE条件（如果有）
    where_clause = f" WHERE {node_data.condition}" if node_data.condition else ""
    sql = f"SELECT {select_clause} FROM {node_data.tableName}{where_clause};"
    return sql

def generate_delete_sql(node_data: NodeData) -> str:
    """生成DELETE语句"""
    # 添加WHERE条件（如果有）
    where_clause = f" WHERE {node_data.condition}" if node_data.condition else ""
    sql = f"DELETE FROM {node_data.tableName}{where_clause};"
    return sql

def extract_columns_and_values(node_data: NodeData) -> tuple:
    """提取列名和值，支持多种数据结构"""
    columns = []
    values = []
    
    # 优先使用parameters数据
    if node_data.parameters and isinstance(node_data.parameters, list):
        for param in node_data.parameters:
            if hasattr(param, 'name') and hasattr(param, 'value'):
                columns.append(param.name)
                # 如果是字符串，直接加引号；如果是对象/数组，转json字符串
                if isinstance(param.value, (dict, list)):
                    import json
                    values.append(f"'{json.dumps(param.value, ensure_ascii=False)}'")
                else:
                    values.append(f"'{param.value}'")
    
    # 如果没有parameters，尝试从其他字段提取
    elif hasattr(node_data, '__dict__'):
        # 遍历所有字段，排除特殊字段
        exclude_fields = {'name', 'type', 'tableName', 'databaseName', 'condition', 'icon', 'sql', 'fields', 'charset', 'collation'}
        for key, value in node_data.__dict__.items():
            if key not in exclude_fields and value is not None and value != '':
                columns.append(key)
                values.append(f"'{value}'")
    
    return columns, values

def generate_xml(node_data: NodeData) -> str:
    """生成JSON描述文件"""
    # 构建JSON数据结构
    json_data = {
        "module_info": {
            "name": node_data.name,
            "type": node_data.type,
            "description": f"{node_data.type.upper()} 模块配置信息"
        },
        "database_config": {
            "database_name": node_data.databaseName,
            "table_name": node_data.tableName
        },
        "parameters": [],
        "condition": node_data.condition,
        "generated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "1.0"
    }
    
    # 处理参数数据
    if node_data.parameters and isinstance(node_data.parameters, list):
        json_data["parameters"] = [
            {
                "name": param.name,
                "value": param.value,
            }
            for param in node_data.parameters
        ]
    elif node_data.fields and isinstance(node_data.fields, list):
        # 处理动态表单的fields数据
        json_data["parameters"] = [
            {
                "name": field.get('fieldName', ''),
                "value": field.get('fieldType', ''),
                "isPrimary": field.get('isPrimary', False),
                "notNull": field.get('notNull', False)
            }
            for field in node_data.fields
        ]
    
    # 添加其他动态字段
    if node_data.charset:
        json_data["charset"] = node_data.charset
    if node_data.collation:
        json_data["collation"] = node_data.collation
    
    # 转换为格式化的JSON字符串
    json_content = json.dumps(json_data, ensure_ascii=False, indent=2)
    return json_content

def generate_cpp(node_data: NodeData) -> str:
    """生成C++源文件"""
    return f"// {node_data.name}.cpp\n// 自动生成的C++源文件\n"

def generate_header(node_data: NodeData) -> str:
    """生成C++头文件"""
    return f"// {node_data.name}.h\n// 自动生成的C++头文件\n"

def generate_draggable_model(node_data: NodeData) -> str:
    """生成可拖拽的模型文件"""

    
    # 优先使用传入的图标，如果没有则根据类型获取默认图标
    if node_data.icon:
        icon_path = node_data.icon
    else:
        icon_path = "/src/assets/Data.svg"
    
    # 构建可拖拽模型的数据结构
    draggable_model = {
        "type": "draggable_model",
        "version": "1.0",
        "model_config": {
            "name": node_data.name,
            "type": node_data.type,
            "icon": icon_path,  # 使用动态图标路径
            "category": "basic" if node_data.type in ["insert", "update", "select", "create", "delete"] else "custom",
            "inputs": [
                { "name": "输入", "connected": False, "id": "input" }
            ],
            "outputs": [
                { "name": "输出", "connected": False, "id": "output" }
            ]
        },
        "database_config": {
            "database_name": node_data.databaseName,
            "table_name": node_data.tableName
        },
        "parameters": [],
        "condition": node_data.condition,
        "generated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": f"预配置的 {node_data.type.upper()} 模型"
    }
    
    # 处理参数数据
    if node_data.parameters and isinstance(node_data.parameters, list):
        draggable_model["parameters"] = [
            {
                "name": param.name,
                "value": param.value
            }
            for param in node_data.parameters
        ]
    elif node_data.fields and isinstance(node_data.fields, list):
        # 处理动态表单的fields数据
        draggable_model["parameters"] = [
            {
                "name": field.get('fieldName', ''),
                "value": field.get('fieldType', ''),
                "isPrimary": field.get('isPrimary', False),
                "notNull": field.get('notNull', False)
            }
            for field in node_data.fields
        ]
    
    # 添加其他动态字段
    if node_data.charset:
        draggable_model["charset"] = node_data.charset
    if node_data.collation:
        draggable_model["collation"] = node_data.collation
    
    # 转换为格式化的JSON字符串
    json_content = json.dumps(draggable_model, ensure_ascii=False, indent=2)
    return json_content

@router.get("/databases")
async def get_databases():
    """获取数据库列表"""
    try:
        workspace_path = FileUtil.get_workspace_path()
        tables_file = os.path.join(workspace_path, "tables.json")
        
        databases = []
        
        # 从tables.json中提取数据库列表
        if os.path.exists(tables_file):
            with open(tables_file, 'r', encoding='utf-8') as f:
                database_tables = json.load(f)
                databases = list(database_tables.keys())
        
        return {
            'status': 'success',
            'databases': databases
        }
    except Exception as e:
        logger.error(f"获取数据库列表失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

def save_table_name(database_name: str, table_name: str, columns: list):
    """保存表名和字段到数据库表对应关系文件，结构为 {db: {table: [columns]}}"""
    try:
        workspace_path = FileUtil.get_workspace_path()
        tables_file = os.path.join(workspace_path, "tables.json")
        os.makedirs(workspace_path, exist_ok=True)
        # 读取现有的数据库表对应关系
        database_tables = {}
        if os.path.exists(tables_file):
            with open(tables_file, 'r', encoding='utf-8') as f:
                database_tables = json.load(f)
        # 只用新结构
        if database_name not in database_tables:
            database_tables[database_name] = {}
        database_tables[database_name][table_name] = columns or []
        # 保存更新
        with open(tables_file, 'w', encoding='utf-8') as f:
            json.dump(database_tables, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存表名失败: {str(e)}")
        return False

@router.get("/tables")
async def get_tables(database_name: str = None):
    """获取表列表"""
    try:
        workspace_path = FileUtil.get_workspace_path()
        tables_file = os.path.join(workspace_path, "tables.json")
        
        database_tables = {}
        if os.path.exists(tables_file):
            with open(tables_file, 'r', encoding='utf-8') as f:
                database_tables = json.load(f)
        
        if database_name:
            # 返回指定数据库的表列表
            tables = database_tables.get(database_name, [])
            return {
                'status': 'success',
                'tables': tables
            }
        else:
            # 返回所有数据库表对应关系
            return {
                'status': 'success',
                'database_tables': database_tables
            }
    except Exception as e:
        logger.error(f"获取表列表失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_code(node_data: NodeData):
    print("=== 请求到达generate_code函数 ===")
    logger.info("=== 请求到达generate_code函数 ===")
    
    try:
        # 添加详细的调试日志
        logger.info("=== 开始代码生成 ===")
        logger.info(f"接收到的node_data类型: {type(node_data)}")
        logger.info(f"node_data原始数据: {node_data}")
        logger.info(f"node_data.dict(): {node_data.dict()}")
        logger.info(f"node_data.name: {node_data.name}")
        logger.info(f"node_data.type: {node_data.type}")
        logger.info(f"node_data.tableName: {node_data.tableName}")
        logger.info(f"node_data.databaseName: {node_data.databaseName}")
        logger.info(f"node_data.parameters: {node_data.parameters}")
        logger.info(f"node_data.fields: {node_data.fields}")
        logger.info(f"node_data.condition: {node_data.condition}")
        logger.info(f"node_data.sql: {node_data.sql}")
        logger.info(f"node_data.charset: {getattr(node_data, 'charset', None)}")
        logger.info(f"node_data.collation: {getattr(node_data, 'collation', None)}")
        
        # 获取工作空间路径
        workspace_path = FileUtil.get_workspace_path()
        if not workspace_path:
            raise HTTPException(status_code=500, detail="工作空间路径未配置")

        # 创建必要的目录
        module_dir = os.path.join(workspace_path, node_data.name)
        sql_dir = os.path.join(module_dir, "sql")
        src_dir = os.path.join(module_dir, "src")
        
        # 确保目录存在
        os.makedirs(sql_dir, exist_ok=True)
        os.makedirs(src_dir, exist_ok=True)
        
        # 生成SQL文件
        sql_content = generate_sql(node_data)
        logger.info(f"生成的SQL内容: {sql_content}")
        sql_file_path = os.path.join(sql_dir, f"{node_data.name}.sql")
        with open(sql_file_path, "w", encoding="utf-8") as f:
            f.write(sql_content)
        
        # # 生成JSON文件
        # json_content = generate_xml(node_data)
        # json_file_path = os.path.join(module_dir, f"{node_data.name}.json")
        # with open(json_file_path, "w", encoding="utf-8") as f:
        #     f.write(json_content)
        
        # 生成可拖拽模型文件
        draggable_content = generate_draggable_model(node_data)
        draggable_file_path = os.path.join(module_dir, f"{node_data.name}_model.json")
        with open(draggable_file_path, "w", encoding="utf-8") as f:
            f.write(draggable_content)
        
        # 生成C++文件
        cpp_content = generate_cpp(node_data)
        cpp_file_path = os.path.join(src_dir, f"{node_data.name}.cpp")
        with open(cpp_file_path, "w", encoding="utf-8") as f:
            f.write(cpp_content)
        
        # 生成头文件
        header_content = generate_header(node_data)
        header_file_path = os.path.join(src_dir, f"{node_data.name}.h")
        with open(header_file_path, "w", encoding="utf-8") as f:
            f.write(header_content)
        
        logger.info("=== 代码生成完成 ===")
        
        return {
            "status": "success", 
            "message": "代码生成成功",
            "files": {
                "sql": sql_file_path,
                # "json": json_file_path,
                "draggable": draggable_file_path,
                "cpp": cpp_file_path,
                "header": header_file_path
            }
        }
    
    except Exception as e:
        logger.error(f"代码生成失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parse_draggable_model")
async def parse_draggable_model(request: DraggableModelRequest):
    """解析可拖拽模型文件"""
    try:
        # 解析JSON内容
        model_data = json.loads(request.file_content)
        
        # 验证文件格式
        if model_data.get("type") != "draggable_model":
            raise HTTPException(status_code=400, detail="不是有效的可拖拽模型文件")
        
        # 提取模型配置
        model_config = model_data.get("model_config", {})
        database_config = model_data.get("database_config", {})
        parameters = model_data.get("parameters", [])
        condition = model_data.get("condition")
        logger.info(f'-----图标地址：{model_config.get("icon", "/src/assets/Data.svg")}')
        
        # 构建节点数据
        node_data = {
            "name": model_config.get("name", "unnamed"),
            "type": model_config.get("type", "custom"),
            "icon": model_config.get("icon", "/src/assets/Data.svg"),
            "category": model_config.get("category", "custom"),
            "inputs": model_config.get("inputs", []),
            "outputs": model_config.get("outputs", []),
            "databaseName": database_config.get("database_name"),
            "tableName": database_config.get("table_name"),
            "parameters": parameters,
            "condition": condition,
            "x": 100,  # 默认位置
            "y": 100,
            "id": f"node_{int(time.time() * 1000)}"  # 生成唯一ID
        }
        
        return {
            "status": "success",
            "node_data": node_data,
            "description": model_data.get("description", "预配置模型")
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="JSON格式错误")
    except Exception as e:
        logger.error(f"解析拖拽模型文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parse_draggable_test")
async def parse_draggable_test(request: DraggableModelRequest):
    """解析 test.json 文件，提取 nodes 和 connections"""
    try:
        data = json.loads(request.file_content)
        nodes = data.get("nodes", [])
        connections = data.get("connections", [])
        return {
            "status": "success",
            "nodes": nodes,
            "connections": connections,
            "description": data.get("metadata", {}).get("description", "模型图")
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="JSON格式错误")
    except Exception as e:
        logger.error(f"解析 test.json 文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/columns")
async def get_columns(database_name: str, table_name: str):
    """获取指定数据库和表的列名"""
    try:
        workspace_path = FileUtil.get_workspace_path()
        tables_file = os.path.join(workspace_path, "tables.json")
        if not os.path.exists(tables_file):
            raise HTTPException(status_code=404, detail="tables.json不存在")
        with open(tables_file, 'r', encoding='utf-8') as f:
            database_tables = json.load(f)
        if database_name not in database_tables:
            raise HTTPException(status_code=404, detail=f"数据库 {database_name} 不存在")
        tables = database_tables[database_name]
        if table_name not in tables:
            raise HTTPException(status_code=404, detail=f"表 {table_name} 不存在于数据库 {database_name}")
        columns = tables[table_name]
        return {
            'status': 'success',
            'columns': columns
        }
    except Exception as e:
        logger.error(f"获取列名失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_available_modules")
async def get_available_modules():
    """
    获取可用的模型列表
    从configData/modules.json文件中读取
    """
    try:
        # 获取项目根目录
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_file = os.path.join(current_dir, 'configData', 'modules.json')
        
        if not os.path.exists(config_file):
            logger.warning(f"配置文件不存在: {config_file}")
            return {
                'status': 'success',
                'data': {
                    'modules': [],
                    'categories': []
                }
            }
        
        # 读取JSON文件
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        logger.info(f"成功读取模型配置，共 {len(config_data.get('modules', []))} 个模块")
        
        return {
            'status': 'success',
            'data': config_data
        }
        
    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_module_by_id/{module_id}")
async def get_module_by_id(module_id: str):
    """
    根据模块ID获取模块详情
    """
    try:
        # 获取项目根目录
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_file = os.path.join(current_dir, 'configData', 'modules.json')
        
        if not os.path.exists(config_file):
            raise HTTPException(status_code=404, detail="配置文件不存在")
        
        # 读取JSON文件
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 查找指定模块
        modules = config_data.get('modules', [])
        module = next((m for m in modules if m['id'] == module_id), None)
        
        if not module:
            raise HTTPException(status_code=404, detail=f"模块 {module_id} 不存在")
        
        return {
            'status': 'success',
            'data': module
        }
        
    except Exception as e:
        logger.error(f"获取模块详情失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_model_modules")
async def get_model_modules():
    """
    获取模型列表
    从configData目录下的所有JSON文件中读取并合并
    支持新的三级层级结构：大层级->子层级->模块
    支持通过order字段控制显示顺序
    """
    try:
        # 获取项目根目录
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_dir = os.path.join(current_dir, 'configData')
        
        if not os.path.exists(config_dir):
            logger.warning(f"配置目录不存在: {config_dir}")
            return {
                'status': 'success',
                'data': {}
            }
        
        # 合并所有JSON文件的数据
        merged_data = {}
        file_order_info = {}  # 存储文件顺序信息
        
        # 遍历configData目录下的所有JSON文件
        json_files = [f for f in os.listdir(config_dir) if f.endswith('.json')]
        logger.info(f"找到 {len(json_files)} 个JSON配置文件: {json_files}")
        
        for json_file in json_files:
            file_path = os.path.join(config_dir, json_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                
                # 合并文件数据到总数据中
                for category_key, category_data in file_data.items():
                    if category_key in merged_data:
                        # 如果大层级已存在，合并子层级
                        if 'children' in category_data and 'children' in merged_data[category_key]:
                            for sub_category_key, sub_category_data in category_data['children'].items():
                                if sub_category_key in merged_data[category_key]['children']:
                                    # 如果子层级已存在，合并模块
                                    if 'children' in sub_category_data and 'children' in merged_data[category_key]['children'][sub_category_key]:
                                        merged_data[category_key]['children'][sub_category_key]['children'].extend(sub_category_data['children'])
                                    else:
                                        merged_data[category_key]['children'][sub_category_key] = sub_category_data
                                else:
                                    # 如果子层级不存在，直接添加
                                    merged_data[category_key]['children'][sub_category_key] = sub_category_data
                    else:
                        # 如果大层级不存在，直接添加
                        merged_data[category_key] = category_data
                        # 记录顺序信息
                        file_order_info[category_key] = {
                            'order': category_data.get('order', 999),  # 默认顺序为999
                            'file': json_file
                        }
                
                logger.info(f"成功读取并合并配置文件: {json_file}")
                
            except Exception as e:
                logger.error(f"读取配置文件 {json_file} 失败: {str(e)}")
                continue
        
        if not merged_data:
            logger.warning("没有找到有效的配置文件")
            return {
                'status': 'success',
                'data': {}
            }
        
        # 按order字段排序大层级
        sorted_categories = sorted(merged_data.items(), key=lambda x: file_order_info.get(x[0], {}).get('order', 999))
        merged_data = dict(sorted_categories)
        
        # 统计模块数量
        total_categories = len(merged_data)
        total_sub_categories = 0
        total_modules = 0
        
        for category_key, category_data in merged_data.items():
            if 'children' in category_data:
                total_sub_categories += len(category_data['children'])
                for sub_category_key, sub_category_data in category_data['children'].items():
                    if 'children' in sub_category_data:
                        total_modules += len(sub_category_data['children'])
        
        logger.info(f"成功合并模型配置，共 {total_categories} 个大层级，{total_sub_categories} 个子层级，{total_modules} 个模块")
        logger.info(f"大层级显示顺序: {[key for key in merged_data.keys()]}")
        
        return {
            'status': 'success',
            'data': merged_data
        }
        
    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_model_by_id/{module_id}")
async def get_model_by_id(module_id: int):
    """
    根据模块ID获取模块详情
    """
    try:
        # 获取项目根目录
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_file = os.path.join(current_dir, 'configData', 'model_modules.json')
        
        if not os.path.exists(config_file):
            raise HTTPException(status_code=404, detail="配置文件不存在")
        
        # 读取JSON文件
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 查找指定模块
        basic_modules = config_data.get('basic', [])
        custom_modules = config_data.get('custom', [])
        
        module = next((m for m in basic_modules if m['id'] == module_id), None)
        if not module:
            module = next((m for m in custom_modules if m['id'] == module_id), None)
        
        if not module:
            raise HTTPException(status_code=404, detail=f"模块 {module_id} 不存在")
        
        return {
            'status': 'success',
            'data': module
        }
        
    except Exception as e:
        logger.error(f"获取模块详情失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
