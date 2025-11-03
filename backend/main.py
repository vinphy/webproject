from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from service.resource_service import resource_service
from util.db import init_db, Base
from models import resource_model

# 导入各个控制层
from control import auth, project, home_control, logs_control, resource_control, code_file_control, sql_parser_control, bit_test_control

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    print("应用启动中...")
    
    # 初始化数据库表
    try:
        init_db(Base)
        print("数据库表初始化完成")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
    
    # 启动资源监控服务
    try:
        resource_service.start_background_update()
        print("资源监控服务已启动")
    except Exception as e:
        print(f"资源监控服务启动失败: {e}")
    
    yield
    
    # 关闭时执行
    print("应用关闭中...")
    
    # 停止资源监控服务
    try:
        resource_service.stop_background_update()
        print("资源监控服务已停止")
    except Exception as e:
        print(f"资源监控服务停止失败: {e}")

app = FastAPI(title="项目管理系统API", lifespan=lifespan)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(project.router, prefix="/api/projects", tags=["项目管理"])
app.include_router(home_control.router, prefix="/api/home", tags=["首页"])
app.include_router(logs_control.router, prefix="/api/logs", tags=["日志管理"])
app.include_router(resource_control.router, prefix="/api/resources", tags=["资源监控"])
app.include_router(code_file_control.router, prefix="/api/codeFile", tags=["代码文件"])
app.include_router(sql_parser_control.router, prefix="/api/sqlParser", tags=["SQL解析"])
app.include_router(bit_test_control.router, prefix="/api/bitTest", tags=["位测试"])

@app.get("/")
async def root():
    return {"message": "项目管理系统API服务运行中", "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)