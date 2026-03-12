from typing import Dict, List, Optional

from app.core.security import get_password_hash
from app.schemas.user import UserCreate, UserInDB

# 임시 데이터베이스 대용으로 사용하는 딕셔너리
fake_users_db: Dict[int, UserInDB] = {
    1: UserInDB(
        id=1,
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        is_active=True
    )
}

def get_user_by_email(email: str) -> Optional[UserInDB]:
    """
    이메일로 사용자 조회
    """
    for user in fake_users_db.values():
        if user.email == email:
            return user
    return None

def get_user_by_id(user_id: int) -> Optional[UserInDB]:
    """
    ID로 사용자 조회
    """
    if user_id in fake_users_db:
        return fake_users_db[user_id]
    return None

def create_user(user_in: UserCreate) -> UserInDB:
    """
    새 사용자 생성
    """
    # 새 사용자 ID 생성
    user_id = max(fake_users_db.keys()) + 1 if fake_users_db else 1
    
    # 비밀번호 해시화
    hashed_password = get_password_hash(user_in.password)
    
    # 사용자 생성
    user = UserInDB(
        id=user_id,
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password,
        is_active=True
    )
    
    # 임시 DB에 저장
    fake_users_db[user_id] = user
    
    return user 