"""Custom middleware for tracking metrics and other cross-cutting concerns."""

import json
import time
import tracemalloc
from typing import (
    TYPE_CHECKING,
    Callable,
    override,
)

from asgi_correlation_id import correlation_id
from fastapi import Request
from jose import (
    JWTError,
    jwt,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import settings
from app.core.logging import (
    bind_context,
    clear_context,
    logger,
)
from app.core.metrics import (
    http_request_duration_seconds,
    http_requests_total,
)

if TYPE_CHECKING:
    from pyinstrument import Profiler  # pyright: ignore[reportMissingImports]
    from pyinstrument.renderers import JSONRenderer  # pyright: ignore[reportMissingImports]

    PYINSTRUMENT_AVAILABLE = True
else:
    try:
        from pyinstrument import Profiler
        from pyinstrument.renderers import JSONRenderer

        PYINSTRUMENT_AVAILABLE = True
    except ImportError:
        Profiler = None
        JSONRenderer = None
        PYINSTRUMENT_AVAILABLE = False


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking HTTP request metrics."""

    @override
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Track metrics for each request.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            Response: The response from the application
        """
        start_time = time.time()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            raise
        finally:
            duration = time.time() - start_time

            # Record metrics
            http_requests_total.labels(method=request.method, endpoint=request.url.path, status=status_code).inc()

            http_request_duration_seconds.labels(method=request.method, endpoint=request.url.path).observe(duration)

        return response


class LoggingContextMiddleware(BaseHTTPMiddleware):
    """Middleware for adding user_id and session_id to logging context."""

    @override
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Extract user_id and session_id from authenticated requests and add to logging context.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            Response: The response from the application
        """
        try:
            # Clear any existing context from previous requests
            clear_context()

            # Extract token from Authorization header
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

                try:
                    # Decode token to get session_id (stored in "sub" claim)
                    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
                    session_id = payload.get("sub")

                    if session_id:
                        # Bind session_id to logging context
                        bind_context(session_id=session_id)

                        # Try to get user_id from request state after authentication
                        # This will be set by the dependency injection if the endpoint uses authentication
                        # We'll check after the request is processed

                except JWTError:
                    # Token is invalid, but don't fail the request - let the auth dependency handle it
                    pass

            # Process the request
            response = await call_next(request)

            # After request processing, check if user info was added to request state
            if hasattr(request.state, "user_id"):
                bind_context(user_id=request.state.user_id)

            return response

        finally:
            # Always clear context after request is complete to avoid leaking to other requests
            clear_context()


class ProfilingMiddleware(BaseHTTPMiddleware):
    """Automatic per-request profiling middleware using pyinstrument.

    Only active when DEBUG=true. Profiles every request and saves an HTML
    flamegraph to PROFILING_DIR when the request exceeds
    PROFILING_THRESHOLD_SECONDS. Files are named {request_id}.html so they
    can be correlated with logs. /tmp is cleaned up automatically by the OS.
    """

    @override
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Profile every request; save enriched JSON if duration exceeds threshold."""
        if not PYINSTRUMENT_AVAILABLE:
            return await call_next(request)

        # Start all three profilers
        tracemalloc.start()
        cpu_start = time.process_time()

        profiler = Profiler(async_mode="enabled")
        with profiler:
            response = await call_next(request)

        # Capture metrics immediately after the request
        cpu_ms = round((time.process_time() - cpu_start) * 1000, 2)
        mem_current_kb, mem_peak_kb = (v // 1024 for v in tracemalloc.get_traced_memory())
        snapshot = tracemalloc.take_snapshot()
        tracemalloc.stop()

        wall_ms = round((profiler.last_session.duration if profiler.last_session else 0.0) * 1000, 2)

        if wall_ms / 1000 >= settings.PROFILING_THRESHOLD_SECONDS:
            raw_id = correlation_id.get() or "unknown"
            if len(raw_id) == 32 and "-" not in raw_id:
                raw_id = f"{raw_id[:8]}-{raw_id[8:12]}-{raw_id[12:16]}-{raw_id[16:20]}-{raw_id[20:]}"

            settings.PROFILING_DIR.mkdir(parents=True, exist_ok=True)
            filepath = settings.PROFILING_DIR / f"{raw_id}.json"

            # Top 20 memory allocators — exclude profiler and stdlib noise
            _excluded = ("tracemalloc", "pyinstrument", "<frozen", "logging/__init__")
            top_allocs = [
                {
                    "file": str(stat.traceback[0].filename).replace(str(__file__).rsplit("/", 3)[0] + "/", ""),
                    "line": stat.traceback[0].lineno,
                    "size_kb": round(stat.size / 1024, 2),
                    "count": stat.count,
                }
                for stat in snapshot.statistics("lineno")
                if not any(ex in str(stat.traceback[0].filename) for ex in _excluded)
            ]

            call_tree = json.loads(profiler.output(renderer=JSONRenderer()))
            report = {
                "request_id": raw_id,
                "endpoint": f"{request.method} {request.url.path}",
                "wall_time_ms": wall_ms,
                "cpu_time_ms": cpu_ms,
                "io_wait_ms": round(wall_ms - cpu_ms, 2),
                "memory_peak_kb": mem_peak_kb,
                "memory_allocated_kb": mem_current_kb,
                "top_memory_allocators": top_allocs,
                "call_tree": call_tree,
            }
            filepath.write_text(json.dumps(report, indent=2))
            logger.debug(
                "slow_request_profile_saved",
                path=request.url.path,
                method=request.method,
                wall_time_ms=wall_ms,
                cpu_time_ms=cpu_ms,
                memory_peak_kb=mem_peak_kb,
                io_wait_ms=round(wall_ms - cpu_ms, 2),
                profile_file=str(filepath),
            )

        return response
