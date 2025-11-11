// ... existing code ...
from control import auth, project, home_control, logs_control, resource_control, code_file_control, sql_parser_control, bit_test_control
# 暂时注释掉不存在的导入
# from control import test_case_control

// ... existing code ...
# 暂时注释掉测试用例路由注册
# app.include_router(test_case_control.router, prefix="/api/test-cases", tags=["测试用例"])