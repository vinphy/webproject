from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from util.FileUtil import FileUtil
import traceback
import logging

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