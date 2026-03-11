# Todo MCP Demo

**只需定义 Model，自动生成 GraphQL API 和 MCP Server。**

基于 `sqlmodel-graphql` 库，通过 `@query` 和 `@mutation` 装饰器，一次定义即可获得：
- GraphQL API（含 GraphiQL 界面）
- MCP Server（支持 stdio 和 HTTP 模式）

---

## 核心特性

### 一处定义，多处使用

```python
# models.py - 只需定义 Model 和装饰器
from sqlmodel import SQLModel
from sqlmodel_graphql import query, mutation

class Todo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    done: bool = Field(default=False)

    @query(name="todos")
    async def get_all(cls, limit: int = 100) -> list["Todo"]:
        ...

    @mutation(name="todo_add")
    async def create(cls, title: str) -> "Todo":
        ...
```

上述代码自动生成：

| 能力 | 说明 |
|------|------|
| **GraphQL Query** | `todos(limit: 100): [Todo]` |
| **GraphQL Mutation** | `todo_add(title: "xxx"): Todo` |
| **MCP Tool** | `todos`, `todo_add` 工具供 AI 调用 |

---

## 项目结构

```
src/todo/
├── models.py       # Model 定义（核心）
├── app.py          # GraphQL 服务（几行代码）
├── mcp_server.py   # MCP Server（几行代码）
└── database.py     # 数据库配置
```

---

## 快速开始

```bash
# 安装依赖
uv sync

# 启动 GraphQL 服务
uv run python -m todo.app
# 访问 http://localhost:8000/graphql

# 启动 MCP Server (stdio)
uv run todo-mcp

# 启动 MCP Server (HTTP)
uv run todo-mcp --http
```

---

## GraphQL API

访问 http://localhost:8000/graphql 进入 GraphiQL 界面。

### Query
```graphql
query {
  todos { id title done comments { content } }
  todo(id: 1) { id title }
  comments { id content todo_id }
  comments_by_todo(todoId: 1) { id content }
}
```

### Mutation
```graphql
mutation {
  todo_add(title: "New Task") { id title }
  todo_add_with_comments(title: "Task", comments: ["c1"]) { id }
  todo_done(id: 1, done: true) { id done }
  todo_delete(id: 1)
  comment_add(todoId: 1, content: "note") { id }
  comment_delete(id: 1)
}
```

---

## MCP Server

### Claude Desktop 配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "todo": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/todo-mcp-demo", "todo-mcp"]
    }
  }
}
```

### 可用工具

所有 `@query` 和 `@mutation` 自动暴露为 MCP 工具：

| 工具 | 说明 |
|------|------|
| `todos` / `todo` | 查询 Todo |
| `todo_add` / `todo_done` / `todo_delete` | Todo 增删改 |
| `comments` / `comment` / `comments_by_todo` | 查询评论 |
| `comment_add` / `comment_delete` | 评论增删 |

---

## 技术栈

- **sqlmodel-graphql**: 自动生成 GraphQL + MCP
- **SQLModel**: ORM
- **FastAPI**: Web 框架
- **FastMCP**: MCP 协议
