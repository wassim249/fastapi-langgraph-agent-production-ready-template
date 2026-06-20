"""Helpers for managing fire-and-forget asyncio tasks."""

import asyncio
from collections.abc import Coroutine
from typing import Any

_background_tasks: set[asyncio.Task] = set()


def spawn_background_task(coro: Coroutine[Any, Any, Any]) -> asyncio.Task:
    """Schedule a fire-and-forget coroutine while retaining a strong reference.

    Args:
        coro: The coroutine to run in the background.

    Returns:
        The scheduled task. Callers may ignore it; the reference is held
        internally until the task completes.
    """
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return task
