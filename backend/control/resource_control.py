from fastapi import APIRouter, HTTPException
from service.resource_service import resource_service
from typing import Dict, List

router = APIRouter()

@router.get("/status", response_model=Dict)
async def get_resource_status():
    """获取资源状态"""
    try:
        # print(resource_service.get_resource_status())   
        return resource_service.get_resource_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取资源状态失败: {str(e)}")

@router.get("/cpu", response_model=Dict)
async def get_cpu_status():
    """获取CPU状态"""
    try:
        print(resource_service.get_cpu_status())
        return resource_service.get_cpu_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取CPU状态失败: {str(e)}")

@router.get("/gpu", response_model=Dict)
async def get_gpu_status():
    """获取GPU状态"""
    try:
        return resource_service.get_gpu_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取GPU状态失败: {str(e)}")

@router.get("/gpu/history", response_model=List[Dict])
async def get_gpu_history(limit: int = 30):
    """获取GPU历史数据"""
    try:
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="limit参数必须在1-100之间")
        return resource_service.get_gpu_history(limit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取GPU历史数据失败: {str(e)}")

@router.get("/cpu/history", response_model=List[Dict])
async def get_cpu_history(limit: int = 30):
    """获取CPU历史数据"""
    try:
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="limit参数必须在1-100之间")
        return resource_service.get_cpu_history(limit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取CPU历史数据失败: {str(e)}")