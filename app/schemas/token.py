from pydantic import BaseModel

from app.core.enums import RoleEnum


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  # user_id (login id)
    role: RoleEnum
    exp: int | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str
