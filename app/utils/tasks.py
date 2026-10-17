"""This file contains the background task utilities for the application."""

import asyncio
from typing import (
    Any,
    Coroutine,
)

_background_tasks: set[asyncio.Task] = set()


def create_background_task(coro: Coroutine[Any, Any, Any]) -> None:
    """Run a coroutine as a fire-and-forget task and keep a reference to it until it finishes.

    The event loop only keeps weak references to tasks, so a task nothing else holds
    can be garbage-collected before it completes.

    Args:
        coro: The coroutine to run in the background
    """
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
