"""LangGraph tools for enhanced language model capabilities.

This package contains custom tools that can be used with LangGraph to extend
the capabilities of language models. Currently includes tools for web search
and other external integrations.
"""

from langchain_core.tools.base import BaseTool

from .duckduckgo_search import duckduckgo_search_tool

# Tools used by the HTTP/LangGraph chat agent.
# Phone-agent tools live in `booking.py` and `livekit_core.py` and are wired directly into the LiveKit Agent.
tools: list[BaseTool] = [duckduckgo_search_tool]
