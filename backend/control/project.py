from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Any, Dict

from util.db import get_db
from control.auth import get_current_user
from service import project_service
from models import auth_model

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
    try:
        p = project_service.create_project(db, current_user.id, payload.dict())
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
