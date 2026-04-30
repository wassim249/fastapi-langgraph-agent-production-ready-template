# FastAPI LangGraph Agent Template

A production-ready template for building AI agent backends with FastAPI and LangGraph. Handles the hard parts — stateful conversations, long-term memory, tool calling, observability, rate limiting, auth — so you can focus on your agent logic.

**Built for AI engineers** who want a solid foundation, not a tutorial project.

## What's included

- **LangGraph** stateful agent with checkpointing, tool calling, and human-in-the-loop support
- **Long-term memory** via mem0 + pgvector — semantic search per user, cache-backed
- **LLM service** with circular model fallback, exponential backoff retries, and total timeout budget
- **Langfuse** tracing on all LLM calls; Prometheus metrics + Grafana dashboards
- **JWT auth** with session management; rate limiting via slowapi
- **Alembic** migrations; optional Valkey/Redis cache layer
- **Structured logging** with request/session/user context on every line

## Quickstart

```bash
git clone <repo-url> my-agent && cd my-agent
cp .env.example .env.development   # fill in your keys
make install
make docker-up                     # starts API + PostgreSQL
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) to see the interactive API.

> For local development without Docker see [docs/getting-started.md](docs/getting-started.md).

## Documentation

| Guide | What it covers |
|---|---|
| [Getting Started](docs/getting-started.md) | Prerequisites, local setup, first API call |
| [Architecture](docs/architecture.md) | System design, request flow, component diagrams |
| [Configuration](docs/configuration.md) | All environment variables with defaults |
| [Authentication](docs/authentication.md) | JWT flow, sessions, endpoint reference |
| [Database & Migrations](docs/database.md) | Schema, Alembic migrations, pgvector |
| [LLM Service](docs/llm-service.md) | Models, retries, fallback, timeout budget |
| [Memory](docs/memory.md) | mem0 long-term memory, cache layer |
| [Observability](docs/observability.md) | Langfuse, structured logging, Prometheus, profiling |
| [Evaluation](docs/evaluation.md) | Eval framework, custom metrics, reports |
| [Docker](docs/docker.md) | Docker, Compose, full monitoring stack |

## Project structure

```
app/
  api/v1/          # Route handlers
  core/
    langgraph/     # Agent graph + tools
    prompts/       # System prompt template
    cache.py       # Valkey/Redis + in-memory fallback
    config.py      # Settings
    middleware.py  # Metrics, logging context, profiling
    limiter.py     # Rate limiting
  models/          # SQLModel ORM models
  schemas/         # Pydantic request/response schemas
  services/        # LLM, database, memory services
alembic/           # Database migrations
evals/             # LLM evaluation framework
```

## Contributing

PRs welcome. Please read [docs/getting-started.md](docs/getting-started.md) to get your environment set up, then follow the coding conventions in [AGENTS.md](AGENTS.md).

Report security issues privately — see [SECURITY.md](SECURITY.md).

## License

See [LICENSE](LICENSE).

## FAQ

### General

**What is this template?**
This is a production-ready template for building AI agent backends with FastAPI and LangGraph. It handles stateful conversations, long-term memory, tool calling, observability, rate limiting, and authentication — providing a solid foundation for AI engineers.

**How does this differ from a basic LangGraph setup?**
This template provides a complete production stack including database migrations (Alembic), long-term memory (mem0 + pgvector), observability (Langfuse + Prometheus), JWT authentication, rate limiting, and structured logging — components you'd typically build separately.

### Setup & Configuration

**Do I need Docker?**
Docker is recommended for local development (`make docker-up` starts API + PostgreSQL). For local development without Docker, see [docs/getting-started.md](docs/getting-started.md).

**What LLM providers are supported?**
The LLM service supports any provider compatible with LangChain's `init_chat_model`, including OpenAI, Anthropic, Azure, and local models. Configure via environment variables in `.env.development`.

**How do I configure long-term memory?**
Long-term memory uses mem0 + pgvector for semantic search per user. Configure your PostgreSQL connection and mem0 API key in `.env.development`. See [docs/memory.md](docs/memory.md) for details.

### Development

**How do I add custom tools?**
Add your tool implementations in `app/core/langgraph/tools/` and register them in the agent graph configuration. See the existing tools for examples.

**How does the LLM service handle failures?**
The LLM service implements circular model fallback (tries multiple models in sequence), exponential backoff retries, and a total timeout budget to ensure resilient LLM interactions.

**Can I use this without Langfuse?**
Yes, Langfuse tracing is optional. Disable it by omitting the Langfuse configuration variables. The agent will still function with structured logging.

### Troubleshooting

**The API won't start**
- Ensure PostgreSQL is running (`make docker-up` starts it automatically)
- Check that all required environment variables are set (copy `.env.example` to `.env.development`)
- Verify database migrations: `make migrate`

**Memory/semantic search not working**
- Verify pgvector extension is enabled in PostgreSQL
- Check mem0 API key configuration
- Ensure embedding model is configured and accessible

**Rate limiting is too aggressive**
Adjust rate limit configuration in `app/core/middleware.py` or via environment variables. See [docs/configuration.md](docs/configuration.md) for available options.
