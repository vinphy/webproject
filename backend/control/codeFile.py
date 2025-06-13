from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from util.FileUtil import FileUtil

router = APIRouter()

class FileInfo(BaseModel):
    name: str
    content: str

class ModuleFiles(BaseModel):
    module_name: str
    files: List[FileInfo]

@router.post("/write_module_files")
async def write_module_files(module_files: ModuleFiles):
    """写入模块相关文件
    
    Args:
        module_files: 包含模块名称和文件列表的请求体
        
    Returns:
        Dict: 写入结果
    """
    try:
        # 转换文件列表格式
        files = [{"name": file.name, "content": file.content} for file in module_files.files]
        
        # 写入文件
        result = FileUtil.write_module_files(module_files.module_name, files)
        
        if result['status'] == 'error':
            raise HTTPException(status_code=500, detail=result['message'])
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 