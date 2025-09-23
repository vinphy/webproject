from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Text, desc, and_

from util.db import Base, get_db, init_db

router = APIRouter()

# SQLAlchemy Model
class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String(20), index=True, nullable=False)  # 操作日志/运行日志/异常日志/正常日志
    source = Column(String(100), nullable=True)
    user = Column(String(100), nullable=True)
    message = Column(Text, nullable=True)
    level = Column(String(20), nullable=True)  # 可选：INFO/WARN/ERROR
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

# Ensure table exists
init_db(Base)

# Pydantic Schemas
class LogOut(BaseModel):
    id: int
    type: str
    source: Optional[str] = None
    user: Optional[str] = None
    message: Optional[str] = None
    level: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class LogListOut(BaseModel):
    items: List[LogOut]
    total: int


@router.get("/list", response_model=LogListOut)
def list_logs(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=200),
    type: str = Query("", description="日志类型：操作日志/运行日志/异常日志/正常日志，可为空"),
    keyword: str = Query("", description="关键字，匹配 message/source/user"),
    startDate: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    endDate: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    try:
        q = db.query(Log)
        if type:
            q = q.filter(Log.type == type)
        if keyword:
            like = f"%{keyword}%"
            q = q.filter(
                (Log.message.ilike(like)) | (Log.source.ilike(like)) | (Log.user.ilike(like))
            )
        if startDate:
            try:
                start_dt = datetime.strptime(startDate + " 00:00:00", "%Y-%m-%d %H:%M:%S")
                q = q.filter(Log.created_at >= start_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="startDate 格式应为 YYYY-MM-DD")
        if endDate:
            try:
                end_dt = datetime.strptime(endDate + " 23:59:59", "%Y-%m-%d %H:%M:%S")
                q = q.filter(Log.created_at <= end_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="endDate 格式应为 YYYY-MM-DD")

        total = q.count()
        items = (
            q.order_by(desc(Log.created_at))
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        print('--------打印日志结果-----')

        print(items)
        return {"items": items, "total": total}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{log_id}", response_model=LogOut)
def get_log(log_id: int, db: Session = Depends(get_db)):
    item = db.query(Log).filter(Log.id == log_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="日志不存在")
    return item


# 可选：初始化一些示例数据
@router.post("/seed")
def seed_logs(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    demo = [
        Log(type="操作日志", source="项目管理", user="admin", message="创建项目：智能测试平台", level="INFO", created_at=now),
        Log(type="运行日志", source="任务调度", user="system", message="开始执行漏洞扫描任务#42", level="INFO", created_at=now),
        Log(type="异常日志", source="接口服务", user="system", message="请求超时：/api/run/start 504", level="ERROR", created_at=now),
        Log(type="正常日志", source="监控服务", user="system", message="CPU使用率 35%，内存 62%", level="INFO", created_at=now),
        Log(type="操作日志", source="用例管理", user="tester", message="更新测试用例：登录功能-正向", level="INFO", created_at=now),
    ]
    for d in demo:
        db.add(d)
    db.commit()
    return {"status": "success", "inserted": len(demo)} 