from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from util.FileUtil import FileUtil
import traceback
import logging
import os
import json
from datetime import datetime
import time

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

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
    value: str

class NodeData(BaseModel):
    name: str
    type: str
    tableName: str
    databaseName: Optional[str] = None
    parameters: List[Parameter]
    condition: Optional[str] = None
    icon: Optional[str] = None

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
    # 获取列名和值
    columns = [param.name for param in node_data.parameters]
    values = [f"'{param.value}'" for param in node_data.parameters]  # 添加引号
    type = node_data.type
    
    if type == 'insert':
        # 构建SQL语句
        sql = f"INSERT INTO {node_data.tableName} ({', '.join(columns)}) VALUES ({', '.join(values)});"
    elif type == 'update':
        # 构建SET子句
        set_clauses = [f"{col} = {val}" for col, val in zip(columns, values)]
        # 添加WHERE条件（如果有）
        where_clause = f" WHERE {node_data.condition}" if node_data.condition else ""
        sql = f"UPDATE {node_data.tableName} SET {', '.join(set_clauses)}{where_clause};"
    elif type == 'select':
        # 构建SELECT子句
        select_clause = ', '.join(columns) if columns else '*'
        # 添加WHERE条件（如果有）
        where_clause = f" WHERE {node_data.condition}" if node_data.condition else ""
        sql = f"SELECT {select_clause} FROM {node_data.tableName}{where_clause};"
    elif type == 'delete':
        # 添加WHERE条件（如果有）
        where_clause = f" WHERE {node_data.condition}" if node_data.condition else ""
        sql = f"DELETE FROM {node_data.tableName}{where_clause};"
    elif type == 'create':
        sql_parts = []
        
        # 如果有数据库名，先创建数据库
        if node_data.databaseName:
            save_database_name(node_data.databaseName)
            sql_parts.append(f"CREATE DATABASE IF NOT EXISTS {node_data.databaseName};")
            sql_parts.append(f"USE {node_data.databaseName};")
        
        # 构建字段定义
        field_definitions = []
        for param in node_data.parameters:
            # 根据参数值判断字段类型
            value = param.value.lower()
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
            
            # 添加字段定义
            field_definitions.append(f"{param.name} {field_type}")
        
        # 构建CREATE TABLE语句
        create_table_sql = f"CREATE TABLE {node_data.tableName} (\n    " + \
                          ",\n    ".join(field_definitions) + \
                          "\n);"
        sql_parts.append(create_table_sql)
        
        # 保存表名到对应关系
        if node_data.databaseName and node_data.tableName:
            save_table_name(node_data.databaseName, node_data.tableName)
        
        sql = "\n".join(sql_parts)
    return sql

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
        "parameters": [
            {
                "name": param.name,
                "value": param.value,
                # "type": "field" if node_data.type == "create" else "value"
            }
            for param in node_data.parameters
        ],
        "condition": node_data.condition,
        "generated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "1.0"
    }
    
    # 转换为格式化的JSON字符串
    json_content = json.dumps(json_data, ensure_ascii=False, indent=2)
    return json_content

def generate_cpp(node_data: NodeData) -> str:
    """生成C++源文件"""
    # TODO: 实现C++生成
    return ""

def generate_header(node_data: NodeData) -> str:
    """生成C++头文件"""
    # TODO: 实现头文件生成
    return ""

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
        "parameters": [
            {
                "name": param.name,
                "value": param.value
            }
            for param in node_data.parameters
        ],
        "condition": node_data.condition,
        "generated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": f"预配置的 {node_data.type.upper()} 模型"
    }
    
    # 转换为格式化的JSON字符串
    json_content = json.dumps(draggable_model, ensure_ascii=False, indent=2)
    return json_content

@router.get("/databases")
async def get_databases():
    """获取数据库列表"""
    try:
        workspace_path = FileUtil.get_workspace_path()
        database_file = os.path.join(workspace_path, "database.txt")
        
        databases = []
        if os.path.exists(database_file):
            with open(database_file, 'r', encoding='utf-8') as f:
                databases = [line.strip() for line in f.readlines() if line.strip()]
        
        return {
            'status': 'success',
            'databases': databases
        }
    except Exception as e:
        logger.error(f"获取数据库列表失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

def save_database_name(database_name: str):
    """保存数据库名到文件"""
    try:
        workspace_path = FileUtil.get_workspace_path()
        database_file = os.path.join(workspace_path, "database.txt")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(database_file), exist_ok=True)
        
        # 读取现有数据库列表
        existing_databases = []
        if os.path.exists(database_file):
            with open(database_file, 'r', encoding='utf-8') as f:
                existing_databases = [line.strip() for line in f.readlines() if line.strip()]
        
        # 如果数据库名不存在，则添加
        if database_name not in existing_databases:
            with open(database_file, 'a', encoding='utf-8') as f:
                f.write(f"{database_name}\n")
        
        return True
    except Exception as e:
        logger.error(f"保存数据库名失败: {str(e)}")
        return False

def save_table_name(database_name: str, table_name: str):
    """保存表名到数据库表对应关系文件"""
    try:
        workspace_path = FileUtil.get_workspace_path()
        tables_file = os.path.join(workspace_path, "tables.json")
        
        # 读取现有的数据库表对应关系
        database_tables = {}
        if os.path.exists(tables_file):
            with open(tables_file, 'r', encoding='utf-8') as f:
                database_tables = json.load(f)
        
        # 确保数据库存在
        if database_name not in database_tables:
            database_tables[database_name] = []
        
        # 如果表名不存在，则添加
        if table_name not in database_tables[database_name]:
            database_tables[database_name].append(table_name)
        
        # 保存更新后的对应关系
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
    try:
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
        sql_file_path = os.path.join(sql_dir, f"{node_data.name}.sql")
        with open(sql_file_path, "w", encoding="utf-8") as f:
            f.write(sql_content)
        
        # 生成JSON文件
        json_content = generate_xml(node_data)
        json_file_path = os.path.join(module_dir, f"{node_data.name}.json")
        with open(json_file_path, "w", encoding="utf-8") as f:
            f.write(json_content)
        
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
        
        return {
            "status": "success", 
            "message": "代码生成成功",
            "files": {
                "sql": sql_file_path,
                "json": json_file_path,
                "draggable": draggable_file_path,
                "cpp": cpp_file_path,
                "header": header_file_path
            }
        }
    
    except Exception as e:
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
