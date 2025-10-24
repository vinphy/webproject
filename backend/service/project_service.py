from typing import Dict, Any
from sqlalchemy.orm import Session
from models import project_model


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
