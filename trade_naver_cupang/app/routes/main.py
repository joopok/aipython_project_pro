from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from app.models import User
from app import db
from app.utils.auth import verify_password, hash_password, login_required
from app.utils.response import handle_error, handle_success
from app.constants import *
from datetime import datetime
import logging

bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

# login_required는 app.utils.auth에서 import됨


@bp.route('/')
def index():
    # 이미 로그인한 경우 대시보드로 리다이렉트
    if SESSION_USER_ID in session:
        return redirect(url_for('main.dashboard'))
    return render_template('login.html')

def _validate_login_input(username, password):
    """로그인 입력값 검증"""
    if not username or not password:
        return False, '아이디와 비밀번호를 입력해주세요.'
    return True, None

def _authenticate_user(username, password):
    """사용자 인증"""
    try:
        user = User.query.filter_by(username=username, is_active=True).first()
        
        if not user:
            logger.warning(f"Login failed: User not found - {username}")
            return None, '존재하지 않는 아이디입니다.'
        
        if not verify_password(password, user.password):
            logger.warning(f"Login failed: Invalid password - {username}")
            return None, '비밀번호가 일치하지 않습니다.'
        
        # 마지막 로그인 시간 업데이트
        user.last_login = datetime.now()
        db.session.commit()
        
        return user, None
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return None, '인증 처리 중 오류가 발생했습니다.'

def _set_user_session(user):
    """사용자 세션 설정"""
    session[SESSION_USER_ID] = user.id
    session[SESSION_USERNAME] = user.username
    session[SESSION_USER_ROLE] = user.role  # 'role' 키로 저장
    session[SESSION_USER_FULLNAME] = user.full_name
    logger.info(f"Login successful: {user.username} with role: {user.role}")

@bp.route('/login', methods=['POST'])
def login():
    is_ajax = True  # fetch API 사용 시 항상 JSON 응답
    
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    # 입력값 검증
    valid, error_msg = _validate_login_input(username, password)
    if not valid:
        return handle_error(error_msg, is_ajax=is_ajax, status_code=HTTP_BAD_REQUEST)
    
    try:
        # 사용자 인증
        user, error_msg = _authenticate_user(username, password)
        if not user:
            return handle_error(error_msg, is_ajax=is_ajax, status_code=HTTP_UNAUTHORIZED)
        
        # 세션 설정
        _set_user_session(user)
        
        # 성공 응답
        welcome_msg = f'환영합니다, {user.full_name or user.username}님!'
        return handle_success(welcome_msg, redirect_endpoint='main.dashboard', is_ajax=is_ajax)
        
    except Exception as e:
        error_msg = '로그인 처리 중 오류가 발생했습니다.'
        return handle_error(error_msg, is_ajax=is_ajax, status_code=HTTP_INTERNAL_ERROR, log_error=e)

@bp.route('/logout')
def logout():
    username = session.get(SESSION_USERNAME, 'Unknown')
    session.clear()
    logger.info(f"Logout: {username}")
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('main.index', logout=1))

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@bp.route('/orders')
@login_required
def orders():
    return render_template('orders.html')

@bp.route('/tracking')
@login_required
def tracking():
    return render_template('tracking.html')


@bp.route('/users')
@login_required
def users():
    """사용자 관리 페이지"""
    # 디버깅을 위해 현재 세션 정보 로그
    logger.info(f"=== USERS PAGE ACCESS ===")
    logger.info(f"Username: {session.get(SESSION_USERNAME)}")
    logger.info(f"Role from session: {session.get(SESSION_USER_ROLE)}")
    logger.info(f"SESSION_USER_ROLE constant: {SESSION_USER_ROLE}")
    logger.info(f"ROLE_ADMIN constant: {ROLE_ADMIN}")
    logger.info(f"Full session data: {dict(session)}")
    
    # 관리자만 접근 가능 (임시로 주석 처리)
    # if session.get(SESSION_USER_ROLE) != ROLE_ADMIN:
    #     logger.warning(f"Access denied: {session.get(SESSION_USER_ROLE)} != {ROLE_ADMIN}")
    #     flash('관리자 권한이 필요합니다.', 'error')
    #     return redirect(url_for('main.dashboard'))
    
    # 모든 사용자 목록 조회
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        logger.info(f"Successfully loaded {len(users)} users")
        return render_template('users.html', users=users)
    except Exception as e:
        logger.error(f"Get users error: {str(e)}", exc_info=True)
        # 오류가 발생해도 빈 목록으로 페이지 표시
        return render_template('users.html', users=[])

@bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    """사용자 생성 페이지"""
    # 관리자만 접근 가능
    if session.get(SESSION_USER_ROLE) != ROLE_ADMIN:
        flash('관리자 권한이 필요합니다.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'GET':
        return render_template('create_user.html')
    
    # POST 요청 처리
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    email = request.form.get('email', '').strip()
    full_name = request.form.get('full_name', '').strip()
    role = request.form.get('role', ROLE_USER)
    
    # 입력값 검증
    if not all([username, password, email, full_name]):
        flash('모든 필수 항목을 입력해주세요.', 'error')
        return render_template('create_user.html')
    
    # 비밀번호 길이 검증
    if len(password) < 6:
        flash('비밀번호는 최소 6자 이상이어야 합니다.', 'error')
        return render_template('create_user.html')
    
    try:
        # 중복 사용자 확인
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                flash('이미 존재하는 아이디입니다.', 'error')
            else:
                flash('이미 존재하는 이메일입니다.', 'error')
            return render_template('create_user.html')
        
        # 새 사용자 생성
        new_user = User(
            username=username,
            password=hash_password(password),
            email=email,
            full_name=full_name,
            role=role,
            is_active=True,
            created_at=datetime.now()
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f"New user created: {username} by {session.get(SESSION_USERNAME)}")
        flash(f'사용자 {username}이(가) 성공적으로 생성되었습니다.', 'success')
        return redirect(url_for('main.users'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Create user error: {str(e)}", exc_info=True)
        flash('사용자 생성 중 오류가 발생했습니다.', 'error')
        return render_template('create_user.html')

@bp.route('/health')
def health():
    return {'status': 'healthy'}, 200

@bp.route('/users-test')
def users_test():
    """권한 체크 없는 사용자 페이지 테스트"""
    logger.info("=== USERS TEST PAGE ===")
    users = User.query.all()
    return render_template('users.html', users=users)

@bp.route('/test-session')
@login_required
def test_session():
    """세션 정보 확인 페이지"""
    return render_template('test_session.html')

@bp.route('/debug-users')
@login_required
def debug_users():
    """사용자 관리 디버그 페이지"""
    return render_template('debug_users.html')