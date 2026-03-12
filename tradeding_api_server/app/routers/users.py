from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt

from app.core.config import SECRET_KEY, ALGORITHM
from app.models.user import create_user, get_user_by_email, get_user_by_id
from app.routers.auth import oauth2_scheme
from app.schemas.user import TokenPayload, User, UserCreate

router = APIRouter()

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    현재 인증된 사용자 정보 조회
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증이 유효하지 않습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 토큰 디코딩
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenPayload(sub=email)
    except JWTError:
        raise credentials_exception
    
    # 사용자 조회
    user = get_user_by_email(email=token_data.sub)
    if user is None:
        raise credentials_exception
    
    return User(
        id=user.id,
        email=user.email,
        username=user.username,
        is_active=user.is_active
    )

@router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate) -> Any:
    """
    새 사용자 등록
    """
    # 이메일 중복 확인
    user = get_user_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다"
        )
    
    # 새 사용자 생성
    user = create_user(user_in=user_in)
    
    return User(
        id=user.id,
        email=user.email,
        username=user.username,
        is_active=user.is_active
    )

@router.get("/users/me", response_model=User)
async def read_current_user(current_user: User = Depends(get_current_user)) -> Any:
    """
    현재 로그인한 사용자 정보 조회
    """
    return current_user 