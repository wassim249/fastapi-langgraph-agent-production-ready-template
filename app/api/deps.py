"""API dependencies for authentication and database sessions."""

from fastapi import (
    Depends,
    HTTPException,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.agents.logging import (
    bind_context,
    logger,
)
from app.models.session import Session as ChatSession
from app.services.db_session import get_async_session
from app.utils.auth import verify_token
from app.utils.sanitization import sanitize_string

security = HTTPBearer()


async def get_current_session_async(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db_session: AsyncSession = Depends(get_async_session),
) -> ChatSession:
    """Validate token and load the current chat session using async DB access."""
    try:
        token = sanitize_string(credentials.credentials)

        session_id = verify_token(token)
        if session_id is None:
            logger.error("session_id_not_found", token_part=token[:10] + "...")
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        session_id = sanitize_string(session_id)

        result = await db_session.exec(select(ChatSession).where(ChatSession.id == session_id))
        chat_session = result.first()
        if chat_session is None:
            logger.error("session_not_found", session_id=session_id)
            raise HTTPException(
                status_code=404,
                detail="Session not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        bind_context(user_id=chat_session.user_id)

        return chat_session
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("session_authentication_failed", error=str(exc))
        raise HTTPException(
            status_code=500,
            detail="Authentication failed",
        )
