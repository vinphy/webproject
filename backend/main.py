from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from control.code_file_control import router as code_file_router
from control.bit_test_control import router as bit_test_router
from control.sql_parser_control import router as sql_parser_router
from control.logs_control import router as logs_router
from control.auth import router as auth_router
from control.home_control import router as home_router

app = FastAPI()

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# 注册路由
app.include_router(auth_router, prefix="/api/auth", tags=["auth"]) # 认证路由
app.include_router(code_file_router, prefix="/api/code", tags=["code"])
app.include_router(bit_test_router, prefix="/api/test", tags=["test"])
app.include_router(sql_parser_router, prefix="/api/sql", tags=["sql"])
app.include_router(logs_router, prefix="/api/logs", tags=["logs"])
app.include_router(home_router, prefix="/api/home", tags=["home"])


@app.on_event("startup")
def on_startup():
    """应用启动时执行的初始化函数
    
    此函数在 FastAPI 应用启动时被触发，主要负责执行初始化操作，
    当前主要功能是确保系统中存在默认的管理员账户。
    """
    # 确保默认管理员存在
    # 动态导入所需模块，避免循环导入问题
    from models.auth_model import ensure_default_admin
    from util.db import get_db
    try:
        # 获取数据库会话并执行确保默认管理员存在的操作
        with next(get_db()) as db:
            ensure_default_admin(db)
    except Exception as e:
        print(f"[STARTUP] ensure_default_admin failed: {e}")

@app.get("/")
async def root():
    return {"message": "Welcome to the API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 