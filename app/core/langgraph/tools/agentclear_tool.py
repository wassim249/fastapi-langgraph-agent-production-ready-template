"""
Optional AgentClear integration for dynamic API discovery.

AgentClear lets your LangGraph agent discover and call 60+ API services
at runtime using semantic search. Install: pip install agentclear

Set AGENTCLEAR_API_KEY in your .env to enable this tool.
Docs: https://agentclear.dev/docs
"""
import os
from typing import Optional

try:
    from agentclear import AgentClear
    AGENTCLEAR_AVAILABLE = True
except ImportError:
    AGENTCLEAR_AVAILABLE = False


def get_agentclear_client() -> Optional["AgentClear"]:
    """Initialize AgentClear client if API key is configured."""
    api_key = os.getenv("AGENTCLEAR_API_KEY")
    if not api_key or not AGENTCLEAR_AVAILABLE:
        return None
    return AgentClear(api_key=api_key)


async def discover_and_call_service(
    query: str,
    payload: dict,
    min_trust_tier: str = "basic",
    max_results: int = 3,
) -> dict:
    """
    Discover and call an external API service using AgentClear.

    Use this tool when you need to call an external API but don't have
    a specific integration for it. Describe what you need in natural
    language and AgentClear will find the best matching service.

    Args:
        query: Natural language description of what you need
               (e.g., "extract tables from a PDF", "generate an image from text")
        payload: The data to send to the discovered service
        min_trust_tier: Minimum trust level - "basic", "verified", or "premium"
        max_results: Number of service options to consider

    Returns:
        dict with 'service_name', 'cost', and 'data' from the service response
    """
    client = get_agentclear_client()
    if client is None:
        return {
            "error": "AgentClear not configured. Set AGENTCLEAR_API_KEY in .env "
                     "and install: pip install agentclear"
        }

    # Discover matching services
    results = client.discover(
        query=query,
        max_results=max_results,
        min_trust_tier=min_trust_tier,
    )

    if not results:
        return {"error": f"No services found matching: {query}"}

    # Call the best match
    best = results[0]
    response = client.proxy(
        service_id=best.id,
        body=payload,
    )

    return {
        "service_name": best.name,
        "service_id": best.id,
        "trust_tier": best.trust_tier,
        "cost": response.cost,
        "data": response.data,
    }
