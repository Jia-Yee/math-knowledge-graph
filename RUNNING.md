# Math Knowledge Graph - API & Web 运行指南

## 📁 文件结构

```
math-knowledge-graph/
├── app/
│   ├── api/
│   │   └── main.py           # FastAPI 后端服务
│   └── web/
│       └── index.html        # Web 前端界面
├── data/
│   └── core-nodes.json       # 知识节点数据
└── schema/                   # JSON Schema 定义
```

---

## 🚀 快速启动

### 1. 安装依赖

```bash
cd /Users/jia/.qclaw/workspace/math-knowledge-graph

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或: venv\Scripts\activate  # Windows

# 安装依赖
pip install fastapi uvicorn pydantic
```

### 2. 启动后端服务

```bash
# 在项目根目录运行
python3 app/api/main.py
```

服务将启动在: **http://localhost:8000**

### 3. 访问 Web 界面

直接在浏览器中打开:
```
file:///Users/jia/.qclaw/workspace/math-knowledge-graph/app/web/index.html
```

或者使用 Python 启动一个简单的 HTTP 服务器:
```bash
cd app/web
python3 -m http.server 8080
```

然后访问: **http://localhost:8080**

---

## 📡 API 接口文档

启动后端后，访问自动生成的文档:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 核心接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/levels` | 获取所有学习阶段 |
| GET | `/nodes` | 获取知识节点列表 |
| GET | `/nodes/{node_id}` | 获取节点详情 |
| GET | `/branches` | 获取数学分支列表 |
| GET | `/assessment/questions` | 获取评估问题 |
| POST | `/users/{user_id}/assess` | 提交知识评估 |
| GET | `/users/{user_id}/profile` | 获取用户知识画像 |
| POST | `/users/{user_id}/recommend` | 获取学习推荐 |

---

## 🎯 使用流程

### 1. 选择学习阶段
用户在 Web 界面选择自己的学习阶段（小学/初中/高中/本科）

### 2. 知识点评估
- 系统展示该阶段的重要知识点
- 用户选择"知道"或"不知道"
- 后台构建用户的知识掌握图谱

### 3. 查看知识画像
- 统计已掌握和待学习的知识点数量
- 展示各级别的掌握进度
- 确定当前推荐学习级别

### 4. 获取学习推荐
- 系统分析知识依赖关系
- 推荐可以学习的下一个知识点
- 按难度和重要性排序

---

## 🔧 功能特性

### 已实现
- ✅ 知识节点数据模型（50个节点）
- ✅ 依赖关系建模（prerequisites）
- ✅ FastAPI RESTful API
- ✅ 用户知识评估接口
- ✅ 学习路径推荐算法
- ✅ Web 前端界面（4步流程）

### 待完善
- [ ] 依赖边数据独立存储
- [ ] 更复杂的推荐算法（考虑学习风格）
- [ ] 学习进度持久化（数据库）
- [ ] 用户认证系统
- [ ] 知识图谱可视化
- [ ] 更多知识节点（目标500+）

---

## 📝 示例请求

### 获取评估问题
```bash
curl "http://localhost:8000/assessment/questions?level=primary&limit=5"
```

### 提交评估结果
```bash
curl -X POST "http://localhost:8000/users/user_123/assess" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "assessments": [
      {"node_id": "natural_numbers", "known": true},
      {"node_id": "addition", "known": true},
      {"node_id": "subtraction", "known": false}
    ]
  }'
```

### 获取学习推荐
```bash
curl -X POST "http://localhost:8000/users/user_123/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "max_nodes": 5
  }'
```

---

## 🐛 常见问题

### 1. CORS 错误
如果前端无法连接后端，确保后端服务已正确启动，并且 CORS 配置允许前端域名。

### 2. 数据未加载
如果 API 返回空数据，检查 `data/core-nodes.json` 文件是否存在且格式正确。

### 3. 端口被占用
如果 8000 端口被占用，修改 `app/api/main.py` 最后一行的端口号:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # 改为其他端口
```

---

## 🎨 界面预览

Web 界面包含以下步骤：

1. **选择级别** - 精美的卡片式级别选择
2. **知识点评估** - 进度条 + 问题卡片
3. **知识画像** - 统计卡片 + 进度可视化
4. **学习推荐** - 推荐列表 + 学习路径

界面采用紫色渐变主题，响应式设计，支持移动端访问。
