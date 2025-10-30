from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from util.db import get_db
from service import home_service
from control.auth import get_current_user
from models import auth_model
from service.home_service import get_monthly_project_stats

router = APIRouter()


@router.get("/profile")
def get_profile(current_user: auth_model.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取首页个人资料信息"""
    profile = home_service.get_home_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="用户不存在")
    return profile


@router.get("/project-stats")
def get_project_stats(current_user: auth_model.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取项目执行进度统计数据"""
    try:
        stats = home_service.get_project_stats(db, current_user.id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目统计数据失败: {str(e)}")


@router.get("/monthly-stats", response_model=dict)
async def get_monthly_project_stats_api(
    current_user: auth_model.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    months: int = Query(12, description="统计月份数", ge=1, le=24)
):
    """获取项目月度统计数据接口"""
    try:
        result = get_monthly_project_stats(db, current_user.id, months)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取月度统计数据失败: {str(e)}")

@router.get("/current-testing-projects", response_model=dict)
async def get_current_testing_projects_api(
    current_user: auth_model.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(10, description="项目数量限制", ge=1, le=50)
):
    """获取当前正在测试的项目数据接口"""
    try:
        result = home_service.get_current_testing_projects(db, current_user.id, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取当前测试项目数据失败: {str(e)}")