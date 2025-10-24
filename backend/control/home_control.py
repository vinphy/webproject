from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from util.db import get_db
from service import home_service
from control.auth import get_current_user
from models import auth_model

router = APIRouter()


@router.get("/profile")
def get_profile(current_user: auth_model.User = Depends(get_current_user), db: Session = Depends(get_db)):
     # 依赖注入：get_current_user 验证用户身份，get_db 获取数据库会话
    profile = home_service.get_home_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="用户不存在")
    return profile
