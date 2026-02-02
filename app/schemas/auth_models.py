"""Auth domain schemas for integer user/session tables."""

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class AuthUserBase(SQLModel):
    email: str
    hashed_password: str


class AuthUserCreate(AuthUserBase):
    pass


class AuthUserUpdate(SQLModel):
    email: Optional[str] = None
    hashed_password: Optional[str] = None


class AuthUserRead(AuthUserBase):
    id: int
    created_at: datetime


class AuthSessionBase(SQLModel):
    id: str
    user_id: int
    name: str = ""


class AuthSessionCreate(AuthSessionBase):
    pass


class AuthSessionUpdate(SQLModel):
    user_id: Optional[int] = None
    name: Optional[str] = None


class AuthSessionRead(AuthSessionBase):
    created_at: datetime
