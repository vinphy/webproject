from typing import List, Dict
from sqlalchemy.orm import Session
from models.auth_model import get_user_by_id
from models.home_model import get_recent_projects


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
        'createdProjectsCount': 0,  # fallback
        'projects': []
    }

    # try to fetch recent projects (best effort)
    try:
        projects = get_recent_projects(limit=5)
        profile['projects'] = projects
        profile['createdProjectsCount'] = len(projects)
    except Exception:
        # keep best-effort behavior — don't fail entire request if project query errors
        profile['projects'] = []

    return profile
