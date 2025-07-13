import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY 환경변수가 설정되지 않았습니다. .env 파일을 확인하세요.")
    
    # MariaDB 설정
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    if not DB_PASSWORD:
        raise ValueError("DB_PASSWORD 환경변수가 설정되지 않았습니다. .env 파일을 확인하세요.")
    DB_NAME = os.environ.get('DB_NAME', 'trade_naver_cupang')
    
    # SQLAlchemy MariaDB 연결 문자열
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SQL 쿼리 로깅 설정
    SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', 'True').lower() == 'true'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 3600
    }
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # API Keys for Naver/Coupang
    NAVER_CLIENT_ID = os.environ.get('NAVER_CLIENT_ID')
    NAVER_CLIENT_SECRET = os.environ.get('NAVER_CLIENT_SECRET')
    COUPANG_ACCESS_KEY = os.environ.get('COUPANG_ACCESS_KEY')
    COUPANG_SECRET_KEY = os.environ.get('COUPANG_SECRET_KEY')
    
    # Selenium settings
    SELENIUM_DRIVER_PATH = os.environ.get('SELENIUM_DRIVER_PATH')
    HEADLESS_BROWSER = os.environ.get('HEADLESS_BROWSER', 'True').lower() == 'true'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    # Production 환경에서는 SQL 쿼리 로깅 비활성화
    SQLALCHEMY_ECHO = False
    # 세션 쿠키 보안 설정
    SESSION_COOKIE_SECURE = False  # HTTPS 사용시 True로 변경
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}