from flask import Blueprint, request, jsonify, session
from app.models import MarketplaceProduct, SearchHistory, User
from app.utils.response import handle_error, json_response
from app.utils.auth import hash_password
from app.constants import *
from app import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('api', __name__)


@bp.route('/search', methods=['POST'])
def search():
    """
    상품 검색 API
    현재 스크래퍼가 비활성화되어 있어 빈 결과를 반환합니다.
    """
    data = request.get_json()
    keyword = data.get('keyword')
    platform = data.get('platform', PLATFORM_ALL)
    
    if not keyword:
        return json_response({'error': 'Keyword is required'}, HTTP_BAD_REQUEST)
    
    results = []
    
    try:
        # TODO: 스크래퍼 기능이 활성화되면 주석 해제
        # if platform in [PLATFORM_NAVER, PLATFORM_ALL]:
        #     naver_scraper = NaverScraper()
        #     naver_results = naver_scraper.search(keyword)
        #     results.extend(naver_results)
        
        # Save search history
        history = SearchHistory(
            keyword=keyword,
            platform=platform,
            result_count=len(results)
        )
        db.session.add(history)
        db.session.commit()
        
        return json_response({
            'keyword': keyword,
            'platform': platform,
            'count': len(results),
            'results': results,
            'message': '현재 검색 기능이 비활성화되어 있습니다.'
        })
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        db.session.rollback()
        return json_response({'error': '검색 중 오류가 발생했습니다.'}, HTTP_INTERNAL_ERROR)


@bp.route('/products', methods=['GET'])
def get_products():
    """상품 목록 조회 API"""
    page = request.args.get('page', DEFAULT_PAGE, type=int)
    per_page = request.args.get('per_page', DEFAULT_PER_PAGE, type=int)
    platform = request.args.get('platform')
    
    try:
        query = MarketplaceProduct.query
        if platform:
            query = query.filter_by(platform=platform)
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return json_response({
            'products': [p.to_dict() for p in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages
        })
    except Exception as e:
        logger.error(f"Get products error: {str(e)}", exc_info=True)
        return json_response({'error': '상품 목록을 불러오는 중 오류가 발생했습니다.'}, HTTP_INTERNAL_ERROR)


@bp.route('/history', methods=['GET'])
def get_search_history():
    """검색 기록 조회 API"""
    try:
        history = SearchHistory.query.order_by(
            SearchHistory.created_at.desc()
        ).limit(MAX_SEARCH_HISTORY).all()
        
        return json_response([h.to_dict() for h in history])
    except Exception as e:
        logger.error(f"Get search history error: {str(e)}", exc_info=True)
        return json_response({'error': '검색 기록을 불러오는 중 오류가 발생했습니다.'}, HTTP_INTERNAL_ERROR)


@bp.route('/users', methods=['GET'])
def get_users():
    """사용자 목록 조회 API"""
    # 관리자만 접근 가능 (임시 비활성화)
    # if session.get(SESSION_USER_ROLE) != ROLE_ADMIN:
    #     return json_response({'message': '권한이 없습니다.'}, 403)
    
    try:
        users = User.query.all()
        return jsonify([{
            'id': u.id,
            'username': u.username,
            'full_name': u.full_name,
            'email': u.email,
            'role': u.role,
            'is_active': u.is_active,
            'created_at': u.created_at.isoformat() if u.created_at else None,
            'last_login': u.last_login.isoformat() if u.last_login else None
        } for u in users])
    except Exception as e:
        logger.error(f"Get users error: {str(e)}", exc_info=True)
        return json_response({'error': '사용자 목록을 불러오는 중 오류가 발생했습니다.'}, HTTP_INTERNAL_ERROR)


@bp.route('/users', methods=['POST'])
def create_user():
    """새 사용자 생성 API"""
    # 관리자만 접근 가능 (임시 비활성화)
    # if session.get(SESSION_USER_ROLE) != ROLE_ADMIN:
    #     return json_response({'message': '권한이 없습니다.'}, 403)
    
    data = request.json
    
    # 필수 필드 검증
    required_fields = ['username', 'password', 'email']
    for field in required_fields:
        if not data.get(field):
            return json_response({'message': f'{field}는 필수 입력 항목입니다.'}, 400)
    
    try:
        # 중복 체크
        if User.query.filter_by(username=data['username']).first():
            return json_response({'message': '이미 존재하는 아이디입니다.'}, 400)
        
        if User.query.filter_by(email=data['email']).first():
            return json_response({'message': '이미 존재하는 이메일입니다.'}, 400)
        
        # 새 사용자 생성
        user = User(
            username=data['username'],
            password=hash_password(data['password']),
            full_name=data.get('full_name'),
            email=data['email'],
            role=data.get('role', 'user'),
            is_active=data.get('is_active', True),
            created_at=datetime.now()
        )
        
        db.session.add(user)
        db.session.commit()
        
        return json_response({
            'message': '사용자가 성공적으로 생성되었습니다.',
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        }, 201)
        
    except Exception as e:
        logger.error(f"Create user error: {str(e)}", exc_info=True)
        db.session.rollback()
        return json_response({'error': '사용자 생성 중 오류가 발생했습니다.'}, HTTP_INTERNAL_ERROR)