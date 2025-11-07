from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from pydantic import BaseModel
import os

from util.db import get_db
from service import project_service, log_service
from service.log_file_service import log_file_service
from service.result_image_service import result_image_service
from control.auth import get_current_user
from models.auth_model import User
from models.project_model import Project

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
def create_project_endpoint(payload: ProjectCreatePayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 权限检查：需要 'project:create' 权限或角色判断
    from service import auth_service
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
def list_projects_endpoint(page: int = 1, size: int = 20, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Return paginated list of projects for current user."""
    try:
        offset = max(0, (page - 1) * size)
        res = project_service.list_projects(db, owner_id=None, limit=size, offset=offset)
        # res is { items, total }
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/{project_id}', summary='Get project detail')
def get_project_detail_endpoint(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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

class ProjectLogsResponse(BaseModel):
    success:bool
    data:list[str]
    message:str=""
    last_position:int=0

@router.get('/{project_id}/logs',response_model=ProjectLogsResponse)
def get_project_logs(
    project_id: int,
    last_position : int = 0, #上次读取的位置
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)   
):
    """获取项目运行日志"""
    try:
        # 1. 获取项目信息，确定日志文件路径
        project_result = project_service.get_project_detail(db, project_id)
        if not project_result['success']:
            return ProjectLogsResponse(success=False, data=[], message="项目不存在")
        
        project_data = project_result['data']
        project_name = project_data.get('name', f'project_{project_id}')
        log_file_name = project_data.get('log_file_name')  # 获取数据库中的日志文件名

        log_result = log_file_service.read_project_logs(project_id, project_name, last_position, log_file_name)
        
        return ProjectLogsResponse(
            success=log_result['success'], 
            data=log_result['data'], 
            message=log_result['message'],
            last_position=log_result.get('last_position', 0)
        )
        
    except Exception as e:
        return ProjectLogsResponse(
            success=False, 
            data=[], 
            message=f"获取项目日志失败: {str(e)}",
            last_position=0
        )


@router.get("/{project_id}/result-images")
async def get_project_result_images(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取项目的结果图片列表"""
    try:
        image_paths = result_image_service.get_project_result_images(db, project_id)
        
        return {
            "success": True,
            "message": "获取结果图片成功",
            "data": {
                "images": image_paths,
                "total_count": len(image_paths)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"获取失败: {str(e)}")


@router.delete('/{project_id}', summary='Delete project')
def delete_project_endpoint(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """删除项目"""
    try:
        # 权限检查：需要 'project:delete' 权限或管理员角色
        from service import auth_service
        if not auth_service.user_has_permission(db, current_user, 'project:delete') and not (current_user and getattr(current_user, 'role', None) and current_user.role.name in ('admin', 'project_manager')):
            raise HTTPException(status_code=403, detail='需要 project:delete 权限')
        
        result = project_service.delete_project(db, project_id)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result['message'])
        
        # 记录操作日志
        try:
            log_service.create_log(db, type='操作日志', source='项目管理', user=current_user.username if current_user else None, message=f"删除项目：ID {project_id}", level='INFO')
        except Exception:
            pass
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'删除项目失败: {str(e)}')

@router.post('/{project_id}/execute', summary='Execute project')
def execute_project_endpoint(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """执行项目"""
    try:
        # 权限检查：需要 'project:execute' 权限或项目成员角色
        from service import auth_service
        if not auth_service.user_has_permission(db, current_user, 'project:execute') and not (current_user and getattr(current_user, 'role', None) and current_user.role.name in ('admin', 'project_manager', 'tester')):
            raise HTTPException(status_code=403, detail='需要 project:execute 权限')
        
        result = project_service.execute_project(db, project_id)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result['message'])
        
        # 记录操作日志
        try:
            log_service.create_log(db, type='操作日志', source='项目管理', user=current_user.username if current_user else None, message=f"执行项目：ID {project_id}", level='INFO')
        except Exception:
            pass
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'执行项目失败: {str(e)}')