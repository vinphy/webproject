from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from util.db import get_db
from service import log_service, auth_service
from control.auth import get_current_user

router = APIRouter()


# Pydantic Schemas
class LogOut(BaseModel):
    id: int
    type: str
    source: Optional[str] = None
    user: Optional[str] = None
    message: Optional[str] = None
    level: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True


class LogListOut(BaseModel):
    items: List[LogOut]
    total: int


@router.get("/list", response_model=LogListOut)
def list_logs(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=200),
    type: str = Query("", description="日志类型：操作日志/运行日志/异常日志/正常日志，可为空"),
    keyword: str = Query("", description="关键字，匹配 message/source/user"),
    startDate: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    endDate: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    # 权限检查：需要 logs:view 权限或 admin
    if not auth_service.user_has_permission(db, current_user, 'logs:view') and not (current_user.role and current_user.role.name == 'admin'):
        raise HTTPException(status_code=403, detail='需要 logs:view 权限')
    try:
        res = log_service.list_logs(db, page=page, size=size, type=type or None, keyword=keyword or None, startDate=startDate, endDate=endDate)
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{log_id}", response_model=LogOut)
def get_log(log_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # require logs:view
    if not auth_service.user_has_permission(db, current_user, 'logs:view') and not (current_user.role and current_user.role.name == 'admin'):
        raise HTTPException(status_code=403, detail='需要 logs:view 权限')
    item = log_service.get_log(db, log_id)
    if not item:
        raise HTTPException(status_code=404, detail="日志不存在")
    return item


@router.post("/seed")
def seed_logs(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Only admin or auth:manage can seed demo logs
    if not auth_service.user_has_permission(db, current_user, 'auth:manage') and not (current_user.role and current_user.role.name == 'admin'):
        raise HTTPException(status_code=403, detail='需要 auth:manage 权限')
    # Use service to create demo logs
    samples = [
        { 'type': '操作日志', 'source': '项目管理', 'user': 'admin', 'message': '创建项目：智能测试平台', 'level': 'INFO' },
        { 'type': '运行日志', 'source': '任务调度', 'user': 'system', 'message': '开始执行漏洞扫描任务#42', 'level': 'INFO' },
        { 'type': '异常日志', 'source': '接口服务', 'user': 'system', 'message': '请求超时：/api/run/start 504', 'level': 'ERROR' },
        { 'type': '正常日志', 'source': '监控服务', 'user': 'system', 'message': 'CPU使用率 35%，内存 62%', 'level': 'INFO' },
        { 'type': '操作日志', 'source': '用例管理', 'user': 'tester', 'message': '更新测试用例：登录功能-正向', 'level': 'INFO' }
    ]
    for s in samples:
        log_service.create_log(db, type=s['type'], source=s.get('source'), user=s.get('user'), message=s.get('message'), level=s.get('level'))
    return { 'status': 'success', 'inserted': len(samples) }