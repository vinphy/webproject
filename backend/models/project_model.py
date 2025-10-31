from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, func, Enum
from sqlalchemy.orm import relationship, Session

from util.db import Base, init_db

from sqlalchemy.ext.declarative import declarative_base
import enum


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


def count_projects(db: Session, owner_id: Optional[int] = None):
    q = db.query(func.count(Project.id))
    if owner_id:
        q = q.filter(Project.owner_id == owner_id)
    return q.scalar() or 0


# 新增项目统计相关函数
def get_project_stats(db: Session, owner_id: Optional[int] = None):
    """获取项目统计信息"""
    # 项目总数
    total_count = count_projects(db, owner_id)
    
    # 按状态统计
    status_stats = {}
    if owner_id:
        status_query = db.query(Project.status, func.count(Project.id)).filter(Project.owner_id == owner_id).group_by(Project.status).all()
    else:
        status_query = db.query(Project.status, func.count(Project.id)).group_by(Project.status).all()
    
    for status, count in status_query:
        status_stats[status] = count
    
    # 按进度统计
    progress_stats = {
        'not_started': db.query(func.count(Project.id)).filter(Project.progress == 0).scalar() or 0,
        'in_progress': db.query(func.count(Project.id)).filter(Project.progress > 0, Project.progress < 100).scalar() or 0,
        'completed': db.query(func.count(Project.id)).filter(Project.progress == 100).scalar() or 0
    }
    
    # 最近创建的项目数量（最近7天）
    seven_days_ago = datetime.utcnow() - datetime.timedelta(days=7)
    recent_count = db.query(func.count(Project.id)).filter(Project.created_at >= seven_days_ago)
    if owner_id:
        recent_count = recent_count.filter(Project.owner_id == owner_id)
    recent_count = recent_count.scalar() or 0
    
    return {
        'total': total_count,
        'status_stats': status_stats,
        'progress_stats': progress_stats,
        'recent_count': recent_count
    }


def get_recent_projects(db: Session, owner_id: Optional[int] = None, limit: int = 5):
    """获取最近的项目列表"""
    q = db.query(Project).order_by(Project.created_at.desc())
    if owner_id:
        q = q.filter(Project.owner_id == owner_id)
    return q.limit(limit).all()


def get_project_detail(db: Session, project_id: int):
    """获取项目详细信息，包含关联的用户信息和config数据"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None
    
    # 基础项目信息
    project_detail = {
        'id': project.id,
        'project_code': project.project_code,
        'name': project.name,
        'description': project.description,
        'project_type': project.project_type,
        'status': project.status,
        'progress': project.progress,
        'created_at': project.created_at,
        'updated_at': project.updated_at,
        'owner_name': project.owner.username if project.owner else None,
        'owner_id': project.owner_id,
        'config': project.config  # 添加config字段
    }
    
    return project_detail