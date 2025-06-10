# Vue + Python 全栈项目

这是一个使用Vue 3和Python FastAPI构建的全栈项目。

## 项目结构

```
.
├── frontend/          # Vue 3前端项目
│   ├── src/          # 源代码
│   ├── public/       # 静态资源
│   └── package.json  # 项目依赖
│
└── backend/          # Python后端项目
    ├── app/         # 应用代码
    ├── requirements.txt  # Python依赖
    └── main.py      # 入口文件
```

## 开发环境要求

- Node.js >= 16
- Python >= 3.8
- npm >= 7

## 启动说明

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

### 后端启动
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## API文档

启动后端服务后，访问 http://localhost:8000/docs 查看API文档。 