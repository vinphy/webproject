from fastapi import APIRouter, HTTPException
from typing import Dict, List
from service.resource_service import resource_service

router = APIRouter()

@router.get("/cpu")
async def get_cpu_status():
    """获取CPU状态"""
    try:
        result = resource_service.get_cpu_status()
        # 包装成前端期望的格式
        return {
            "success": True,
            "data": result,
            "message": "获取CPU状态成功"
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "message": f"获取CPU状态失败: {str(e)}"
        }

@router.get("/gpu/history")
async def get_gpu_history(limit: int = 30):
    """获取GPU历史数据"""
    try:
        result = resource_service.get_gpu_history(limit)
        print(result)
        # 包装成前端期望的格式
        return {
            "success": True,
            "data": result,
            "message": "获取GPU历史数据成功"
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "message": f"获取GPU历史数据失败: {str(e)}"
        }