from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models.test_case_model import (
    create_test_case, get_test_case_by_id, list_test_cases, 
    count_test_cases, update_test_case, delete_test_case
)

class TestCaseService:
    """测试用例服务类"""
    
    @staticmethod
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
    ) -> Dict[str, Any]:
        """创建测试用例"""
        try:
            test_case = create_test_case(
                db=db,
                name=name,
                description=description,
                type=type,  # 修改：test_type -> type
                priority=priority,
                status=status,
                steps=steps,
                expected_result=expected_result,
                created_by=created_by
            )
            
            return {
                'status': 'success',
                'data': {
                    'id': test_case.id,
                    'name': test_case.name,
                    'description': test_case.description,
                    'type': test_case.type,  # 修改：test_type -> type
                    'priority': test_case.priority,
                    'status': test_case.status,
                    'created_by': test_case.created_by,
                    'created_at': test_case.created_at.isoformat() if test_case.created_at else None
                },
                'message': '测试用例创建成功'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'创建测试用例失败: {str(e)}'
            }
    
    @staticmethod
    def get_test_case_list(
        db: Session,
        page: int = 1,
        size: int = 10,
        search: str = None,
        type: str = None,  # 修改：test_type -> type
        status: str = None
    ) -> Dict[str, Any]:
        """获取测试用例列表"""
        try:
            print(f'进入 TestCaseService.get_test_case_list() - 参数: page={page}, size={size}, search={search}, type={type}, status={status}')  # 修改：test_type -> type
            
            skip = (page - 1) * size
            print(f'计算skip: {skip}')
            
            # 调用模型层函数
            print(f'开始调用 list_test_cases()')
            test_cases = list_test_cases(
                db=db,
                skip=skip,
                limit=size,
                search=search,
                type=type,  # 修改：test_type -> type
                status=status
            )
            print(f'list_test_cases() 调用完成，返回 {len(test_cases)} 条记录')
            
            print(f'开始调用 count_test_cases()')
            total = count_test_cases(
                db=db,
                search=search,
                type=type,  # 修改：test_type -> type
                status=status
            )
            print(f'count_test_cases() 调用完成，总数: {total}')
            
            # 格式化返回数据
            items = []
            for test_case in test_cases:
                # 解析steps字段
                steps_data = None
                if test_case.steps:
                    import json
                    try:
                        steps_data = json.loads(test_case.steps)
                    except:
                        steps_data = None
                
                items.append({
                    'id': test_case.id,
                    'name': test_case.name,
                    'description': test_case.description,
                    'type': test_case.type,  # 修改：test_type -> type
                    'priority': test_case.priority,
                    'status': test_case.status,
                    'created_by': test_case.created_by,
                    'updated_at': test_case.updated_at.isoformat() if test_case.updated_at else None,
                    'steps': steps_data,
                    'expected_result': test_case.expected_result
                })
            
            result = {
                'status': 'success',
                'data': {
                    'items': items,
                    'total': total,
                    'page': page,
                    'size': size
                }
            }
            print(f'TestCaseService.get_test_case_list() 处理完成，返回结果: {result}')
            return result
        except Exception as e:
            print(f'TestCaseService.get_test_case_list() 发生异常: {str(e)}')
            return {
                'status': 'error',
                'message': f'获取测试用例列表失败: {str(e)}'
            }
    
    @staticmethod
    def get_test_case_detail(db: Session, test_case_id: int) -> Dict[str, Any]:
        """获取测试用例详情"""
        try:
            test_case = get_test_case_by_id(db, test_case_id)
            if not test_case:
                return {
                    'status': 'error',
                    'message': '测试用例不存在'
                }
            
            # 解析steps字段
            steps_data = None
            if test_case.steps:
                import json
                try:
                    steps_data = json.loads(test_case.steps)
                except:
                    steps_data = None
            
            return {
                'status': 'success',
                'data': {
                    'id': test_case.id,
                    'name': test_case.name,
                    'description': test_case.description,
                    'type': test_case.type,  # 修改：test_type -> type
                    'priority': test_case.priority,
                    'status': test_case.status,
                    'steps': steps_data,
                    'expected_result': test_case.expected_result,
                    'created_by': test_case.created_by,
                    'created_at': test_case.created_at.isoformat() if test_case.created_at else None,
                    'updated_at': test_case.updated_at.isoformat() if test_case.updated_at else None
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'获取测试用例详情失败: {str(e)}'
            }
    
    @staticmethod
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
    ) -> Dict[str, Any]:
        """更新测试用例"""
        try:
            test_case = update_test_case(
                db=db,
                test_case_id=test_case_id,
                name=name,
                description=description,
                type=type,  # 修改：test_type -> type
                priority=priority,
                status=status,
                steps=steps,
                expected_result=expected_result
            )
            
            if not test_case:
                return {
                    'status': 'error',
                    'message': '测试用例不存在'
                }
            
            return {
                'status': 'success',
                'message': '测试用例更新成功',
                'data': {
                    'id': test_case.id,
                    'name': test_case.name
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'更新测试用例失败: {str(e)}'
            }
    
    @staticmethod
    def delete_test_case(db: Session, test_case_id: int) -> Dict[str, Any]:
        """删除测试用例"""
        try:
            success = delete_test_case(db, test_case_id)
            if not success:
                return {
                    'status': 'error',
                    'message': '测试用例不存在'
                }
            
            return {
                'status': 'success',
                'message': '测试用例删除成功'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'删除测试用例失败: {str(e)}'
            }