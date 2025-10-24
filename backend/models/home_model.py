from typing import List, Dict
from sqlalchemy import text
from util.db import engine


def get_recent_projects(limit: int = 5) -> List[Dict]:
    """Return recent projects from pms_sca table as list of dicts.
    Uses SQLAlchemy engine and text to avoid duplicating connection code.
    """
    sql = text(
        """
        SELECT id, item as projectName, project_type as type, status as result, info as description, created_at
        FROM pms_sca
        ORDER BY id DESC
        LIMIT :limit
        """
    )
    conn = engine.connect()
    try:
        res = conn.execute(sql, {"limit": limit})
        rows = [dict(r) for r in res.fetchall()]
        return rows
    finally:
        conn.close()
