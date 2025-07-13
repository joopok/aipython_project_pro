import bcrypt
from functools import wraps
from flask import session, redirect, url_for, flash
from app.constants import SESSION_USER_ID
import logging

logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """비밀번호를 해시화합니다."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """비밀번호를 검증합니다."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def login_required(f):
    """로그인이 필요한 페이지에 대한 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"=== LOGIN CHECK for {f.__name__} ===")
        logger.info(f"Session keys: {list(session.keys())}")
        logger.info(f"SESSION_USER_ID constant: {SESSION_USER_ID}")
        logger.info(f"Checking for: {SESSION_USER_ID} in session")
        
        if SESSION_USER_ID not in session:
            logger.warning(f"User not logged in, redirecting to login page")
            flash('로그인이 필요합니다.', 'warning')
            return redirect(url_for('main.index'))
        
        logger.info(f"User {session.get(SESSION_USER_ID)} logged in, proceeding")
        return f(*args, **kwargs)
    return decorated_function