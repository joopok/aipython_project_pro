from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.routers.users import get_current_user
from app.schemas.user import User

router = APIRouter()

@router.get("/public", status_code=status.HTTP_200_OK)
async def get_public_data() -> Dict[str, Any]:
    """
    인증이 필요없는 공개 API
    """
    return {
        "message": "이것은 공개 API입니다. 인증이 필요하지 않습니다.",
        "data": {
            "sample": "공개 데이터",
            "items": ["항목1", "항목2", "항목3"]
        }
    }

@router.get("/private", status_code=status.HTTP_200_OK)
async def get_private_data(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    인증이 필요한 비공개 API
    """
    return {
        "message": "인증된 사용자를 위한 비공개 API입니다.",
        "user": current_user.username,
        "data": {
            "sample": "비공개 데이터",
            "items": ["비공개1", "비공개2", "비공개3"]
        }
    }

@router.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(item: Dict[str, Any], current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    새 항목 생성 API (POST 요청 예시)
    """
    # 항목 생성 로직
    item["owner"] = current_user.username
    item["id"] = 1  # 실제로는 DB에서 자동 생성될 ID
    
    return {
        "message": "항목이 생성되었습니다.",
        "item": item
    } 