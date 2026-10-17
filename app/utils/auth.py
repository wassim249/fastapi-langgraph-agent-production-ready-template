"""This file contains the authentication utilities for the application."""

import re
from datetime import (
    UTC,
    datetime,
    timedelta,
)
from typing import Optional

from jose import (
    JWTError,
    jwt,
)

from app.core.config import settings
from app.core.logging import logger
from app.schemas.auth import Token
from app.utils.sanitization import sanitize_string


def create_access_token(thread_id: str, expires_delta: Optional[timedelta] = None) -> Token:
    """Create a new access token for a thread.

    Args:
        thread_id: The unique thread ID for the conversation.
        expires_delta: Optional expiration time delta.

    Returns:
        Token: The generated access token.
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=settings.JWT_ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": thread_id,
        "exp": expire,
        "iat": datetime.now(UTC),
        "jti": sanitize_string(f"{thread_id}-{datetime.now(UTC).timestamp()}"),  # Add unique token identifier
    }

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    logger.info("token_created", thread_id=thread_id, expires_at=expire.isoformat())

    return Token(access_token=encoded_jwt, expires_at=expire)


def verify_token(token: str) -> Optional[str]:
    """Verify a JWT token and return the thread ID.

    Args:
        token: The JWT token to verify.

    Returns:
        Optional[str]: The thread ID if token is valid, None otherwise.

    Raises:
        ValueError: If the token format is invalid
    """
    if not token or not isinstance(token, str):
        logger.warning("token_invalid_format")
        raise ValueError("Token must be a non-empty string")

    # Basic format validation before attempting decode
    # JWT tokens consist of 3 base64url-encoded segments separated by dots
    if not re.match(r"^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$", token):
        logger.warning("token_suspicious_format")
        raise ValueError("Token format is invalid - expected JWT format")

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        thread_id: str | None = payload.get("sub")
        if thread_id is None:
            logger.warning("token_missing_thread_id")
            return None

        logger.info("token_verified", thread_id=thread_id)
        return thread_id

    except JWTError as e:
        logger.error("token_verification_failed", error=str(e))
        return None
