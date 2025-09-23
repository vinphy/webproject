from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from control.codeFile import router as code_file_router
from control.bit_test_control import router as bit_test_router
from control.sql_parser_control import router as sql_parser_router
from control.logs_control import router as logs_router

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# 注册路由
app.include_router(code_file_router, prefix="/api/code", tags=["code"])
app.include_router(bit_test_router, prefix="/api/test", tags=["test"])
app.include_router(sql_parser_router, prefix="/api/sql", tags=["sql"])
app.include_router(logs_router, prefix="/api/logs", tags=["logs"])

# 认证路由
from control.auth import router as auth_router
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

@app.on_event("startup")
def on_startup():
    # 确保默认管理员存在
    from control.auth import ensure_default_admin
    from util.db import get_db
    try:
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