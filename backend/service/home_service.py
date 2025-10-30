from typing import List, Dict
from sqlalchemy.orm import Session
from models.auth_model import get_user_by_id
from models.home_model import get_recent_projects, get_project_stats as get_project_stats_model


def get_home_profile(db: Session, user_id: int) -> Dict:
    """Compose profile for home page: user basic info + recent projects."""
    user = get_user_by_id(db, user_id)
    if not user:
        return {}
    
    profile = {
        'id': user.id,
        'name': user.username,
        'email': user.email,
        'role': user.role.name if user.role else None,
        'createdProjectsCount': 0,
        'projects': []
    }

    # 获取最近项目
    try:
        projects = get_recent_projects(db, user_id, limit=5)
        profile['projects'] = projects
        profile['createdProjectsCount'] = len(projects)
    except Exception:
        # 保持最佳实践 - 如果项目查询出错，不使整个请求失败
        profile['projects'] = []

    return profile


def get_project_stats(db: Session, user_id: int) -> Dict:
    """获取项目执行进度统计数据"""
    try:
        stats = get_project_stats_model(db, user_id)
        return stats
    except Exception as e:
        # 如果获取失败，返回默认数据
        return {
            'total': 0,
            'completed': 0,
            'inProgress': 0,
            'pending': 0,
            'status_stats': {},
            'progress_stats': {
                'not_started': 0,
                'in_progress': 0,
                'completed': 0
            },
            'recent_count': 0
        }


def get_monthly_project_stats(db: Session, user_id: int, months: int = 12) -> Dict:
    """获取项目月度统计数据"""
    try:
        from models.home_model import get_monthly_project_stats as get_monthly_stats_model
        stats = get_monthly_stats_model(db, user_id, months)
        
        # 添加调试信息
        print(f"用户 {user_id} 的月度统计数据: {stats}")
        
        return {
            'success': True,
            'data': stats,
            'total_months': len(stats),
            'user_id': user_id
        }
    except Exception as e:
        # 添加错误调试信息
        print(f"获取月度统计数据失败 - 用户 {user_id}: {str(e)}")
        
        # 如果获取失败，返回默认数据（全部为0）
        return {
            'success': False,
            'error': str(e),
            'data': [],
            'total_months': 0,
            'user_id': user_id
        }