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
from service.log_file_service import log_file_service

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
    current_user: auth_model.User = Depends(get_current_user)   
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

        #2. 构建日志文件路径（假设C程序生成到固定目录）
        # log_dir = os.path.join(os.getcwd(), 'logs', 'projects')
        # log_file_path = os.path.join(log_dir, f'{project_name}_{project_id}.log')

        #3. 如果日志文件不存在，返回空数据
        # if not os.path.exists(log_file_path):
        #     return ProjectLogsResponse(
        #         success=True, 
        #         data=[], 
        #         message="日志文件不存在",
        #         last_position=0
        #     )
        
        # #4. 读取日志文件
        # logs = []
        # current_position = 0
        
        # try:
        #     with open(log_file_path, 'r', encoding='utf-8') as f:
        #         # 如果指定了上次位置，则跳转到该位置
        #         if last_position > 0:
        #             f.seek(last_position)
                
        #         # 读取新内容
        #         new_logs = f.readlines()
        #         current_position = f.tell()  # 获取当前读取位置
                
        #         #处理日志内容
        #         for line in new_logs:
        #             line = line.strip()
        #             if line:  # 跳过空行
        #                 logs.append(line)
                        
        # except Exception as e:
        #     return ProjectLogsResponse(
        #         success=False, 
        #         data=[], 
        #         message=f"读取日志文件失败: {str(e)}",
        #         last_position=last_position
        #     )

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
