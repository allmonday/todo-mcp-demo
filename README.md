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

    @query
    async def get_todos(cls, limit: int = 100) -> list["Todo"]:
        ...

    @mutation
    async def create_todo(cls, title: str) -> "Todo":
        ...
```

上述代码自动生成：

| 能力 | 说明 |
|------|------|
| **GraphQL Query** | `todoGetTodos(limit: 100): [Todo]` |
| **GraphQL Mutation** | `todoCreateTodo(title: "xxx"): Todo` |
| **MCP Tool** | `todoGetTodos`, `todoCreateTodo` 工具供 AI 调用 |

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
  todoGetTodos { id title done comments { content } }
  todoGetTodo(id: 1) { id title }
  commentGetComments { id content todo_id }
  commentGetCommentsByTodo(todoId: 1) { id content }
}
```

### Mutation
```graphql
mutation {
  todoCreateTodo(title: "New Task") { id title }
  todoCreateTodoWithComments(title: "Task", comments: ["c1"]) { id }
  todoSetTodoDone(id: 1, done: true) { id done }
  todoDeleteTodo(id: 1)
  commentCreateComment(todoId: 1, content: "note") { id }
  commentDeleteComment(id: 1)
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
| `todoGetTodos` / `todoGetTodo` | 查询 Todo |
| `todoCreateTodo` / `todoSetTodoDone` / `todoDeleteTodo` | Todo 增删改 |
| `commentGetComments` / `commentGetComment` / `commentGetCommentsByTodo` | 查询评论 |
| `commentCreateComment` / `commentDeleteComment` | 评论增删 |

---

## 技术栈

- **sqlmodel-graphql**: 自动生成 GraphQL + MCP
- **SQLModel**: ORM
- **FastAPI**: Web 框架
- **FastMCP**: MCP 协议
