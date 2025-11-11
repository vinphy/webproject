from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.orm import Session
from util.db import Base, init_db

class TestCase(Base):
    __tablename__ = 'test_cases'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(50))
    status = Column(String(20), default='草稿')
    priority = Column(String(20), default='中')
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    config = Column(JSON)
    tags = Column(JSON)
    is_deleted = Column(Boolean, default=False)

class TestCaseModel:
    def __init__(self, db: Session):
        self.db = db
    
    def create_test_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建测试用例"""
        try:
            test_case = TestCase(**case_data)
            self.db.add(test_case)
            self.db.commit()
            self.db.refresh(test_case)
            return {
                'id': test_case.id,
                'name': test_case.name,
                'description': test_case.description,
                'type': test_case.type,
                'status': test_case.status,
                'priority': test_case.priority,
                'created_by': test_case.created_by,
                'created_at': test_case.created_at,
                'updated_at': test_case.updated_at
            }
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_test_case_list(self, page: int = 1, size: int = 10, search: str = None, status: str = None) -> Dict[str, Any]:
        """获取测试用例列表（分页）"""
        try:
            query = self.db.query(TestCase).filter(TestCase.is_deleted == False)
            
            if search:
                query = query.filter(
                    (TestCase.name.like(f'%{search}%')) | 
                    (TestCase.description.like(f'%{search}%'))
                )
            
            if status:
                query = query.filter(TestCase.status == status)
            
            total = query.count()
            offset = (page - 1) * size
            cases = query.order_by(TestCase.updated_at.desc()).offset(offset).limit(size).all()
            
            return {
                'items': [
                    {
                        'id': case.id,
                        'name': case.name,
                        'description': case.description,
                        'type': case.type,
                        'status': case.status,
                        'priority': case.priority,
                        'created_by': case.created_by,
                        'created_at': case.created_at.isoformat() if case.created_at else None,
                        'updated_at': case.updated_at.isoformat() if case.updated_at else None
                    }
                    for case in cases
                ],
                'total': total,
                'page': page,
                'size': size
            }
        except Exception as e:
            raise e
    
    def get_test_case_by_id(self, case_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取测试用例详情"""
        try:
            case = self.db.query(TestCase).filter(TestCase.id == case_id, TestCase.is_deleted == False).first()
            if case:
                return {
                    'id': case.id,
                    'name': case.name,
                    'description': case.description,
                    'type': case.type,
                    'status': case.status,
                    'priority': case.priority,
                    'created_by': case.created_by,
                    'config': case.config,
                    'tags': case.tags,
                    'created_at': case.created_at.isoformat() if case.created_at else None,
                    'updated_at': case.updated_at.isoformat() if case.updated_at else None
                }
            return None
        except Exception as e:
            raise e
    
    def update_test_case(self, case_id: int, update_data: Dict[str, Any]) -> bool:
        """更新测试用例"""
        try:
            case = self.db.query(TestCase).filter(TestCase.id == case_id, TestCase.is_deleted == False).first()
            if case:
                for key, value in update_data.items():
                    setattr(case, key, value)
                case.updated_at = datetime.now()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete_test_case(self, case_id: int) -> bool:
        """软删除测试用例"""
        try:
            case = self.db.query(TestCase).filter(TestCase.id == case_id, TestCase.is_deleted == False).first()
            if case:
                case.is_deleted = True
                case.updated_at = datetime.now()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise e