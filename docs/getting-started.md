# Getting Started：从零启动本项目

这份文档面向第一次接触这个项目的人。目标是：按步骤操作后，能启动 API、打开 Swagger 文档，并完成一次真实聊天请求。

推荐先走 **Docker 路径**。它会同时启动 API 和 PostgreSQL，最少依赖本机环境。

## 0. 你需要先准备什么

| 工具 | 用途 | 检查命令 |
| --- | --- | --- |
| Python 3.13+ | 运行本地脚本、生成密钥、安装依赖 | `python --version` |
| uv | Python 依赖管理 | `uv --version` |
| Docker + Docker Compose v2 | 启动 API、PostgreSQL、可选监控栈 | `docker compose version` |
| LLM API key | 让 Agent 真正调用模型回答问题 | 从你的 OpenAI 或 OpenAI-compatible provider 获取 |

如果没有 `uv`：

```bash
pip install uv
```

Langfuse、Prometheus、Grafana 都不是第一次启动的必需项。先把主流程跑通，再打开观测能力。

## 1. 克隆项目并创建配置文件

```bash
git clone <repo-url> my-agent
cd my-agent
cp .env.example .env.development
```

以后本地开发默认改 `.env.development`。不要把真实密钥写进 `.env.example`，也不要把 `.env.development` 提交到 Git。

## 2. 填写 `.env.development`

打开 `.env.development`，先只关注下面这些变量。

### 2.1 必填项

| 变量 | 你应该填什么 | 为什么需要 |
| --- | --- | --- |
| `OPENAI_API_KEY` | 你的 LLM API key，例如 `sk-...` | Agent、长期记忆、session 命名都会调用模型。 |
| `DEFAULT_LLM_MODEL` | 你的模型名，例如 `gpt-4o-mini` | 应用启动后默认先调用这个模型。 |
| `JWT_SECRET_KEY` | 一段随机长字符串 | 用来签名登录 token，不能用固定示例值。 |
| `POSTGRES_HOST` | Docker 路径填 `db`；本机 Python 路径填 `localhost` | 告诉应用数据库在哪里。 |
| `POSTGRES_DB` | 数据库名，例如 `my_agent` | PostgreSQL 里要使用的数据库。 |
| `POSTGRES_USER` | 数据库用户名，例如 `my_agent` | 应用用它登录数据库。 |
| `POSTGRES_PASSWORD` | 自己设置的数据库密码 | 应用用它登录数据库。 |

生成 `JWT_SECRET_KEY`：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

如果你不知道数据库名、用户名、密码怎么取，开发环境可以直接用这一组：

```dotenv
POSTGRES_DB=my_agent
POSTGRES_USER=my_agent
POSTGRES_PASSWORD=dev_password_change_me
```

这三个值只要彼此一致即可。Docker 第一次创建数据库容器时，会用它们初始化 PostgreSQL。

### 2.2 推荐的 Docker 开发配置

第一次启动建议 `.env.development` 至少长这样：

```dotenv
APP_ENV=development
DEBUG=true

OPENAI_API_KEY="你的 LLM API key" # pragma: allowlist secret
DEFAULT_LLM_MODEL=gpt-4o-mini
# 如果你使用 OpenAI-compatible 第三方服务，再打开并填写这一行：
# OPENAI_BASE_URL=https://provider.example.com/v1

JWT_SECRET_KEY="粘贴 python secrets 命令生成的值" # pragma: allowlist secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_DAYS=30

POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=my_agent
POSTGRES_USER=my_agent
POSTGRES_PASSWORD=dev_password_change_me # pragma: allowlist secret

LANGFUSE_TRACING_ENABLED=false
LOG_FORMAT=console
```

注意：Docker 路径下 `POSTGRES_HOST=db`，因为 API 容器和数据库容器在同一个 Docker Compose 网络里，`db` 是数据库服务名。

### 2.3 可选项先怎么处理

| 变量 | 第一次启动建议 | 说明 |
| --- | --- | --- |
| `OPENAI_BASE_URL` | 用官方 OpenAI 可留空；第三方兼容服务才填写 | 必须包含服务商要求的 `/v1` 路径时就照服务商文档填。 |
| `LANGFUSE_TRACING_ENABLED` | 先设为 `false` | 没有 Langfuse 账号也能启动。 |
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` | 先不用改 | 只有启用 Langfuse tracing 时才需要。 |
| `VALKEY_HOST` | 先留空 | 留空时使用进程内缓存；要共享缓存再设为 `valkey`。 |
| `LONG_TERM_MEMORY_*` | 先保留默认 | 只有要换记忆提取模型、embedding 模型或 collection 名时才改。 |

## 3. 路径 A：用 Docker 启动 API + PostgreSQL

这是推荐路径。

```bash
make install
make docker-up
```

`make docker-up` 会启动两个服务：

- `app`：FastAPI API，端口 `8000`。
- `db`：PostgreSQL + pgvector，端口 `5432`。

查看日志：

```bash
make docker-logs
```

打开：

- Swagger API 文档：[http://localhost:8000/docs](http://localhost:8000/docs)
- 健康检查：[http://localhost:8000/health](http://localhost:8000/health)

如果你需要停掉容器：

```bash
make docker-down
```

## 4. 数据库迁移

应用需要数据库表。Docker 路径下推荐直接在 `app` 容器里执行迁移，因为容器内能稳定解析 `POSTGRES_HOST=db`：

```bash
docker compose --env-file .env.development exec app uv run alembic upgrade head
```

看到命令正常结束后，再打开 [http://localhost:8000/docs](http://localhost:8000/docs) 做接口调用。

如果你不是用 Docker 跑 API，而是本机 Python 路径，迁移命令见下一节。

## 5. 路径 B：不用 Docker，只本机运行 Python

这条路径适合你本机已经有 PostgreSQL，并且数据库中已启用 pgvector。

`.env.development` 里数据库 host 应该改成：

```dotenv
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=my_agent
POSTGRES_USER=my_agent
POSTGRES_PASSWORD=dev_password_change_me
```

然后执行：

```bash
make install
make migrate
make dev
```

如果 PostgreSQL 用户或数据库还不存在，需要先在本机 PostgreSQL 中创建。具体命令取决于你的 PostgreSQL 安装方式。

## 6. 完成第一次 API 调用

下面命令假设 API 已在 `http://localhost:8000` 运行。

### 6.1 注册用户

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "Secret123!", "username": "you"}' # pragma: allowlist secret
```

返回里会有 `token.access_token`。这是用户 token，只能代表“这个用户已登录”。

为了后续命令更直观，可以复制返回值后设置变量：

```bash
USER_TOKEN="粘贴 token.access_token"
```

### 6.2 创建聊天 session

```bash
curl -X POST http://localhost:8000/api/v1/auth/session \
  -H "Authorization: Bearer $USER_TOKEN"
```

返回里会有另一个 `token.access_token`。这是 session token，聊天接口要用它。

```bash
SESSION_TOKEN="粘贴 session 返回的 token.access_token"
```

### 6.3 发送聊天请求

```bash
curl -X POST http://localhost:8000/api/v1/chatbot/chat \
  -H "Authorization: Bearer $SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "你好，请用一句话介绍你自己。"}]}'
```

如果你想看流式响应：

```bash
curl -N -X POST http://localhost:8000/api/v1/chatbot/chat/stream \
  -H "Authorization: Bearer $SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "请列出三个适合新手修改这个项目的入口。"}]}'
```

## 7. 修改指南：常见需求应该改哪里

### 7.1 修改 Agent 的回答风格和业务身份

改这个文件：

```text
app/core/prompts/system.md
```

适合放：

- Agent 的角色。
- 回答风格。
- 业务规则。
- 不允许做什么。
- 输出格式要求。

改完后重启 API，再调用聊天接口验证。

### 7.2 增加或修改工具

工具目录：

```text
app/core/langgraph/tools/
```

一般步骤：

1. 在 `app/core/langgraph/tools/` 下新增一个工具文件。
2. 使用 LangChain tool 格式定义工具。
3. 在 `app/core/langgraph/tools/__init__.py` 里导入并加入 `tools` 列表。
4. 重启 API。
5. 用聊天请求验证 Agent 是否会在合适场景调用工具。

### 7.3 修改默认模型

只换启动模型时，优先改 `.env.development`：

```dotenv
DEFAULT_LLM_MODEL=gpt-4o-mini
```

要调整 fallback 顺序或支持更多模型，再改：

```text
app/services/llm/registry.py
```

### 7.4 修改 API 接口

路由文件在：

```text
app/api/v1/
```

- `auth.py`：注册、登录、session。
- `chatbot.py`：聊天、流式聊天、消息历史。
- `api.py`：汇总所有 router。

新增接口时，记得补：

- Pydantic schema：`app/schemas/`。
- rate limiting decorator。
- structlog 日志。
- async 数据库调用。

### 7.5 修改数据库结构

模型目录：

```text
app/models/
```

修改 SQLModel 后生成迁移：

```bash
make migration MSG="describe your change"
```

检查 `alembic/versions/` 下生成的迁移文件，确认无误后执行：

```bash
make migrate
```

## 8. 可选：启动完整监控栈

主流程跑通后，如果要看 Prometheus 和 Grafana：

```bash
make stack-up
```

访问：

- Prometheus：[http://localhost:9090](http://localhost:9090)
- Grafana：[http://localhost:3000](http://localhost:3000)

Grafana 默认账号：

```text
admin / admin
```

停止完整栈：

```bash
make stack-down
```

## 9. 常见问题

### API 启动失败，提示缺少 `JWT_SECRET_KEY`

说明 `.env.development` 没有被正确填写，或者值还是空。执行：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

把输出粘贴到：

```dotenv
JWT_SECRET_KEY="这里换成生成的值"
```

### 数据库连接失败

先确认你走的是哪条路径：

- Docker 路径：`.env.development` 里应为 `POSTGRES_HOST=db`。
- 本机 Python 路径：`.env.development` 里通常应为 `POSTGRES_HOST=localhost`。

查看 Docker 服务：

```bash
docker compose --env-file .env.development ps
```

查看日志：

```bash
make docker-logs
```

### `make migrate` 连不上 `db`

这是因为 `db` 是 Docker Compose 网络里的服务名，宿主机不一定能解析。Docker 路径下请在 app 容器里跑迁移：

```bash
docker compose --env-file .env.development exec app uv run alembic upgrade head
```

如果你想从宿主机执行 `make migrate`，需要把 `.env.development` 里的 `POSTGRES_HOST` 改成 `localhost`，并确保 API 容器也使用能访问数据库的配置；第一次启动不推荐这样混用。

### 聊天接口返回模型调用错误

优先检查：

- `OPENAI_API_KEY` 是否真实可用。
- `DEFAULT_LLM_MODEL` 是否是你的服务商支持的模型名。
- 使用第三方 OpenAI-compatible provider 时，`OPENAI_BASE_URL` 是否正确。
- 如果服务商不支持 registry 里的 fallback 模型，需要同步调整 `app/services/llm/registry.py`。

### 没有 Langfuse 账号

开发环境直接设置：

```dotenv
LANGFUSE_TRACING_ENABLED=false
```

### pre-commit 提示 detect-secrets

如果是测试文档里的假密码，可以在对应行尾添加：

```text
# pragma: allowlist secret
```

真实密钥不要这样处理，应该移出仓库。

## 10. 日常开发命令

```bash
make dev              # 本机启动 API，热重载
make docker-up        # Docker 启动 API + DB
make docker-down      # 停止 Docker API + DB
make docker-logs      # 查看 Docker 日志
make migrate          # 执行数据库迁移
make lint             # ruff lint
make format           # ruff format
make typecheck        # pyright
make check            # lint + typecheck
```
