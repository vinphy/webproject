from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from models.test_case_model import TestCaseModel
from util.db import get_db

class TestCaseService:
    def __init__(self, db: Session):
        self.db = db
        self.test_case_model = TestCaseModel(db)
    
    def create_test_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建测试用例服务"""
        try:
            return self.test_case_model.create_test_case(case_data)
        except Exception as e:
            raise Exception(f"创建测试用例失败: {str(e)}")
    
    def get_test_case_list(self, page: int = 1, size: int = 10, search: str = None, status: str = None) -> Dict[str, Any]:
        """获取测试用例列表服务"""
        try:
            return self.test_case_model.get_test_case_list(page, size, search, status)
        except Exception as e:
            raise Exception(f"获取测试用例列表失败: {str(e)}")
    
    def get_test_case_detail(self, case_id: int) -> Optional[Dict[str, Any]]:
        """获取测试用例详情服务"""
        try:
            return self.test_case_model.get_test_case_by_id(case_id)
        except Exception as e:
            raise Exception(f"获取测试用例详情失败: {str(e)}")
    
    def update_test_case(self, case_id: int, update_data: Dict[str, Any]) -> bool:
        """更新测试用例服务"""
        try:
            return self.test_case_model.update_test_case(case_id, update_data)
        except Exception as e:
            raise Exception(f"更新测试用例失败: {str(e)}")
    
    def delete_test_case(self, case_id: int) -> bool:
        """删除测试用例服务"""
        try:
            return self.test_case_model.delete_test_case(case_id)
        except Exception as e:
            raise Exception(f"删除测试用例失败: {str(e)}")

# 创建全局实例
test_case_service = TestCaseService()