from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.orm import Session
from util.db import Base

class TestCase(Base):
    __tablename__ = 'test_cases'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(64), default='功能测试')  # 修改：test_type -> type
    priority = Column(String(32), default='中')
    status = Column(String(32), default='草稿')
    steps = Column(Text, nullable=True)
    expected_result = Column(Text, nullable=True)
    created_by = Column(String(100), default='admin')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def create_test_case(
    db: Session, 
    name: str, 
    description: str = '', 
    type: str = '功能测试',  # 修改：test_type -> type
    priority: str = '中',
    status: str = '草稿',
    steps: Optional[List[dict]] = None,
    expected_result: str = '',
    created_by: str = 'admin'
):
    """创建测试用例"""
    steps_json = None
    if steps:
        import json
        steps_json = json.dumps(steps, ensure_ascii=False)
    
    test_case = TestCase(
        name=name,
        description=description,
        type=type,  # 修改：test_type -> type
        priority=priority,
        status=status,
        steps=steps_json,
        expected_result=expected_result,
        created_by=created_by
    )
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    return test_case

def get_test_case_by_id(db: Session, test_case_id: int):
    """根据ID获取测试用例"""
    return db.query(TestCase).filter(TestCase.id == test_case_id).first()

def list_test_cases(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    search: str = None,
    type: str = None,  # 修改：test_type -> type
    status: str = None
):
    """获取测试用例列表"""
    query = db.query(TestCase)
    
    if search:
        query = query.filter(TestCase.name.contains(search) | TestCase.description.contains(search))
    
    if type:  # 修改：test_type -> type
        query = query.filter(TestCase.type == type)  # 修改：test_type -> type
    
    if status:
        query = query.filter(TestCase.status == status)
    
    return query.order_by(TestCase.id.desc()).offset(skip).limit(limit).all()

def count_test_cases(
    db: Session,
    search: str = None,
    type: str = None,  # 修改：test_type -> type
    status: str = None
):
    """统计测试用例数量"""
    query = db.query(TestCase)
    
    if search:
        query = query.filter(TestCase.name.contains(search) | TestCase.description.contains(search))
    
    if type:  # 修改：test_type -> type
        query = query.filter(TestCase.type == type)  # 修改：test_type -> type
    
    if status:
        query = query.filter(TestCase.status == status)
    
    return query.count()

def update_test_case(
    db: Session, 
    test_case_id: int,
    name: str = None,
    description: str = None,
    type: str = None,  # 修改：test_type -> type
    priority: str = None,
    status: str = None,
    steps: Optional[List[dict]] = None,
    expected_result: str = None
):
    """更新测试用例"""
    test_case = get_test_case_by_id(db, test_case_id)
    if not test_case:
        return None
    
    if name is not None:
        test_case.name = name
    if description is not None:
        test_case.description = description
    if type is not None:  # 修改：test_type -> type
        test_case.type = type  # 修改：test_type -> type
    if priority is not None:
        test_case.priority = priority
    if status is not None:
        test_case.status = status
    if expected_result is not None:
        test_case.expected_result = expected_result
    if steps is not None:
        import json
        test_case.steps = json.dumps(steps, ensure_ascii=False)
    
    test_case.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(test_case)
    return test_case

def delete_test_case(db: Session, test_case_id: int):
    """删除测试用例"""
    test_case = get_test_case_by_id(db, test_case_id)
    if test_case:
        db.delete(test_case)
        db.commit()
        return True
    return False