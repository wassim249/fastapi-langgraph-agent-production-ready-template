"""Pytest fixtures for API tests."""

from __future__ import annotations

from typing import AsyncIterator, Dict, Iterator, List, Optional, Type
from uuid import uuid4

import httpx
import pytest
from sqlalchemy.sql import operators
from sqlalchemy.sql.elements import BindParameter, BinaryExpression
from sqlmodel import SQLModel

from app.api.deps import get_current_session_async
from app.api.v1 import auth as auth_module
from app.api.v1 import chatbot as chatbot_module
from app.agents.limiter import limiter
from app.main import app
from app.models.session import Session as ChatSession
from app.models.user import User
from app.services.db_session import get_async_session


class InMemoryStore:
    """Simple in-memory store keyed by model and ID."""

    def __init__(self) -> None:
        self._data: Dict[Type[SQLModel], Dict[str, SQLModel]] = {}
        self._counters: Dict[Type[SQLModel], int] = {}

    def add(self, record: SQLModel) -> None:
        model = type(record)
        if getattr(record, "id", None) is None:
            if getattr(record, "__annotations__", {}).get("id") is int:
                next_id = self._counters.get(model, 1)
                record.id = next_id
                self._counters[model] = next_id + 1
            else:
                record.id = str(uuid4())
        self._data.setdefault(model, {})[str(record.id)] = record

    def delete(self, record: SQLModel) -> None:
        model = type(record)
        self._data.get(model, {}).pop(str(record.id), None)

    def list(self, model: Type[SQLModel]) -> List[SQLModel]:
        return list(self._data.get(model, {}).values())

    def get(self, model: Type[SQLModel], record_id: str) -> Optional[SQLModel]:
        return self._data.get(model, {}).get(str(record_id))


class FakeResult:
    def __init__(self, records: List[SQLModel]):
        self._records = records

    def all(self) -> List[SQLModel]:
        return list(self._records)

    def first(self) -> Optional[SQLModel]:
        return self._records[0] if self._records else None


class FakeAsyncSession:
    """Minimal async session for CRUD tests."""

    def __init__(self, store: InMemoryStore):
        self._store = store

    async def exec(self, stmt):
        model = stmt.column_descriptions[0].get("entity")
        records = self._store.list(model)
        records = self._apply_where(stmt, records)
        records = self._apply_offset_limit(stmt, records)
        return FakeResult(records)

    def add(self, record: SQLModel) -> None:
        self._store.add(record)

    async def commit(self) -> None:
        return None

    async def refresh(self, record: SQLModel) -> None:
        return None

    def delete(self, record: SQLModel) -> None:
        self._store.delete(record)

    def _apply_where(self, stmt, records: List[SQLModel]) -> List[SQLModel]:
        for criterion in getattr(stmt, "_where_criteria", ()):
            if isinstance(criterion, BinaryExpression) and criterion.operator is operators.eq:
                left = criterion.left
                right = criterion.right
                if getattr(left, "name", None) == "id":
                    value = right.value if isinstance(right, BindParameter) else right
                    records = [record for record in records if self._ids_equal(record.id, value)]
        return records

    @staticmethod
    def _ids_equal(left, right) -> bool:
        if isinstance(left, int) or isinstance(right, int):
            try:
                return int(left) == int(right)
            except (TypeError, ValueError):
                return False
        return str(left) == str(right)

    def _apply_offset_limit(self, stmt, records: List[SQLModel]) -> List[SQLModel]:
        offset_clause = getattr(stmt, "_offset_clause", None)
        limit_clause = getattr(stmt, "_limit_clause", None)
        offset = offset_clause.value if isinstance(offset_clause, BindParameter) else offset_clause
        limit = limit_clause.value if isinstance(limit_clause, BindParameter) else limit_clause
        if offset:
            records = records[int(offset) :]
        if limit:
            records = records[: int(limit)]
        return records


class TestDatabaseService:
    """Database service for tests using in-memory data."""

    def __init__(self) -> None:
        self._users: Dict[int, User] = {}
        self._sessions: Dict[str, ChatSession] = {}
        self._next_user_id = 1

    async def create_user(self, email: str, password: str) -> User:
        user = User(id=self._next_user_id, email=email, hashed_password=password)
        self._users[user.id] = user
        self._next_user_id += 1
        return user

    async def get_user(self, user_id: int) -> User | None:
        return self._users.get(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    async def delete_user_by_email(self, email: str) -> bool:
        for user_id, user in list(self._users.items()):
            if user.email == email:
                del self._users[user_id]
                return True
        return False

    async def create_session(self, session_id: str, user_id: int, name: str = "") -> ChatSession:
        chat_session = ChatSession(id=session_id, user_id=user_id, name=name)
        self._sessions[session_id] = chat_session
        return chat_session

    async def delete_session(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None

    async def get_session(self, session_id: str) -> ChatSession | None:
        return self._sessions.get(session_id)

    async def get_user_sessions(self, user_id: int) -> list[ChatSession]:
        return [session for session in self._sessions.values() if session.user_id == user_id]

    async def update_session_name(self, session_id: str, name: str) -> ChatSession:
        session = self._sessions[session_id]
        session.name = name
        return session


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    """Create an async HTTP client bound to the FastAPI app."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client


@pytest.fixture
def store() -> InMemoryStore:
    return InMemoryStore()


@pytest.fixture
def auth_db_service() -> TestDatabaseService:
    return TestDatabaseService()


@pytest.fixture
def app_with_overrides(store, auth_db_service) -> Iterator:
    async def override_get_async_session() -> AsyncIterator[FakeAsyncSession]:
        yield FakeAsyncSession(store)

    async def override_current_session() -> ChatSession:
        return ChatSession(id=str(uuid4()), user_id=1, name="")

    app.dependency_overrides[get_async_session] = override_get_async_session
    app.dependency_overrides[get_current_session_async] = override_current_session

    original_db_service = auth_module.db_service
    original_agent = chatbot_module.agent
    limiter_enabled = getattr(limiter, "enabled", True)
    limiter.enabled = False
    auth_module.db_service = auth_db_service
    chatbot_module.agent = FakeChatAgent()
    try:
        yield app
    finally:
        auth_module.db_service = original_db_service
        chatbot_module.agent = original_agent
        limiter.enabled = limiter_enabled
        app.dependency_overrides.clear()


class FakeChatAgent:
    async def get_response(self, messages, session_id, user_id=None):
        return messages + [{"role": "assistant", "content": "test-response"}]

    async def get_stream_response(self, messages, session_id, user_id=None):
        for chunk in ["hello", "world"]:
            yield chunk

    async def get_chat_history(self, session_id):
        return [{"role": "assistant", "content": "history"}]

    async def clear_chat_history(self, session_id):
        return None


@pytest.fixture
async def db_client(app_with_overrides) -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app_with_overrides)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
