from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models.project_model import Project
import datetime


def get_recent_projects(db: Session, user_id: int, limit: int = 5) -> List[Dict]:
    """获取最近的项目"""
    projects = db.query(Project).filter(
        Project.owner_id == user_id
    ).order_by(Project.created_at.desc()).limit(limit).all()
    
    results = []
    for project in projects:
        results.append({
            'id': project.id,
            'name': project.name,
            'project_code': project.project_code,
            'status': project.status,
            'progress': float(project.progress) if project.progress is not None else 0,
            'created_at': project.created_at.isoformat() if project.created_at else None,
            'createTime': project.created_at.strftime('%Y-%m-%d %H:%M:%S') if project.created_at else None
        })
    
    return results


def get_project_stats(db: Session, user_id: int) -> Dict:
    """获取项目执行进度统计数据"""
    # 统计项目总数
    total_count = db.query(func.count(Project.id)).filter(
        Project.owner_id == user_id
    ).scalar() or 0

    # 按状态统计项目数量
    status_stats = {}
    status_query = db.query(Project.status, func.count(Project.id)).filter(
        Project.owner_id == user_id
    ).group_by(Project.status).all()
    
    for status, count in status_query:
        status_stats[status] = count

    # 按进度统计（仅作为参考，不用于主要统计）
    progress_stats = {
        'not_started': db.query(func.count(Project.id)).filter(
            and_(Project.owner_id == user_id, Project.progress == 0)
        ).scalar() or 0,
        'in_progress': db.query(func.count(Project.id)).filter(
            and_(Project.owner_id == user_id, Project.progress > 0, Project.progress < 100)
        ).scalar() or 0,
        'completed': db.query(func.count(Project.id)).filter(
            and_(Project.owner_id == user_id, Project.progress == 100)
        ).scalar() or 0
    }

    # 最近7天创建的项目数量
    seven_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    recent_count = db.query(func.count(Project.id)).filter(
        and_(Project.owner_id == user_id, Project.created_at >= seven_days_ago)
    ).scalar() or 0

    # 确保统计数据一致性：主要使用状态统计，进度统计作为参考
    completed_count = status_stats.get('已完成', 0)
    in_progress_count = status_stats.get('进行中', 0) + status_stats.get('测试中', 0)
    pending_count = status_stats.get('待开始', 0) + status_stats.get('暂停', 0)
    
    # 验证总数一致性
    calculated_total = completed_count + in_progress_count + pending_count
    if calculated_total != total_count:
        # 如果统计不一致，使用状态统计的总数
        total_count = calculated_total

    return {
        'total': total_count,
        'completed': completed_count,
        'inProgress': in_progress_count,
        'pending': pending_count,
        'status_stats': status_stats,
        'progress_stats': progress_stats,
        'recent_count': recent_count
    }


def get_monthly_project_stats(db: Session, user_id: int, months: int = 12) -> List[Dict]:
    """获取用户项目月度统计数据"""
    from sqlalchemy import extract
    
    # 计算起始日期（当前日期往前推months个月）
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(days=months*30)  # 近似计算
    
    # 按月统计项目创建数量
    monthly_stats = db.query(
        extract('year', Project.created_at).label('year'),
        extract('month', Project.created_at).label('month'),
        func.count(Project.id).label('count')
    ).filter(
        Project.owner_id == user_id,
        Project.created_at >= start_date
    ).group_by(
        extract('year', Project.created_at),
        extract('month', Project.created_at)
    ).order_by(
        extract('year', Project.created_at).desc(),
        extract('month', Project.created_at).desc()
    ).all()
    
    # 格式化返回数据
    result = []
    for stat in monthly_stats:
        result.append({
            'year': int(stat.year),
            'month': int(stat.month),
            'count': stat.count,
            'label': f"{int(stat.year)}-{int(stat.month):02d}"
        })
    
    # 确保返回最近months个月的数据，即使某个月没有项目也返回0
    current_year = end_date.year
    current_month = end_date.month
    
    # 生成完整的月份列表（按时间顺序从早到晚）
    complete_stats = []
    for i in range(months-1, -1, -1):  # 从最早月份开始
        # 计算月份
        target_month = current_month - i
        target_year = current_year
        
        if target_month <= 0:
            target_month += 12
            target_year -= 1
        
        # 查找对应的统计数据
        found = False
        for stat in result:
            if stat['year'] == target_year and stat['month'] == target_month:
                complete_stats.append(stat)
                found = True
                break
        
        # 如果没有找到，添加0计数
        if not found:
            complete_stats.append({
                'year': target_year,
                'month': target_month,
                'count': 0,
                'label': f"{target_year}-{target_month:02d}"
            })
    
    return complete_stats