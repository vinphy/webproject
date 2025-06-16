from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from service.bit_test_service import BitTestService
import io

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

@router.get("/export/excel")
async def export_excel():
    try:
        excel_data = bit_test_service.export_excel()
        return FileResponse(
            io.BytesIO(excel_data),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename='符合性测试报告.xlsx'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/word")
async def export_word():
    try:
        word_data = bit_test_service.export_word()
        return FileResponse(
            io.BytesIO(word_data),
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename='符合性测试报告.docx'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 