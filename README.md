# FastAPI LangGraph Agent Template

A production-ready FastAPI template for building AI agent applications with LangGraph integration, featuring LLM observability, long-term memory, and comprehensive monitoring.

## 🌟 Features

- **FastAPI** with async endpoints and uvloop optimization
- **LangGraph** for stateful AI agent workflows with persistence
- **Langfuse** for LLM observability and tracing
- **PostgreSQL + pgvector** for data and vector storage
- **mem0ai** for long-term semantic memory
- **JWT authentication** with session management
- **Rate limiting** with configurable rules
- **Structured logging** with environment-specific formatting
- **Prometheus + Grafana** for monitoring
- **Docker** support for easy deployment
- **Model evaluation framework** with automated metrics

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- PostgreSQL with pgvector extension
- Docker and Docker Compose (optional)

### Setup

1. **Clone and install dependencies:**
```bash
git clone <repository-url>
cd <project-directory>
uv sync
```

2. **Configure environment:**
```bash
cp .env.example .env.development
# Edit .env.development with your settings
```

3. **Database setup:**
   - Create a PostgreSQL database
   - Update database connection in `.env.development`:
```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=your_db_name
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

4. **Run migrations:**
```bash
# See Database Migrations section below
alembic upgrade head
```

5. **Start the application:**
```bash
make dev  # or make staging / make prod
```

6. **Access Swagger UI:**
```
http://localhost:8000/docs
```

## 📊 Database Migrations

This project uses **Alembic** for database schema management. Migrations are located in the `migrations/` directory.

### Initial Setup

1. **Create a new migration:**
```bash
alembic revision -m "description_of_changes"
```

2. **Auto-generate migration from models:**
```bash
alembic revision --autogenerate -m "description_of_changes"
```

3. **Review the generated migration** in `migrations/versions/` before applying.

### Running Migrations

1. **Apply all pending migrations:**
```bash
alembic upgrade head
```

2. **Apply migrations up to a specific revision:**
```bash
alembic upgrade <revision_id>
```

3. **Rollback one migration:**
```bash
alembic downgrade -1
```

4. **Rollback to a specific revision:**
```bash
alembic downgrade <revision_id>
```

5. **Show current revision:**
```bash
alembic current
```

6. **Show migration history:**
```bash
alembic history
```

7. **Show pending migrations:**
```bash
alembic heads
```

### Migration Best Practices

- **Always review auto-generated migrations** before applying
- **Test migrations** in development before production
- **Never edit existing migrations** that have been applied to production
- **Create new migrations** for schema changes instead of modifying old ones
- **Use descriptive names** for migration messages
- **Backup your database** before running migrations in production

### Environment Variables

Alembic automatically reads database connection from environment variables:
- `DATABASE_URL` (takes precedence if set)
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`

## 🐳 Docker Setup

1. **Build and run:**
```bash
make docker-build-env ENV=development
make docker-run-env ENV=development
```

2. **Access services:**
- API: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## ⚙️ Configuration

Environment-specific config files:
- `.env.development` - Local development
- `.env.staging` - Staging environment
- `.env.production` - Production environment

### Key Environment Variables

```bash
# Application
APP_ENV=development
PROJECT_NAME="FastAPI LangGraph Agent"
DEBUG=true

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mydb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# LLM
OPENAI_API_KEY=your_openai_api_key
DEFAULT_LLM_MODEL=gpt-4o
DEFAULT_LLM_TEMPERATURE=0.7

# Observability
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com

# Security
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🧠 Key Components

### Long-Term Memory (mem0ai)
- Semantic memory storage with pgvector
- User-specific memory isolation
- Automatic memory extraction and retrieval

### LLM Service
- Multiple model support (GPT-4o, GPT-4o-mini, GPT-5 variants)
- Automatic retry logic with exponential backoff
- Streaming responses for real-time interactions

### Logging
- Structured logging with structlog
- Request context binding (request_id, session_id, user_id)
- Environment-specific formatting (JSON in production, colored in development)

## 📝 Model Evaluation

Run evaluations to measure model performance:

```bash
# Interactive mode
make eval ENV=development

# Quick mode with defaults
make eval-quick ENV=development

# Without report generation
make eval-no-report ENV=development
```

Reports are generated in `evals/reports/` with timestamps.

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login and get JWT token
- `POST /api/v1/auth/logout` - Logout

### Chat
- `POST /api/v1/chatbot/chat` - Send message
- `POST /api/v1/chatbot/chat/stream` - Streaming response
- `GET /api/v1/chatbot/history` - Get history
- `DELETE /api/v1/chatbot/history` - Clear history

### Monitoring
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

Full API documentation available at `/docs` (Swagger) or `/redoc` (ReDoc).

## 📚 Project Structure

```
app/
├── api/v1/          # API routes
├── agents/          # LangGraph agents and tools
├── core/            # Config, logging, metrics, middleware
├── models/          # SQLModel database models
├── schemas/         # Pydantic schemas
├── services/        # Business logic (LLM, database)
└── utils/           # Utility functions
migrations/          # Alembic migrations
evals/               # Model evaluation framework
```

## 🛡️ Security

See [SECURITY.md](SECURITY.md) for security policies and reporting.

## 📄 License

See [LICENSE](LICENSE) for license terms.

## 🤝 Contributing

1. Follow project coding standards
2. Ensure all tests pass
3. Update documentation
4. Use conventional commits
