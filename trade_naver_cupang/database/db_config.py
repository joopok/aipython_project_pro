import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent.parent))

# config.py에서 설정 가져오기
from config import Config

# MariaDB 연결 문자열
DATABASE_URL = f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}?charset=utf8mb4"

# SQLAlchemy 엔진 생성
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=Config.SQLALCHEMY_ECHO  # SQL 쿼리 로깅
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
Base = declarative_base()

def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """데이터베이스 초기화"""
    try:
        # 데이터베이스 생성 (없는 경우)
        from sqlalchemy import text
        from sqlalchemy import create_engine as create_temp_engine
        
        temp_engine = create_temp_engine(
            f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/?charset=utf8mb4"
        )
        
        with temp_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            conn.commit()
        
        print(f"Database '{Config.DB_NAME}' created or already exists.")
        
        # 테이블 생성
        Base.metadata.create_all(bind=engine)
        print("All tables created successfully.")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    # 데이터베이스 초기화 실행
    init_db()