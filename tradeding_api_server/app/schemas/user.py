from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    """
    기본 사용자 정보
    """
    email: EmailStr
    username: str

class UserCreate(UserBase):
    """
    사용자 생성 시 필요한 정보
    """
    password: str

class UserInDB(UserBase):
    """
    데이터베이스에 저장되는 사용자 정보
    """
    id: int
    hashed_password: str
    is_active: bool = True

class User(UserBase):
    """
    API 응답용 사용자 정보
    """
    id: int
    is_active: bool

class Token(BaseModel):
    """
    토큰 응답 모델
    """
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    """
    토큰 페이로드 모델
    """
    sub: Optional[str] = None 