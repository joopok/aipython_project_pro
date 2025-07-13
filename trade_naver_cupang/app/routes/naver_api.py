"""
네이버 커머스 API 라우트
"""
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from datetime import datetime, timedelta
import logging
from app.services.naver_commerce import NaverCommerceAPI, OrderStatus, ClaimType
from app.models.naver_order import NaverOrder, NaverProductOrder, NaverClaim, NaverOrderSync
from app import db
from app.utils.auth import login_required

logger = logging.getLogger(__name__)

bp = Blueprint('naver', __name__, url_prefix='/naver')
naver_api = NaverCommerceAPI()


@bp.route('/orders')
@login_required
def orders():
    """네이버 주문 목록 페이지"""
    return render_template('naver_orders.html')


@bp.route('/orders/<order_id>')
@login_required
def order_detail(order_id):
    """네이버 주문 상세 페이지"""
    return render_template('naver_order_detail.html', order_id=order_id)


@bp.route('/api/orders', methods=['GET'])
@login_required
def api_get_orders():
    """네이버 주문 목록 조회 API"""
    try:
        # 파라미터 추출
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 20, type=int)
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        search = request.args.get('search')
        
        # 날짜 파싱
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_date = datetime.now() - timedelta(days=7)
            
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end_date = datetime.now()
        
        # 데이터베이스 조회
        query = db.session.query(NaverProductOrder).join(NaverOrder)
        
        # 네이버 API 인증 정보 확인
        if not naver_api.client_id or not naver_api.client_secret:
            logger.warning("네이버 API 인증 정보가 설정되지 않았습니다.")
        
        # 필터 적용
        query = query.filter(NaverOrder.order_date.between(start_date, end_date))
        
        if status:
            query = query.filter(NaverProductOrder.product_order_status == status)
            
        if search:
            query = query.filter(
                db.or_(
                    NaverProductOrder.product_order_id.contains(search),
                    NaverProductOrder.product_name.contains(search),
                    NaverOrder.orderer_name.contains(search)
                )
            )
        
        # 정렬
        query = query.order_by(NaverOrder.order_date.desc())
        
        # 페이징
        paginated = query.paginate(page=page, per_page=size, error_out=False)
        
        # 결과 변환
        orders = []
        for product_order in paginated.items:
            order_dict = product_order.to_dict()
            order_dict['order'] = product_order.order.to_dict()
            orders.append(order_dict)
        
        return jsonify({
            'success': True,
            'data': orders,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        })
        
    except Exception as e:
        logger.error(f"주문 목록 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'message': '주문 목록 조회 실패',
            'error': str(e)
        }), 500


@bp.route('/api/orders/<product_order_id>', methods=['GET'])
@login_required
def api_get_order_detail(product_order_id):
    """네이버 주문 상세 조회 API"""
    try:
        # 데이터베이스에서 조회
        product_order = NaverProductOrder.query.filter_by(
            product_order_id=product_order_id
        ).first()
        
        if not product_order:
            # API에서 조회 시도
            try:
                api_result = naver_api.get_product_order_detail(product_order_id)
                # TODO: API 결과를 데이터베이스에 저장
                
                return jsonify({
                    'success': True,
                    'data': api_result.get('data', {})
                })
            except Exception as api_error:
                logger.error(f"네이버 API 조회 실패: {str(api_error)}")
                return jsonify({
                    'success': False,
                    'message': '주문 정보를 찾을 수 없습니다.'
                }), 404
        
        # 상세 정보 구성
        result = product_order.to_dict()
        result['order'] = product_order.order.to_dict()
        
        # 클레임 정보 추가
        claims = []
        for claim in product_order.claims:
            claims.append(claim.to_dict())
        result['claims'] = claims
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"주문 상세 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'message': '주문 상세 조회 실패',
            'error': str(e)
        }), 500


@bp.route('/api/sync', methods=['POST'])
@login_required
def api_sync_orders():
    """네이버 주문 동기화 API"""
    try:
        # 동기화 시작
        sync_log = NaverOrderSync(
            sync_type='INCREMENTAL',
            start_time=datetime.utcnow()
        )
        db.session.add(sync_log)
        db.session.commit()
        
        # 동기화 실행
        hours = request.json.get('hours', 24)
        result = naver_api.sync_orders(hours=hours)
        
        # 동기화 결과 저장
        sync_log.end_time = datetime.utcnow()
        sync_log.duration_seconds = (sync_log.end_time - sync_log.start_time).seconds
        sync_log.total_count = result.get('total', 0)
        sync_log.success_count = result.get('synced', 0)
        sync_log.failed_count = result.get('failed', 0)
        
        if result.get('errors'):
            sync_log.error_message = str(result['errors'])
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f"동기화 완료: {result['synced']}/{result['total']} 건",
            'data': result
        })
        
    except Exception as e:
        logger.error(f"주문 동기화 실패: {str(e)}")
        
        if sync_log:
            sync_log.error_message = str(e)
            sync_log.failed_count = sync_log.total_count
            db.session.commit()
            
        return jsonify({
            'success': False,
            'message': '주문 동기화 실패',
            'error': str(e)
        }), 500


@bp.route('/api/orders/<product_order_id>/status', methods=['PUT'])
@login_required
def api_update_order_status(product_order_id):
    """주문 상태 변경 API"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        if not status:
            return jsonify({
                'success': False,
                'message': '상태값이 필요합니다.'
            }), 400
        
        # 네이버 API 호출
        dispatch_date = None
        if status == 'DISPATCHED':
            dispatch_date = datetime.now()
            
        result = naver_api.update_product_order_status(
            product_order_id=product_order_id,
            status=status,
            dispatch_date=dispatch_date
        )
        
        # 데이터베이스 업데이트
        product_order = NaverProductOrder.query.filter_by(
            product_order_id=product_order_id
        ).first()
        
        if product_order:
            product_order.product_order_status = status
            if dispatch_date:
                product_order.shipping_start_date = dispatch_date
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '상태 변경 완료',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"상태 변경 실패: {str(e)}")
        return jsonify({
            'success': False,
            'message': '상태 변경 실패',
            'error': str(e)
        }), 500


@bp.route('/api/orders/<product_order_id>/cancel', methods=['POST'])
@login_required
def api_cancel_order(product_order_id):
    """주문 취소 API"""
    try:
        data = request.get_json()
        cancel_reason = data.get('cancel_reason', 'CUSTOMER_CHANGE')
        cancel_detailed_reason = data.get('cancel_detailed_reason')
        
        # 네이버 API 호출
        result = naver_api.process_cancel(
            product_order_id=product_order_id,
            cancel_reason=cancel_reason,
            cancel_detailed_reason=cancel_detailed_reason
        )
        
        # 데이터베이스 업데이트
        product_order = NaverProductOrder.query.filter_by(
            product_order_id=product_order_id
        ).first()
        
        if product_order:
            product_order.claim_type = ClaimType.CANCEL
            product_order.claim_status = 'CANCEL_REQUEST'
            
            # 클레임 정보 생성
            claim = NaverClaim(
                claim_id=result.get('claimId', f'CANCEL_{product_order_id}'),
                product_order_id=product_order_id,
                claim_type=ClaimType.CANCEL,
                claim_status='CANCEL_REQUEST',
                claim_reason=cancel_reason,
                claim_detailed_reason=cancel_detailed_reason,
                claim_request_date=datetime.utcnow(),
                request_quantity=product_order.quantity
            )
            db.session.add(claim)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '취소 요청 완료',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"취소 요청 실패: {str(e)}")
        return jsonify({
            'success': False,
            'message': '취소 요청 실패',
            'error': str(e)
        }), 500


@bp.route('/api/orders/<product_order_id>/tracking', methods=['PUT'])
@login_required
def api_update_tracking(product_order_id):
    """송장 정보 업데이트 API"""
    try:
        data = request.get_json()
        delivery_company = data.get('delivery_company')
        tracking_number = data.get('tracking_number')
        
        if not delivery_company or not tracking_number:
            return jsonify({
                'success': False,
                'message': '택배사와 송장번호가 필요합니다.'
            }), 400
        
        # 네이버 API 호출
        result = naver_api.update_tracking_info(
            product_order_id=product_order_id,
            delivery_company=delivery_company,
            tracking_number=tracking_number
        )
        
        # 데이터베이스 업데이트
        product_order = NaverProductOrder.query.filter_by(
            product_order_id=product_order_id
        ).first()
        
        if product_order:
            product_order.delivery_company = delivery_company
            product_order.tracking_number = tracking_number
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '송장 정보 업데이트 완료',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"송장 정보 업데이트 실패: {str(e)}")
        return jsonify({
            'success': False,
            'message': '송장 정보 업데이트 실패',
            'error': str(e)
        }), 500


@bp.route('/api/sync/history', methods=['GET'])
@login_required
def api_sync_history():
    """동기화 이력 조회 API"""
    try:
        # 최근 동기화 이력 조회
        sync_logs = NaverOrderSync.query.order_by(
            NaverOrderSync.sync_date.desc()
        ).limit(10).all()
        
        history = []
        for log in sync_logs:
            history.append(log.to_dict())
        
        return jsonify({
            'success': True,
            'data': history
        })
        
    except Exception as e:
        logger.error(f"동기화 이력 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'message': '동기화 이력 조회 실패',
            'error': str(e)
        }), 500