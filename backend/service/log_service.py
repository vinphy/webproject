from typing import Optional
from sqlalchemy.orm import Session
from models import log_model


def create_log(db: Session, type: str, source: Optional[str] = None, user: Optional[str] = None, message: Optional[str] = None, level: Optional[str] = None):
    return log_model.create_log(db, type=type, source=source, user=user, message=message, level=level)


def list_logs(db: Session, page: int = 1, size: int = 10, type: Optional[str] = None, keyword: Optional[str] = None, startDate: Optional[str] = None, endDate: Optional[str] = None):
    items, total = log_model.list_logs(db, page=page, size=size, type=type, keyword=keyword, startDate=startDate, endDate=endDate)
    # convert ORM to dicts suitable for pydantic/JSON
    out = []
    for r in items:
        out.append({
            'id': r.id,
            'type': r.type,
            'source': r.source,
            'user': r.user,
            'message': r.message,
            'level': r.level,
            'created_at': r.created_at.isoformat() if r.created_at else None,
        })
    return { 'items': out, 'total': total }


def get_log(db: Session, log_id: int):
    r = log_model.get_log(db, log_id)
    if not r:
        return None
    return {
        'id': r.id,
        'type': r.type,
        'source': r.source,
        'user': r.user,
        'message': r.message,
        'level': r.level,
        'created_at': r.created_at.isoformat() if r.created_at else None,
    }
