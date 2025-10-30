from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from util.db import get_db
from service import home_service
from control.auth import get_current_user
from models import auth_model

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