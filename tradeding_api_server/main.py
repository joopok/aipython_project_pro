import time
import logging
from typing import Callable
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from contextlib import asynccontextmanager

from app.routers import auth, users, sample, members, kiwoom
from app.services.kiwoom_client import kiwoom_client

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 애플리케이션 수명주기 관리
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시
    logger.info("서버 시작 - 키움 API 클라이언트 초기화")
    yield
    # 종료 시
    await kiwoom_client.close()
    logger.info("서버 종료 - 키움 API 클라이언트 정리 완료")

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="트레이딩 REST API 서버",
    description="키움증권 REST API 기반 트레이딩 서비스",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS 미들웨어 설정
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "*"  # 개발 환경에서만 사용하고, 프로덕션에서는 제거해야 함
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 로깅 미들웨어 추가
@app.middleware("http")
async def logging_middleware(request: Request, call_next: Callable) -> Response:
    # 요청 정보 로깅
    start_time = time.time()
    
    # 요청 경로와 메서드 추출
    path = request.url.path
    method = request.method
    
    # 요청 헤더와 쿼리 파라미터
    headers = dict(request.headers)
    query_params = dict(request.query_params)
    
    # 인증 토큰이 있다면 일부만 표시
    if 'authorization' in headers:
        auth = headers['authorization']
        if auth.startswith('Bearer '):
            headers['authorization'] = f"Bearer {auth[7:20]}..." if len(auth) > 27 else auth
    
    # 요청 바디 추출 시도 (바디를 추출하면 스트림이 소비되므로 실제로는 복사본 생성)
    body = None
    if method in ["POST", "PUT", "PATCH"]:
        try:
            # request.body()는 내부적으로 캐싱되므로 재호출 가능
            body_bytes = await request.body()
            
            # 바이너리 바디를 문자열로 변환 시도
            try:
                body = body_bytes.decode()
                # 비밀번호가 포함된 경우 마스킹 처리
                if "password" in body:
                    # 간단한 방식으로 비밀번호 마스킹 (더 복잡한 상황은 추가 처리 필요)
                    parts = body.split("&")
                    masked_parts = []
                    for part in parts:
                        if part.startswith("password="):
                            masked_parts.append("password=*****")
                        else:
                            masked_parts.append(part)
                    body = "&".join(masked_parts)
            except UnicodeDecodeError:
                body = f"Binary data ({len(body_bytes)} bytes)"
        except Exception as e:
            logger.error(f"요청 바디 추출 실패: {e}")
            body = "Failed to extract body"
    
    logger.info(f"\n{'='*80}")
    logger.info(f"요청 시작: {method} {path}")
    logger.info(f"헤더: {headers}")
    logger.info(f"쿼리 파라미터: {query_params}")
    if body:
        logger.info(f"바디: {body}")
    
    # 요청 처리
    try:
        response = await call_next(request)
        status_code = response.status_code
        
        # 응답 바디 추출 (응답도 스트림이므로 복사해야 함)
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        
        # 새로운 응답 생성
        new_response = Response(
            content=response_body,
            status_code=status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )
        
        # 응답 내용 로깅 (너무 길면 일부만 표시)
        try:
            resp_text = response_body.decode()
            if len(resp_text) > 1000:
                resp_text = resp_text[:1000] + "... (truncated)"
        except:
            resp_text = f"Binary response ({len(response_body)} bytes)"
        
        # 응답 시간 계산
        duration = time.time() - start_time
        
        logger.info(f"응답 완료: {method} {path} - {status_code}")
        logger.info(f"응답 시간: {duration:.4f}초")
        logger.info(f"응답 내용: {resp_text}")
        logger.info(f"{'='*80}\n")
        
        return new_response
    except Exception as e:
        # 처리 중 오류 발생
        logger.error(f"요청 처리 중 오류: {str(e)}")
        logger.info(f"{'='*80}\n")
        
        # 오류 응답 반환
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(e)}"}
        )

# 모든 응답에 application/json Content-Type 헤더 추가
@app.middleware("http")
async def add_json_content_type(request: Request, call_next: Callable) -> Response:
    # 요청 헤더 로깅
    logger.info(f"Request headers: {request.headers}")
    
    # 요청 처리
    response = await call_next(request)
    
    # JSON 응답일 경우에만 Content-Type 헤더 설정
    if response.headers.get("content-type") is None or "json" in response.headers.get("content-type", ""):
        response.headers["Content-Type"] = "application/json"
    
    # 응답 헤더 로깅
    logger.info(f"Response headers: {response.headers}")
    
    return response

# 라우터 등록
app.include_router(auth.router, tags=["인증"])
app.include_router(users.router, prefix="/api", tags=["사용자"])
app.include_router(sample.router, prefix="/api", tags=["샘플"])
app.include_router(members.router, prefix="/api", tags=["회원"])
app.include_router(kiwoom.router, prefix="/api/kiwoom", tags=["키움증권"])

# Static 파일 서빙
_static_dir = Path(__file__).parent / "app" / "static"
app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")

@app.get("/")
async def root():
    """
    API 서버 루트 경로
    """
    return {
        "message": "RestAPI 서버에 오신 것을 환영합니다",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "condition_search": "/condition-search",
    }

@app.get("/condition-search", response_class=HTMLResponse)
async def condition_search_page():
    """조건검색 서비스 페이지"""
    html_path = _static_dir / "condition_search.html"
    return FileResponse(str(html_path), media_type="text/html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6100)