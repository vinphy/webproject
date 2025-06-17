from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from service.bit_test_service import BitTestService
import io
from util.FileUtil import FileUtil
import os

router = APIRouter()
bit_test_service = BitTestService()

@router.get("/list")
async def get_test_list(page: int = 1, size: int = 10):
    try:
        result = bit_test_service.get_test_list(page, size)
        return {
            'status': 'success',
            'data': {
                'items': result['items'],
                'total': result['total']
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start")
async def start_test():
    try:
        bit_test_service.start_test()
        return {
            'status': 'success',
            'message': '测试已启动'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_test():
    try:
        bit_test_service.stop_test()
        return {
            'status': 'success',
            'message': '测试已停止'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export/excel")
async def export_excel(file_data: dict):
    try:
        workspace_path = FileUtil.get_workspace_path()
        file_path = file_data.get('filePath')
        file_path = os.path.join(workspace_path,'excel',file_path)
        print(f"保存路径:{file_path}")
        if not file_path:
            return {
                'status': 'error',
                'message': '未提供文件路径'
            }
            
        result = bit_test_service.export_excel(file_path)
        if result:
            return {
                'status': 'success',
                'message': 'Excel导出成功'
            }
        else:
            return {
                'status': 'error',
                'message': 'Excel导出失败'
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

@router.post("/export/word")
async def export_word(file_data: dict):
    try:
        workspace_path = FileUtil.get_workspace_path()
        file_path = file_data.get('filePath')
        file_path = os.path.join(workspace_path,'excel',file_path)
        print(f"保存路径:{file_path}")
        if not file_path:
            return {
                'status': 'error',
                'message': '未提供文件路径'
            }
        result = bit_test_service.export_word(file_path)
        if result:
            return {
                'status': 'success',
                'message': 'Word导出成功'
            }
        else:
            return {
                'status': 'error',
                'message': 'Word导出失败'
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }