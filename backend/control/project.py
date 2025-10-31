from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Any, Dict

from util.db import get_db
from control.auth import get_current_user
from service import project_service
from models import auth_model
from service import log_service
from service import auth_service

router = APIRouter()


class ProjectCreatePayload(BaseModel):
    projectCode: str | None = None
    projectName: str
    projectType: str | None = None
    testLeader: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    projectDesc: str | None = None
    teamMembers: list[Any] | None = None
    selectedTestCaseIds: list[Any] | None = None
    projectParams: dict | None = None
    step2Selections: dict | None = None


@router.post('/', summary='Create project')
def create_project(payload: ProjectCreatePayload, db: Session = Depends(get_db), current_user: auth_model.User = Depends(get_current_user)):
    # 权限检查：需要 'project:create' 权限或角色判断
    if not auth_service.user_has_permission(db, current_user, 'project:create') and not (current_user and getattr(current_user, 'role', None) and current_user.role.name in ('admin', 'project_manager')):
        raise HTTPException(status_code=403, detail='需要 project:create 权限')
    try:
        p = project_service.create_project(db, current_user.id, payload.dict())
        # record operation log
        try:
            log_service.create_log(db, type='操作日志', source='项目管理', user=current_user.username if current_user else None, message=f"创建项目：{p.name}", level='INFO')
        except Exception:
            pass
        return { 'id': p.id, 'name': p.name }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/', summary='List projects')
def list_projects(page: int = 1, size: int = 20, db: Session = Depends(get_db), current_user: auth_model.User = Depends(get_current_user)):
    """Return paginated list of projects for current user."""
    try:
        offset = max(0, (page - 1) * size)
        res = project_service.list_projects(db, owner_id=None, limit=size, offset=offset)
        # res is { items, total }
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/{project_id}', summary='Get project detail')
def get_project_detail(project_id: int, db: Session = Depends(get_db), current_user: auth_model.User = Depends(get_current_user)):
    """获取项目详细信息"""
    try:
        result = project_service.get_project_detail(db, project_id)
        # print(result)
        if not result['success']:
            raise HTTPException(status_code=404, detail=result['message'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'获取项目详情失败: {str(e)}')