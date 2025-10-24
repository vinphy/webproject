from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship, Session

from util.db import Base, init_db


class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, index=True)
    project_code = Column(String(64), unique=True, index=True, nullable=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    project_type = Column(String(64), nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    owner = relationship('User')
    status = Column(String(32), default='待开始')
    progress = Column(Float, default=0.0)
    config = Column(Text, nullable=True)  # JSON string of config/steps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ensure table exists
init_db(Base)


def create_project(db: Session, name: str, description: str = '', owner_id: Optional[int] = None, project_code: Optional[str] = None, project_type: Optional[str] = None, config: Optional[str] = None):
    p = Project(name=name, description=description, owner_id=owner_id, project_code=project_code, project_type=project_type, config=config)
    db.add(p)
    db.flush()
    return p


def get_project_by_id(db: Session, pk: int):
    return db.query(Project).get(pk)


def list_projects(db: Session, owner_id: Optional[int] = None, limit: int = 50, offset: int = 0):
    q = db.query(Project).order_by(Project.id.desc())
    if owner_id:
        q = q.filter(Project.owner_id == owner_id)
    return q.offset(offset).limit(limit).all()
