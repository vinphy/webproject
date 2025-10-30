from typing import Dict, Any
from sqlalchemy.orm import Session
from models import project_model
import json


def create_project(db: Session, owner_id: int, payload: Dict[str, Any]):
    """Business logic for creating a project.
    payload expected keys: projectCode, projectName, projectType, testLeader, startDate, endDate, projectDesc, teamMembers, selectedTestCaseIds, projectParams, step2Selections
    """
    # basic validation
    name = payload.get('projectName') or payload.get('name')
    if not name:
        raise ValueError('项目名称不能为空')

    project_code = payload.get('projectCode')
    description = payload.get('projectDesc') or payload.get('description') or ''
    project_type = payload.get('projectType')

    # store config as JSON string to keep flexible
    import json
    config = json.dumps({
        'form': {k: payload.get(k) for k in ['projectCode','projectName','projectType','testLeader','startDate','endDate','projectDesc']},
        'teamMembers': payload.get('teamMembers', []),
        'selectedTestCaseIds': payload.get('selectedTestCaseIds', []),
        'projectParams': payload.get('projectParams', {}),
        'step2Selections': payload.get('step2Selections', {})
    }, ensure_ascii=False)

    p = project_model.create_project(db, name=name, description=description, owner_id=owner_id, project_code=project_code, project_type=project_type, config=config)
    db.commit()
    db.refresh(p)
    return p


def list_projects(db: Session, owner_id: int = None, limit: int = 50, offset: int = 0):
    """Return dict with items (parsed) and accurate total count."""
    rows = project_model.list_projects(db, owner_id=owner_id, limit=limit, offset=offset)
    results = []
    for r in rows:
        item = {
            'id': r.id,
            'project_code': r.project_code,
            'name': r.name,
            'description': r.description,
            'project_type': r.project_type,
            'owner_id': r.owner_id,
            'status': r.status,
            'progress': float(r.progress) if r.progress is not None else 0,
            'created_at': r.created_at.isoformat() if r.created_at else None,
            'updated_at': r.updated_at.isoformat() if r.updated_at else None,
            # compatibility with frontend which expects createTime
            'createTime': r.created_at.strftime('%Y-%m-%d %H:%M:%S') if r.created_at else None,
            'config': {}
        }
        try:
            item['config'] = json.loads(r.config) if r.config else {}
        except Exception:
            item['config'] = {}
        results.append(item)

    total = project_model.count_projects(db, owner_id=owner_id)
    return { 'items': results, 'total': int(total) }


def get_project_detail(db: Session, project_id: int):
    """获取项目详情服务函数"""
    try:
        project_detail = project_model.get_project_detail(db, project_id)
        if not project_detail:
            return {
                'success': False,
                'message': '项目不存在',
                'data': None
            }
        
        return {
            'success': True,
            'message': '获取项目详情成功',
            'data': project_detail
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'获取项目详情失败: {str(e)}',
            'data': None
        }