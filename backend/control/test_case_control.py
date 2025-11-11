from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from util.db import get_db
from control.auth import get_current_user
from models.auth_model import User
from service.test_case_service import TestCaseService

router = APIRouter()

# 测试用例创建请求模型
class TestCaseCreatePayload(BaseModel):
    name: str
    description: Optional[str] = None
    test_type: Optional[str] = "功能测试"
    priority: Optional[str] = "中"
    steps: Optional[List[dict]] = None
    expected_result: Optional[str] = None

# 测试用例更新请求模型
class TestCaseUpdatePayload(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    test_type: Optional[str] = None
    priority: Optional[str] = None
    steps: Optional[List[dict]] = None
    expected_result: Optional[str] = None
    status: Optional[str] = None

@router.get("/")
async def get_test_cases(
    page: int = 1, 
    size: int = 10,
    search: Optional[str] = None,
    test_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    
    """获取测试用例列表"""
    try:
        print(f'进入到了测试用例后台1 - 参数: page={page}, size={size}, search={search}, test_type={test_type}, status={status}')
        
        # 添加调试日志，检查服务层调用
        print(f'开始调用 TestCaseService.get_test_case_list()')
        result = TestCaseService.get_test_case_list(
            db=db,
            page=page,
            size=size,
            search=search,
            type=test_type,
            status=status
        )
        print(f'TestCaseService.get_test_case_list() 调用完成，结果: {result}')
        
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['message'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取测试用例列表失败: {str(e)}")

@router.get("/{test_case_id}")
async def get_test_case_detail(
    test_case_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """获取测试用例详情"""
    try:
        result = TestCaseService.get_test_case_detail(db, test_case_id)
        
        if result['status'] == 'error':
            raise HTTPException(status_code=404, detail=result['message'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取测试用例详情失败: {str(e)}")

@router.post("/")
async def create_test_case(
    payload: TestCaseCreatePayload, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """创建测试用例"""
    try:
        result = TestCaseService.create_test_case(
            db=db,
            name=payload.name,
            description=payload.description,
            type=payload.test_type,
            priority=payload.priority,
            steps=payload.steps,
            expected_result=payload.expected_result,
            created_by=current_user.username if current_user else 'admin'
        )
        
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['message'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建测试用例失败: {str(e)}")

@router.put("/{test_case_id}")
async def update_test_case(
    test_case_id: int,
    payload: TestCaseUpdatePayload, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """更新测试用例"""
    try:
        result = TestCaseService.update_test_case(
            db=db,
            test_case_id=test_case_id,
            name=payload.name,
            description=payload.description,
            type=payload.test_type,
            priority=payload.priority,
            status=payload.status,
            steps=payload.steps,
            expected_result=payload.expected_result
        )
        
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['message'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新测试用例失败: {str(e)}")

@router.delete("/{test_case_id}")
async def delete_test_case(
    test_case_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """删除测试用例"""
    try:
        result = TestCaseService.delete_test_case(db, test_case_id)
        
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['message'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除测试用例失败: {str(e)}")

@router.post("/batch-execute")
async def batch_execute_test_cases(
    test_case_ids: List[int], 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """批量执行测试用例（待实现）"""
    try:
        # 暂时返回成功响应，待后续实现具体逻辑
        return {
            'status': 'success',
            'message': '测试用例批量执行功能待实现',
            'data': {
                'executed_count': 0,
                'success_count': 0,
                'failed_count': 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量执行测试用例失败: {str(e)}")