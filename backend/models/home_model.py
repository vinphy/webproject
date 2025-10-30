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
    """获取用户项目月度统计数据 - 优化版本：统计当前月份往前倒推12个月"""
    from sqlalchemy import extract
    
    # 获取当前日期
    current_date = datetime.datetime.utcnow()
    current_year = current_date.year
    current_month = current_date.month
    
    # 计算起始日期（当前月份往前推months个月）
    # 更精确的日期计算，避免近似误差
    start_date = current_date.replace(day=1)  # 当前月的第一天
    for _ in range(months):
        # 往前推一个月
        if start_date.month == 1:
            start_date = start_date.replace(year=start_date.year-1, month=12)
        else:
            start_date = start_date.replace(month=start_date.month-1)
    
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
    
    # 生成完整的月份列表（从最早月份到当前月份）
    complete_stats = []
    
    # 生成月份列表：从起始月份到当前月份
    temp_date = start_date.replace(day=1)
    while temp_date <= current_date.replace(day=1):
        target_year = temp_date.year
        target_month = temp_date.month
        
        # 查找对应的统计数据
        found_stat = None
        for stat in result:
            if stat['year'] == target_year and stat['month'] == target_month:
                found_stat = stat
                break
        
        if found_stat:
            complete_stats.append(found_stat)
        else:
            # 如果没有找到，添加0计数
            complete_stats.append({
                'year': target_year,
                'month': target_month,
                'count': 0,
                'label': f"{target_year}-{target_month:02d}"
            })
        
        # 移动到下一个月
        if temp_date.month == 12:
            temp_date = temp_date.replace(year=temp_date.year+1, month=1)
        else:
            temp_date = temp_date.replace(month=temp_date.month+1)
    
    # 确保只返回最近的months个月数据（如果生成的月份超过months，取最后months个）
    if len(complete_stats) > months:
        complete_stats = complete_stats[-months:]
    
    return complete_stats


def get_current_testing_projects(db: Session, user_id: int, limit: int = 10) -> List[Dict]:
    """获取当前正在测试的项目数据"""
    # 查询用户的所有项目，按项目编号升序排列，限制数量
    projects = db.query(Project).filter(
        Project.owner_id == user_id
    ).order_by(Project.id.asc()).limit(limit).all()
    
    results = []
    for project in projects:
        # 将状态映射为前端需要的格式
        status_mapping = {
            '已完成': 'completed',
            '进行中': 'in-progress', 
            '测试中': 'in-progress',
            '待开始': 'not-started',
            '暂停': 'not-started'
        }
        
        frontend_status = status_mapping.get(project.status, 'not-started')
        
        results.append({
            'id': project.id,
            'projectCode': project.project_code or f"PROJ-{project.id:06d}",
            'progress': float(project.progress) if project.progress is not None else 0.0,
            'status': frontend_status,
            'name': project.name,
            'created_at': project.created_at.isoformat() if project.created_at else None
        })
    
    return results