from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from util.FileUtil import FileUtil
import traceback
import logging
import os

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