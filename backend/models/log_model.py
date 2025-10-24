from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Text, func
from sqlalchemy.orm import Session

from util.db import Base, init_db


class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String(50), index=True, nullable=False)
    source = Column(String(200), nullable=True)
    user = Column(String(200), nullable=True)
    message = Column(Text, nullable=True)
    level = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# ensure table exists
init_db(Base)


def create_log(db: Session, type: str, source: Optional[str] = None, user: Optional[str] = None, message: Optional[str] = None, level: Optional[str] = None):
    l = Log(type=type, source=source, user=user, message=message, level=level)
    db.add(l)
    db.commit()
    db.refresh(l)
    return l


def build_query(db: Session, type: Optional[str] = None, keyword: Optional[str] = None, startDate: Optional[str] = None, endDate: Optional[str] = None):
    q = db.query(Log)
    if type:
        q = q.filter(Log.type == type)
    if keyword:
        like = f"%{keyword}%"
        q = q.filter((Log.message.ilike(like)) | (Log.source.ilike(like)) | (Log.user.ilike(like)))
    if startDate:
        from datetime import datetime
        try:
            start_dt = datetime.strptime(startDate + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
            q = q.filter(Log.created_at >= start_dt)
        except Exception:
            pass
    if endDate:
        from datetime import datetime
        try:
            end_dt = datetime.strptime(endDate + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            q = q.filter(Log.created_at <= end_dt)
        except Exception:
            pass
    return q


def list_logs(db: Session, page: int = 1, size: int = 10, type: Optional[str] = None, keyword: Optional[str] = None, startDate: Optional[str] = None, endDate: Optional[str] = None):
    q = build_query(db, type=type, keyword=keyword, startDate=startDate, endDate=endDate)
    total = q.count()
    items = q.order_by(Log.created_at.desc()).offset((page - 1) * size).limit(size).all()
    return items, int(total)


def get_log(db: Session, log_id: int):
    return db.query(Log).filter(Log.id == log_id).first()
