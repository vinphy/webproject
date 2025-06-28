# Vue + Python 全栈项目

这是一个使用Vue 3和Python FastAPI构建的全栈项目，提供数据库设计和可视化功能。

## 项目结构

```
.
├── frontend/          # Vue 3前端项目
│   ├── src/          # 源代码
│   │   ├── views/    # 页面组件
│   │   ├── components/ # 通用组件
│   │   └── router/   # 路由配置
│   ├── public/       # 静态资源
│   └── package.json  # 项目依赖
│
└── backend/          # Python后端项目
    ├── control/      # 控制器层
    ├── service/      # 服务层
    ├── util/         # 工具类
    ├── requirements.txt  # Python依赖
    └── main.py      # 入口文件
```

## 功能特性

### 1. SQL实体关系图生成器
- **SQL导入**: 支持上传SQL文件或直接输入SQL语句
- **智能解析**: 自动解析CREATE TABLE、ALTER TABLE等DDL语句
- **表结构提取**: 提取表名、字段、数据类型、约束等信息
- **关系识别**: 自动识别主键、外键关系
- **可视化图表**: 使用Vue Flow绘制交互式ER图
- **自动布局**: 智能排列表格节点位置
- **详情查看**: 点击表格查看详细字段信息

### 2. 模块管理
- 拖拽式模块设计
- 可视化流程编排
- 组件库管理

### 3. 日志管理
- 系统日志查看
- 日志分析功能

### 4. 符合性测试
- 自动化测试功能
- 测试结果分析

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

### SQL解析API
- `POST /api/sql/parse` - 解析SQL语句
- `GET /api/sql/test` - 测试SQL解析器

## 使用说明

### SQL ER图功能
1. 点击侧边栏"SQL ER图"菜单
2. 在左侧输入SQL语句或上传SQL文件
3. 点击"解析SQL"按钮
4. 系统自动生成实体关系图
5. 可以拖拽调整表格位置
6. 点击表格查看详细字段信息
7. 使用自动布局功能重新排列图表

### 示例SQL
项目提供了示例SQL文件 `frontend/public/sample.sql`，包含完整的电商数据库表结构，可用于测试ER图生成功能。

## 技术栈

### 前端
- Vue 3 (Composition API)
- Vue Router 4
- Element Plus
- Vue Flow (图表绘制)
- Axios (HTTP客户端)

### 后端
- FastAPI
- Pydantic (数据验证)
- SQL解析器 (正则表达式)

## 项目特色

1. **现代化UI**: 使用Element Plus提供美观的用户界面
2. **响应式设计**: 支持多种屏幕尺寸
3. **交互式图表**: Vue Flow提供流畅的图表交互体验
4. **智能解析**: 强大的SQL解析能力，支持复杂表结构
5. **实时预览**: 解析结果实时显示，支持表格详情查看 