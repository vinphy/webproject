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

    # 自动生成日志文件名
    log_file_name = None
    if project_code:
        log_file_name = f"{project_code}.log"
    else:
        # 使用项目名称生成安全的文件名
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        log_file_name = f"{safe_name}.log"


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
        
        # 获取项目完整信息，包括config
        project = project_model.get_project_by_id(db, project_id)
        if project and project.config:
            try:
                config_data = json.loads(project.config)
                # 解析config中的form数据
                form_data = config_data.get('form', {})
                project_detail.update({
                    'test_leader': form_data.get('testLeader'),
                    'start_date': form_data.get('startDate'),
                    'end_date': form_data.get('endDate'),
                    'priority': form_data.get('priority', '中'),  # 默认优先级为中
                    'execution_items': config_data.get('step2Selections', {}).get('selectedItems', []) , # 执行项
                    'step2Selections': config_data.get('step2Selections', {})   #vuln漏洞扫描； fuzz模糊测试；cases测试用例
                })
                # print('项目详情')
                # print(config_data.get('step2Selections', {}))
                # print(project_detail)
            except Exception as e:
                print(f"解析config失败: {e}")
        
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


def delete_project(db: Session, project_id: int):
    """删除项目"""
    try:
        project = project_model.get_project_by_id(db, project_id)
        if not project:
            return {
                'success': False,
                'message': '项目不存在'
            }
        
        # 删除项目记录
        db.delete(project)
        db.commit()
        
        return {
            'success': True,
            'message': '项目删除成功'
        }
    except Exception as e:
        db.rollback()
        return {
            'success': False,
            'message': f'删除项目失败: {str(e)}'
        }

def execute_project(db: Session, project_id: int):
    """执行单个项目（预留空接口）"""
    try:
        project = get_project_by_id(db, project_id)
        if not project:
            return {
                'success': False,
                'message': '项目不存在'
            }
        
        # 这里预留执行项目的逻辑，目前只返回成功消息
        # 实际执行逻辑可以根据项目类型和配置来实现
        print(f"执行项目 {project_id}")
        return {
            'success': True,
            'message': '项目执行命令已发送',
            'data': {
                'project_id': project_id,
                'name': project.name,
                'status': '执行中'
            }
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'执行项目失败: {str(e)}'
        }

def get_project_by_id(db: Session, project_id: int):
    """获取项目对象（供批量执行使用）"""
    from models.project_model import get_project_by_id as model_get_project_by_id
    return model_get_project_by_id(db, project_id)