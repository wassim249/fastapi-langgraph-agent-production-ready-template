"""A failed graph run must not be mistaken for a human-in-the-loop interrupt.

When a node raises, LangGraph leaves the failed node in ``state.next``. The
agent used to treat any non-empty ``state.next`` as an ``ask_human`` pause, so
the user's next message was passed to ``Command(resume=...)``: it was dropped
from the history and the agent answered the previous message again.
"""

import asyncio
from typing import (
    Any,
    AsyncIterator,
)

import pytest
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

import app.core.langgraph.graph as graph_module
from app.core.langgraph.graph import LangGraphAgent
from app.schemas import Message


class _InMemoryCheckpointer(InMemorySaver):
    """In-memory stand-in for ``AsyncPostgresSaver``."""

    def __init__(self, _pool: Any = None):
        super().__init__()

    async def setup(self) -> None:
        """Nothing to create for the in-memory saver."""


class FakeLLM:
    """Scripted replacement for ``llm_service.call``.

    Each entry of ``script`` is used for one call: an exception is raised, a
    ``dict`` is returned as a tool call, and ``None`` answers the latest user
    message.
    """

    def __init__(self, script: list[Any]):
        """Store the script and record every call's messages."""
        self.script = list(script)
        self.calls: list[list[dict]] = []

    async def __call__(self, messages: list[dict], *args: Any, **kwargs: Any) -> AIMessage:
        """Play the next scripted step."""
        self.calls.append(messages)
        # Like real providers, reject a history with tool calls that have no tool result.
        answered = {m["tool_call_id"] for m in messages if m.get("type") == "tool"}
        requested = {c["id"] for m in messages if m.get("type") == "ai" for c in m.get("tool_calls") or []}
        if requested - answered:
            raise ValueError("tool_calls must be followed by tool messages")
        step = self.script.pop(0) if self.script else None
        if isinstance(step, Exception):
            raise step
        if isinstance(step, dict):
            return AIMessage(content="", tool_calls=[{"id": "call_1", **step}])
        if isinstance(step, list):
            return AIMessage(content="", tool_calls=[{"id": f"call_{i}", **call} for i, call in enumerate(step, 1)])
        last_user = next(m["content"] for m in reversed(messages) if m.get("type") == "human")
        return AIMessage(content=f"answer to: {last_user}")


class ToolBackendError(Exception):
    """Transient tool error that LangGraph's default RetryPolicy retries."""


tool_attempts: list[str] = []


@tool
def flaky_tool(query: str) -> str:
    """Tool that always fails."""
    tool_attempts.append(query)
    raise ToolBackendError("tool backend down")


broken_tool_calls: list[str] = []


@tool
def broken_tool(query: str) -> str:
    """Tool that works once, then breaks; RuntimeError is not retried by the default RetryPolicy.

    Succeeding on the first call keeps the parallel test independent of the
    order in which the tool calls finish.
    """
    broken_tool_calls.append(query)
    if len(broken_tool_calls) > 1:
        raise RuntimeError("tool is broken")
    return "ok"


async def _no_sleep(_delay: float) -> None:
    return None


@pytest.fixture
def agent(monkeypatch: pytest.MonkeyPatch) -> LangGraphAgent:
    """Agent with the real graph wiring, an in-memory checkpointer and no external services."""
    monkeypatch.setattr(graph_module, "AsyncPostgresSaver", _InMemoryCheckpointer)
    monkeypatch.setattr(graph_module.settings, "LANGFUSE_TRACING_ENABLED", False)
    agent = LangGraphAgent()

    async def _no_pool() -> None:
        return None

    monkeypatch.setattr(agent, "_get_connection_pool", _no_pool)
    # Keep the tool node's RetryPolicy from sleeping between attempts.
    monkeypatch.setattr("langgraph.pregel._retry.asyncio.sleep", _no_sleep)
    agent.tools_by_name["flaky_tool"] = flaky_tool
    agent.tools_by_name["broken_tool"] = broken_tool
    tool_attempts.clear()
    broken_tool_calls.clear()
    return agent


def _use_llm(monkeypatch: pytest.MonkeyPatch, agent: LangGraphAgent, script: list[Any]) -> FakeLLM:
    fake = FakeLLM(script)
    monkeypatch.setattr(agent.llm_service, "call", fake)
    return fake


def _user(content: str) -> list[Message]:
    return [Message(role="user", content=content)]


async def _collect(stream: AsyncIterator[str]) -> str:
    return "".join([chunk async for chunk in stream])


def test_new_message_after_failed_llm_call_is_answered(monkeypatch: pytest.MonkeyPatch, agent: LangGraphAgent):
    """After the LLM fails, the next message starts a new run instead of resuming the failed one."""
    _use_llm(monkeypatch, agent, [RuntimeError("all models failed")])

    async def scenario() -> tuple[list[Message], list[Message]]:
        with pytest.raises(Exception, match="all models failed"):
            await agent.get_response(_user("first question"), "s1")
        reply = await agent.get_response(_user("second question"), "s1")
        return reply, await agent.get_chat_history("s1")

    reply, history = asyncio.run(scenario())

    assert reply[-1].content == "answer to: second question"
    assert [m.content for m in history if m.role == "user"] == ["first question", "second question"]


def test_new_message_after_failed_tool_call_is_answered(monkeypatch: pytest.MonkeyPatch, agent: LangGraphAgent):
    """After a tool fails, its dangling call is closed with an error result and the new message is answered."""
    llm = _use_llm(monkeypatch, agent, [{"name": "flaky_tool", "args": {"query": "x"}}])

    async def scenario() -> list[Message]:
        with pytest.raises(ToolBackendError):
            await agent.get_response(_user("search something"), "s2")
        return await agent.get_response(_user("never mind, say hi"), "s2")

    reply = asyncio.run(scenario())

    assert reply[-1].content == "answer to: never mind, say hi"
    # The failed run used up the node's RetryPolicy and was not re-run by the new message.
    assert len(tool_attempts) == 3
    # The dangling tool call was closed with an error result, so the history
    # sent to the provider is valid (every tool call has a tool message).
    sent = llm.calls[-1]
    tool_results = [m for m in sent if m.get("type") == "tool"]
    assert len(tool_results) == 1
    assert tool_results[0]["tool_call_id"] == "call_1"
    assert tool_results[0]["status"] == "error"


def test_stream_after_failed_llm_call_answers_new_message(monkeypatch: pytest.MonkeyPatch, agent: LangGraphAgent):
    """The streaming endpoint makes the same decision as the non-streaming one."""
    _use_llm(monkeypatch, agent, [RuntimeError("all models failed")])

    async def scenario() -> str:
        with pytest.raises(Exception, match="all models failed"):
            await _collect(agent.get_stream_response(_user("first question"), "s3"))
        return await _collect(agent.get_stream_response(_user("second question"), "s3"))

    assert asyncio.run(scenario()) == "answer to: second question"


def test_ask_human_interrupt_is_still_resumed(monkeypatch: pytest.MonkeyPatch, agent: LangGraphAgent):
    """A real ask_human interrupt still takes the next message as its answer."""
    llm = _use_llm(monkeypatch, agent, [{"name": "ask_human", "args": {"question": "Delete all files?"}}])

    async def scenario() -> tuple[list[Message], list[Message]]:
        question = await agent.get_response(_user("delete my files"), "s4")
        reply = await agent.get_response(_user("yes"), "s4")
        return question, reply

    question, reply = asyncio.run(scenario())

    assert question[-1].content == "Delete all files?"
    # "yes" went to the paused tool, not into the history as a new user turn,
    # so the follow-up LLM call still sees the original request as latest.
    assert reply[-1].content == "answer to: delete my files"
    assert [m["content"] for m in llm.calls[-1] if m.get("type") == "tool"] == ["yes"]


def test_tool_failure_after_answered_interrupt_is_not_resumed(monkeypatch: pytest.MonkeyPatch, agent: LangGraphAgent):
    """An answered ask_human followed by a tool failure in the same step does not trap the session."""
    calls = [
        {"name": "ask_human", "args": {"question": "Delete all files?"}},
        {"name": "broken_tool", "args": {"query": "x"}},
    ]
    _use_llm(monkeypatch, agent, [calls])

    async def scenario() -> tuple[list[Message], list[Message]]:
        question = await agent.get_response(_user("delete my files and search"), "s5")
        # The answered interrupt stays listed next to the task error after this.
        with pytest.raises(RuntimeError, match="tool is broken"):
            await agent.get_response(_user("yes"), "s5")
        reply = await agent.get_response(_user("new topic"), "s5")
        return question, reply

    question, reply = asyncio.run(scenario())

    assert question[-1].content == "Delete all files?"
    assert reply[-1].content == "answer to: new topic"
