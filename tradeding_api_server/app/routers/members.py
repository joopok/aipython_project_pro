from typing import Any, Dict, List, Optional
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, Form, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, validator

from app.core.db_maridb import create_connection, close_connection, execute_query
from app.routers.users import get_current_user
from app.schemas.user import User
from app.core.security import get_password_hash, verify_password, create_access_token

# 로거 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_query(query: str, params: tuple = None, result: Any = None) -> None:
    """
    DB 쿼리 실행 정보를 로깅합니다.
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"\n{'='*50}")
    logger.info(f"[{current_time}] 쿼리 실행")
    logger.info(f"Query: {query}")
    logger.info(f"Parameters: {params}")
    logger.info(f"Result: {result}")
    logger.info(f"{'='*50}\n")

router = APIRouter()

class MemberBase(BaseModel):
    """회원 기본 정보"""
    id: int
    username: str
    email: str
    full_name: str
    role: Optional[int] = None
    is_active: bool

class MemberPublic(BaseModel):
    """공개 회원 정보"""
    id: int
    username: str
    email: str
    role: Optional[int] = None
    is_active: bool

class MemberResponse(BaseModel):
    """회원 정보 응답 모델"""
    status: str
    message: str
    data: List[MemberBase]

class MemberPublicResponse(BaseModel):
    """공개 회원 정보 응답 모델"""
    status: str
    message: str
    data: List[MemberPublic]

class TableInfo(BaseModel):
    """테이블 정보 모델"""
    Field: str
    Type: str
    Null: str
    Key: str
    Default: str = None
    Extra: str = None

class TableInfoResponse(BaseModel):
    """테이블 정보 응답 모델"""
    status: str
    message: str
    table_name: str
    columns: List[TableInfo]

class UserCreate(BaseModel):
    """사용자 생성 요청 모델"""
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: str = "user"

class LoginResponse(BaseModel):
    """로그인 응답 모델"""
    status: str
    message: str
    access_token: Optional[str] = None
    token_type: Optional[str] = None

class LoginRequest(BaseModel):
    """로그인 요청 모델"""
    username: Optional[str] = None  # 이메일 주소도 여기 입력
    email: Optional[EmailStr] = None  # username 대신 사용 가능
    password: str
    
    @validator('username', 'email')
    def validate_username_or_email(cls, v, values):
        # username 또는 email 중 하나는 반드시 있어야 함
        username = values.get('username')
        email = values.get('email')
        if not username and not email:
            raise ValueError('username 또는 email은 필수입니다')
        return v

@router.get("/members/public", response_model=MemberPublicResponse)
async def get_public_members(
    skip: int = Query(default=0, description="건너뛸 레코드 수"),
    limit: int = Query(default=10, description="가져올 레코드 수"),
    search: Optional[str] = Query(None, description="검색어")
) -> Any:
    """
    활성화된 회원의 기본 정보를 조회합니다. 인증이 필요하지 않습니다.
    """
    conn, info = create_connection()
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=info["message"]
        )
    
    try:
        # 기본 쿼리
        query = """
        SELECT 
            user_id as id, 
            username,
            email,
            role_id as role,
            is_active
        FROM users
        WHERE is_active = TRUE
        """
        params = []
        
        # 검색 조건 추가
        if search:
            query += """ AND (
                username LIKE %s 
                OR email LIKE %s
            )"""
            search_term = f"%{search}%"
            params.extend([search_term, search_term])
        
        # 정렬 추가
        query += " ORDER BY id DESC"
        
        # 페이지네이션 추가
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, skip])
        
        success, result = execute_query(conn, query, tuple(params) if params else None)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result
            )
        
        # 전체 레코드 수 조회
        count_query = "SELECT COUNT(*) as total FROM users WHERE is_active = TRUE"
        count_success, count_result = execute_query(conn, count_query)
        
        total_count = count_result[0]['total'] if count_success else 0
        
        return {
            "status": "success",
            "message": f"활성화된 회원 {len(result)}명의 정보를 조회했습니다. (전체: {total_count}명)",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회원 정보 조회 중 오류 발생: {str(e)}"
        )
    
    finally:
        close_connection(conn)

@router.get("/members", response_model=MemberResponse)
async def get_all_members(
    current_user: User = Depends(get_current_user),
    skip: int = Query(default=0, description="건너뛸 레코드 수"),
    limit: int = Query(default=10, description="가져올 레코드 수"),
    search: Optional[str] = Query(None, description="검색어")
) -> Any:
    """
    전체 회원 정보를 조회합니다.
    """
    conn, info = create_connection()
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=info["message"]
        )
    
    try:
        # 기본 쿼리
        query = """
        SELECT 
            user_id as id, 
            username,
            email,
            username as full_name,
            role_id as role,
            is_active,
            created_at,
            updated_at
        FROM users
        WHERE 1=1
        """
        params = []
        
        # 검색 조건 추가
        if search:
            query += """ AND (
                username LIKE %s 
                OR email LIKE %s
            )"""
            search_term = f"%{search}%"
            params.extend([search_term, search_term])
        
        # 정렬 추가
        query += " ORDER BY id DESC"
        
        # 페이지네이션 추가
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, skip])
        
        success, result = execute_query(conn, query, tuple(params) if params else None)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result
            )
        
        # 전체 레코드 수 조회
        count_query = "SELECT COUNT(*) as total FROM users"
        count_success, count_result = execute_query(conn, count_query)
        
        total_count = count_result[0]['total'] if count_success else 0
        
        return {
            "status": "success",
            "message": f"{len(result)}명의 회원 정보를 조회했습니다. (전체: {total_count}명)",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
    finally:
        close_connection(conn)

@router.get("/members/table-info", response_model=TableInfoResponse)
async def get_users_table_info(current_user: User = Depends(get_current_user)) -> Any:
    """
    users 테이블의 구조 정보를 조회합니다.
    """
    conn, info = create_connection()
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=info["message"]
        )
    
    try:
        # 테이블 구조 조회 쿼리
        query = "DESCRIBE users"
        success, result = execute_query(conn, query)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result
            )
        
        # 결과가 없는 경우
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="users 테이블을 찾을 수 없습니다."
            )
        
        # 테이블 정보 반환
        return {
            "status": "success",
            "message": "users 테이블 구조를 조회했습니다.",
            "table_name": "users",
            "columns": result
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"테이블 정보 조회 중 오류 발생: {str(e)}"
        )
    
    finally:
        close_connection(conn)

@router.get("/members/test-connection", response_model=Dict[str, Any])
async def test_db_connection() -> Any:
    """
    데이터베이스 연결을 테스트합니다.
    """
    # 데이터베이스 연결
    conn, info = create_connection()
    
    # 연결 결과 반환
    response = {
        "status": info["status"],
        "message": info["message"]
    }
    
    # 연결에 성공한 경우 추가 정보 포함
    if conn:
        response["version"] = info.get("version", "")
        response["database"] = info.get("database", "")
        # 데이터베이스 연결 종료
        close_connection(conn)
    
    return response

@router.get("/members/{member_id}", response_model=MemberResponse)
async def get_member_by_id(member_id: int, current_user: User = Depends(get_current_user)) -> Any:
    """
    특정 회원 정보를 가져옵니다.
    """
    # 데이터베이스 연결
    conn, info = create_connection()
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=info["message"]
        )
    
    try:
        # 회원 정보 조회 쿼리
        query = """
        SELECT 
            user_id, 
            username, 
            username1, 
            email, 
            role_id, 
            is_active 
        FROM users
        WHERE user_id = %s
        """
        
        success, result = execute_query(conn, query, (member_id,))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result
            )
        
        # 결과가 없는 경우
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID가 {member_id}인 회원을 찾을 수 없습니다."
            )
        
        # 회원 정보 반환
        return {
            "status": "success",
            "message": f"ID가 {member_id}인 회원 정보를 조회했습니다.",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회원 정보 조회 중 오류 발생: {str(e)}"
        )
    
    finally:
        # 데이터베이스 연결 종료
        close_connection(conn)

@router.get("/users", response_model=MemberResponse)
async def get_all_users(
    current_user: User = Depends(get_current_user),
    skip: int = Query(default=0, description="건너뛸 레코드 수"),
    limit: int = Query(default=10, description="가져올 레코드 수"),
    search: Optional[str] = Query(None, description="검색어"),
    is_active: Optional[bool] = Query(None, description="활성화 상태")
) -> Any:
    """
    users 테이블의 모든 사용자 정보를 조회합니다.
    """
    conn, info = create_connection()
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=info["message"]
        )
    
    try:
        # 기본 쿼리
        query = """
        SELECT 
            user_id, 
            username,
            username1,
            role_id,
            is_active,
            created_at,
            updated_at
        FROM users
        WHERE 1=1
        """
        params = []

        # 활성화 상태 필터
        if is_active is not None:
            query += " AND is_active = %s"
            params.append(is_active)

        # 검색 조건 추가
        if search:
            query += """ AND (
                username LIKE %s 
                OR email LIKE %s 
                OR CONCAT(first_name, ' ', last_name) LIKE %s
                OR phone LIKE %s
            )"""
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term, search_term])

        # 정렬 추가
        query += " ORDER BY id DESC"

        # 페이지네이션 추가
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, skip])

        # 쿼리 실행 전 로깅
        log_query(query, tuple(params) if params else None)
        
        success, result = execute_query(conn, query, tuple(params) if params else None)
        
        # 쿼리 실행 결과 로깅
        log_query("Query Result", None, result)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result
            )

        # 전체 레코드 수 조회
        count_query = "SELECT COUNT(*) as total FROM users"
        if is_active is not None:
            count_query += " WHERE is_active = %s"
            count_success, count_result = execute_query(conn, count_query, (is_active,))
        else:
            count_success, count_result = execute_query(conn, count_query)
        
        # 카운트 쿼리 결과 로깅
        log_query(count_query, (is_active,) if is_active is not None else None, count_result)
        
        total_count = count_result[0]['total'] if count_success else 0
        
        return {
            "status": "success",
            "message": f"{len(result)}명의 사용자 정보를 조회했습니다. (전체: {total_count}명)",
            "data": result
        }
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 정보 조회 중 오류 발생: {str(e)}"
        )
    
    finally:
        close_connection(conn)

@router.get("/users/{user_id}", response_model=MemberResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    특정 사용자의 상세 정보를 조회합니다.
    """
    conn, info = create_connection()
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=info["message"]
        )
    
    try:
        query = """
        SELECT 
            user_id,
            username,
            username1,
            role_id,
            is_active,
            created_at,
            updated_at
        FROM users
        WHERE user_id = %s
        """
        
        success, result = execute_query(conn, query, (user_id,))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result
            )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID가 {user_id}인 사용자를 찾을 수 없습니다."
            )
        
        return {
            "status": "success",
            "message": f"ID가 {user_id}인 사용자 정보를 조회했습니다.",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 정보 조회 중 오류 발생: {str(e)}"
        )
    
    finally:
        close_connection(conn)

@router.post("/users", response_model=MemberResponse)
async def create_user(
    user_in: UserCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    새로운 사용자를 생성합니다.
    """
    conn, info = create_connection()
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=info["message"]
        )
    
    try:
        # 이메일 중복 확인
        check_query = "SELECT id FROM users WHERE email = %s"
        log_query(check_query, (user_in.email,))
        success, existing_user = execute_query(conn, check_query, (user_in.email,))
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 이메일입니다."
            )
        
        # 비밀번호 해시화
        hashed_password = get_password_hash(user_in.password)
        
        # 사용자 생성 쿼리
        insert_query = """
        INSERT INTO users (
            username,
            email,
            hashed_password,
            first_name,
            last_name,
            phone,
            role,
            is_active,
            created_at,
            updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, TRUE, NOW(), NOW()
        )
        """
        
        params = (
            user_in.username,
            user_in.email,
            hashed_password,
            user_in.first_name,
            user_in.last_name,
            user_in.phone,
            user_in.role
        )
        
        # 쿼리 실행 전 로깅
        log_query(insert_query, params)
        
        success, result = execute_query(conn, insert_query, params)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result
            )
        
        # 생성된 사용자 정보 조회
        select_query = """
        SELECT 
            user_id,
            username,
            username1,
            email,
            role_id ,
            is_active,
            created_at,
            updated_at
        FROM users
        WHERE email = %s
        """
        
        log_query(select_query, (user_in.email,))
        success, created_user = execute_query(conn, select_query, (user_in.email,))
        
        if not success or not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="사용자 생성 후 정보 조회 실패"
            )
        
        return {
            "status": "success",
            "message": "새로운 사용자가 생성되었습니다.",
            "data": created_user
        }
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 생성 중 오류 발생: {str(e)}"
        )
    
    finally:
        close_connection(conn)

@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), response: Response = None) -> Dict[str, Any]:
    """
    사용자 로그인 및 토큰 발급 (form-data 방식)
    
    사용 방법:
    - Content-Type: application/x-www-form-urlencoded
    - Form 필드:
      - username: 이메일 주소
      - password: 비밀번호
    """
    # 응답 헤더에 Content-Type 설정
    if response:
        response.headers["Content-Type"] = "application/json"
        
    return await process_login(form_data.username, form_data.password)

@router.post("/login/json", response_model=LoginResponse)
async def login_json(login_data: LoginRequest, response: Response) -> Dict[str, Any]:
    """
    사용자 로그인 및 토큰 발급 (JSON 방식)
    
    사용 방법:
    - Content-Type: application/json
    - Body:
      {
        "username": "사용자 이메일",
        "password": "비밀번호"
      }
      또는
      {
        "email": "사용자 이메일",
        "password": "비밀번호"
      }
    """
    # 응답 헤더에 Content-Type 설정
    response.headers["Content-Type"] = "application/json"
    
    # username 또는 email 중 하나를 사용
    email_to_use = login_data.email if login_data.email else login_data.username
    return await process_login(email_to_use, login_data.password)

async def process_login(email: str, password: str) -> Dict[str, Any]:
    """
    로그인 처리 공통 함수
    """
    # 고정된 사용자 정보로 테스트 (데이터베이스 접근 없음)
    if email == "admin@example.com" and password == "admin123":
        # 토큰 생성
        access_token = create_access_token(
            data={
                "sub": email,
                "user_id": 1,
                "role": "admin",
                "username": "admin",
                "full_name": "관리자"
            }
        )
        
        logger.info(f"관리자 로그인 성공")
        
        return {
            "status": "success",
            "message": "관리자님 환영합니다.",
            "access_token": access_token,
            "token_type": "bearer"
        }
    else:
        logger.error(f"로그인 실패: 잘못된 자격 증명")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 주소나 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer", "Content-Type": "application/json"},
        ) 