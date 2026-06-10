# FastAPI LangGraph Agent 模板

这是一个用于构建 AI Agent 后端的 FastAPI + LangGraph 项目模板。它已经把会话状态、长期记忆、工具调用、JWT 鉴权、限流、结构化日志、LLM 观测和 Prometheus/Grafana 监控这些基础设施接好，你可以把主要精力放在 Agent 逻辑本身。

这不是最小 demo，而是一个适合作为生产项目起点的后端骨架。

## 你会得到什么

- **LangGraph Agent**：支持多轮会话、checkpoint、工具调用和 human-in-the-loop。
- **长期记忆**：通过 mem0 + PostgreSQL pgvector 保存每个用户的语义记忆。
- **LLM 服务层**：支持默认模型、fallback 顺序、`tenacity` 指数退避重试和总超时预算。
- **认证与会话**：JWT 登录态、用户注册、聊天 session 管理。
- **数据库迁移**：SQLModel + Alembic，PostgreSQL 默认使用 pgvector 镜像。
- **可观测性**：Langfuse tracing、Prometheus metrics、Grafana dashboard、结构化日志。
- **开发工具链**：`uv`、`ruff`、`pyright`、pre-commit、Docker Compose。

## 最快启动

推荐第一次使用 Docker，因为它会一起启动 API 和 PostgreSQL，避免你手动安装数据库。

```bash
git clone <repo-url> my-agent
cd my-agent

cp .env.example .env.development
```

打开 `.env.development`，至少修改这些项：

```dotenv
OPENAI_API_KEY="你的 LLM API key" # pragma: allowlist secret
DEFAULT_LLM_MODEL=gpt-4o-mini
JWT_SECRET_KEY="用下面命令生成的一长串随机字符串" # pragma: allowlist secret
POSTGRES_HOST=db
POSTGRES_DB=my_agent
POSTGRES_USER=my_agent
POSTGRES_PASSWORD="自己设置一个数据库密码" # pragma: allowlist secret
LANGFUSE_TRACING_ENABLED=false
```

生成 `JWT_SECRET_KEY`：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

然后启动：

```bash
make install
make docker-up
docker compose --env-file .env.development exec app uv run alembic upgrade head
```

确认服务可用：

- API 文档：[http://localhost:8000/docs](http://localhost:8000/docs)
- 健康检查：[http://localhost:8000/health](http://localhost:8000/health)

更完整的逐步说明，包括每个环境变量是什么意思、如何填写、如何第一次调用聊天接口，请看 [Getting Started](docs/getting-started.md)。

## 第一次通常要改哪些文件

| 目标 | 修改位置 | 说明 |
| --- | --- | --- |
| 改 Agent 人设和行为规则 | `app/core/prompts/system.md` | 这里是系统提示词模板，适合改回答风格、约束和业务角色。 |
| 加工具 | `app/core/langgraph/tools/` | 新增 LangChain tool 后，在 `app/core/langgraph/tools/__init__.py` 的 `tools` 列表注册。 |
| 改模型和 fallback 顺序 | `app/services/llm/registry.py` | `DEFAULT_LLM_MODEL` 控制起始模型，registry 控制候选模型列表。 |
| 改 API 路由 | `app/api/v1/` | `auth.py` 管认证，`chatbot.py` 管聊天接口，`api.py` 汇总 router。 |
| 改数据库模型 | `app/models/` | 新增或修改 SQLModel 后，用 `make migration MSG="..."` 生成迁移。 |
| 改请求/响应结构 | `app/schemas/` | Pydantic schema 放在这里，接口入参和返回值都应先建模。 |
| 改环境配置 | `.env.development`、`app/core/config.py` | 本地值写 `.env.development`；新增配置项时再同步到 `config.py`。 |

如果只是想改 Agent 怎么回答，通常只需要先看 `app/core/prompts/system.md` 和 `app/core/langgraph/tools/`，不用一开始就理解整个项目。

## 文档导航

| 文档 | 内容 |
| --- | --- |
| [Getting Started](docs/getting-started.md) | 从零启动、配置 `.env`、第一次 API 调用、常见问题。 |
| [Architecture](docs/architecture.md) | 系统结构、请求流、关键组件。 |
| [Configuration](docs/configuration.md) | 所有环境变量和默认值。 |
| [Authentication](docs/authentication.md) | JWT、用户、session 和认证接口。 |
| [Database & Migrations](docs/database.md) | 数据库 schema、Alembic、pgvector。 |
| [LLM Service](docs/llm-service.md) | 模型注册、重试、fallback、超时预算。 |
| [Memory](docs/memory.md) | mem0 长期记忆和缓存层。 |
| [Observability](docs/observability.md) | Langfuse、Prometheus、Grafana、日志和 profiling。 |
| [Evaluation](docs/evaluation.md) | LLM eval 框架、自定义指标、报告。 |
| [Docker](docs/docker.md) | Docker Compose 服务、完整监控栈、Grafana。 |

## 项目结构

```text
app/
  api/v1/          # FastAPI 路由
  core/
    langgraph/     # Agent graph 和工具
    prompts/       # 系统提示词
    cache.py       # Valkey/Redis 或内存缓存
    config.py      # 配置读取
    middleware.py  # 日志、指标、profiling 中间件
    limiter.py     # slowapi 限流
  models/          # SQLModel ORM 模型
  schemas/         # Pydantic 请求/响应模型
  services/        # LLM、数据库、记忆等服务
alembic/           # 数据库迁移
evals/             # LLM 评测框架
```

## FAQ

### `JWT_SECRET_KEY` 是什么？

它是用来签名 JWT token 的密钥。可以把 JWT 理解成“服务器签过名的登录凭证”。如果这个密钥泄露，别人就可能伪造登录态，所以不要提交到 Git。开发环境用下面命令生成即可：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### `POSTGRES_*` 是什么？

这些变量告诉应用怎么连接 PostgreSQL：

- `POSTGRES_HOST`：数据库主机。Docker 内部用 `db`；本机直接连数据库通常用 `localhost`。
- `POSTGRES_PORT`：端口，默认 `5432`。
- `POSTGRES_DB`：数据库名。
- `POSTGRES_USER`：数据库用户名。
- `POSTGRES_PASSWORD`：数据库密码。

第一次用 Docker 时不需要先创建数据库，Compose 会按 `.env.development` 里的 `POSTGRES_DB`、`POSTGRES_USER`、`POSTGRES_PASSWORD` 初始化。

### 一定要配置 Langfuse 吗？

不需要。第一次启动建议先设：

```dotenv
LANGFUSE_TRACING_ENABLED=false
```

等 API 和聊天主流程跑通后，再去配置 `LANGFUSE_PUBLIC_KEY`、`LANGFUSE_SECRET_KEY` 和 `LANGFUSE_HOST`。

### 支持哪些 LLM provider？

当前代码通过 `langchain_openai.ChatOpenAI` 接 OpenAI-compatible API。你至少需要：

```dotenv
OPENAI_API_KEY="你的 API key" # pragma: allowlist secret
DEFAULT_LLM_MODEL=gpt-4o-mini
```

如果你使用的是兼容 OpenAI 协议的第三方服务，再加：

```dotenv
OPENAI_BASE_URL=https://provider.example.com/v1
```

### 长期记忆需要单独申请 mem0 账号吗？

不需要。mem0 在应用进程内运行，记忆数据保存在 PostgreSQL + pgvector 里。它仍然会调用 LLM 和 embedding 模型，所以 `OPENAI_API_KEY` 需要可用。

### API 起不来怎么办？

优先按这个顺序查：

```bash
make docker-logs
```

然后确认：

- `.env.development` 存在。
- `OPENAI_API_KEY` 和 `JWT_SECRET_KEY` 不是占位值。
- Docker 路径下 `POSTGRES_HOST=db`。
- 本机 Python 路径下 `POSTGRES_HOST=localhost`，且 PostgreSQL 已启动。

## 贡献

开发前先按 [Getting Started](docs/getting-started.md) 跑通环境，再遵守 [AGENTS.md](AGENTS.md) 中的代码和协作约定。

安全问题请按 [SECURITY.md](SECURITY.md) 私下报告。

## License

See [LICENSE](LICENSE).
