from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.token import RefreshTokenRequest, Token
from app.schemas.user import UserOut, UserRegisterRequest
from app.services import auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register", response_model=ResponseModel[UserOut], status_code=status.HTTP_201_CREATED)
def register(data: UserRegisterRequest, db: Session = Depends(get_db)):
    user = auth_service.register_student(db, data)
    return ResponseModel(
        message="Registration successful. Your account is pending admin approval.",
        data=UserOut.model_validate(user),
    )


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 password flow. `username` field = User ID, `password` = Password."""
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    return auth_service.create_tokens_for_user(user)


@router.post("/refresh", response_model=Token)
def refresh(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    return auth_service.refresh_access_token(db, data.refresh_token)


@router.get("/me", response_model=ResponseModel[UserOut])
def get_me(current_user: User = Depends(get_current_user)):
    return ResponseModel(data=UserOut.model_validate(current_user))
