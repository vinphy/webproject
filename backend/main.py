from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from control import auth, project, home_control, logs_control, code_file_control, sql_parser_control, bit_test_control

app = FastAPI(title="项目管理系统API")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(project.router, prefix="/api/projects", tags=["projects"])
app.include_router(home_control.router, prefix="/api/home", tags=["home"])
app.include_router(logs_control.router, prefix="/api/logs", tags=["logs"])
app.include_router(code_file_control.router, prefix="/api/code-files", tags=["code-files"])
app.include_router(sql_parser_control.router, prefix="/api/sql-parser", tags=["sql-parser"])
app.include_router(bit_test_control.router, prefix="/api/bit-test", tags=["bit-test"])


@app.get("/")
def read_root():
    return {"message": "项目管理系统API服务运行中"}