"""
쿠팡 커머스 API 라우트
"""
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from datetime import datetime, timedelta
import logging
from app.services.coupang_commerce import CoupangCommerceAPI, DeliveryCompanyCode
from app.models.coupang_order import CoupangOrderSheet, CoupangOrderItem, CoupangOrderSync, OrderStatus
from app import db
from app.utils.auth import login_required

logger = logging.getLogger(__name__)

bp = Blueprint('coupang', __name__, url_prefix='/coupang')
coupang_api = CoupangCommerceAPI()


@bp.route('/orders')
@login_required
def orders():
    """쿠팡 주문 목록 페이지"""
    return render_template('coupang_orders.html')


@bp.route('/orders/<shipment_box_id>')
@login_required
def order_detail(shipment_box_id):
    """쿠팡 주문 상세 페이지"""
    return render_template('coupang_order_detail.html', shipment_box_id=shipment_box_id)


@bp.route('/api/coupang/orders', methods=['GET'])
@login_required
def api_get_orders():
    """쿠팡 주문 목록 조회 API"""
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
            end_date = end_date.replace(hour=23, minute=59, second=59)
        else:
            end_date = datetime.now()
        
        # 데이터베이스 조회
        query = db.session.query(CoupangOrderSheet)
        
        # 필터 적용
        query = query.filter(CoupangOrderSheet.ordered_at.between(start_date, end_date))
        
        if status:
            query = query.filter(CoupangOrderSheet.status == status)
            
        if search:
            query = query.filter(
                db.or_(
                    CoupangOrderSheet.shipment_box_id.contains(search),
                    CoupangOrderSheet.order_id.contains(search),
                    CoupangOrderSheet.orderer_name.contains(search),
                    CoupangOrderSheet.receiver_name.contains(search)
                )
            )
        
        # 정렬
        query = query.order_by(CoupangOrderSheet.ordered_at.desc())
        
        # 페이징
        paginated = query.paginate(page=page, per_page=size, error_out=False)
        
        # 결과 변환
        orders = []
        for order_sheet in paginated.items:
            order_dict = order_sheet.to_dict()
            orders.append(order_dict)
        
        # 통계 정보 계산
        statistics = {
            'total': db.session.query(CoupangOrderSheet).count(),
            'new_orders': db.session.query(CoupangOrderSheet).filter_by(status='ACCEPT').count(),
            'delivering': db.session.query(CoupangOrderSheet).filter_by(status='DELIVERING').count(),
            'preparing': db.session.query(CoupangOrderSheet).filter_by(status='INSTRUCT').count()
        }
        
        return jsonify({
            'success': True,
            'orders': orders,
            'pagination': {
                'total_items': paginated.total,
                'total_pages': paginated.pages,
                'current_page': page,
                'per_page': size
            },
            'statistics': statistics
        })
        
    except Exception as e:
        logger.error(f"주문 목록 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'code': 500,
            'message': '주문 목록 조회 실패',
            'error': str(e)
        }), 500


@bp.route('/api/coupang/orders/<shipment_box_id>', methods=['GET'])
@login_required
def api_get_order_detail(shipment_box_id):
    """쿠팡 주문 상세 조회 API"""
    try:
        # 데이터베이스에서 조회
        order_sheet = CoupangOrderSheet.query.filter_by(
            shipment_box_id=shipment_box_id
        ).first()
        
        if not order_sheet:
            # API에서 조회 시도
            try:
                api_result = coupang_api.get_order_sheet_detail(shipment_box_id)
                # TODO: API 결과를 데이터베이스에 저장
                
                return jsonify({
                    'success': True,
                    'code': 200,
                    'message': 'OK',
                    'data': api_result.get('data', {})
                })
            except Exception as api_error:
                logger.error(f"쿠팡 API 조회 실패: {str(api_error)}")
                return jsonify({
                    'success': False,
                    'code': 404,
                    'message': '주문 정보를 찾을 수 없습니다.'
                }), 404
        
        # 상세 정보 구성
        result = order_sheet.to_dict()
        
        return jsonify({
            'success': True,
            'code': 200,
            'message': 'OK',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"주문 상세 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'code': 500,
            'message': '주문 상세 조회 실패',
            'error': str(e)
        }), 500


@bp.route('/api/coupang/sync', methods=['POST'])
@login_required
def api_sync_orders():
    """쿠팡 주문 동기화 API"""
    try:
        # 동기화 시작
        sync_log = CoupangOrderSync(
            sync_type='INCREMENTAL',
            start_time=datetime.utcnow()
        )
        db.session.add(sync_log)
        db.session.commit()
        
        # 동기화 실행
        hours = request.json.get('hours', 24)
        result = coupang_api.sync_orders(hours=hours)
        
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
            'message': result.get('message', f"동기화 완료: {result.get('synced', 0)}/{result.get('total', 0)} 건"),
            'total_count': result.get('total', 0),
            'success_count': result.get('synced', 0)
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


@bp.route('/api/coupang/orders/<shipment_box_id>/acknowledge', methods=['POST'])
@login_required
def api_acknowledge_order(shipment_box_id):
    """발주 확인 처리 API"""
    try:
        # 쿠팡 API 호출
        result = coupang_api.acknowledge_order([shipment_box_id])
        
        # 데이터베이스 업데이트
        order_sheet = CoupangOrderSheet.query.filter_by(
            shipment_box_id=shipment_box_id
        ).first()
        
        if order_sheet:
            order_sheet.status = OrderStatus.INSTRUCT
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '발주 확인 완료',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"발주 확인 실패: {str(e)}")
        return jsonify({
            'success': False,
            'message': '발주 확인 실패',
            'error': str(e)
        }), 500


@bp.route('/api/coupang/orders/<shipment_box_id>/shipment', methods=['POST'])
@login_required
def api_update_shipment(shipment_box_id):
    """송장 등록 API"""
    try:
        data = request.get_json()
        delivery_company_code = data.get('delivery_company_code')
        invoice_number = data.get('invoice_number')
        
        if not delivery_company_code or not invoice_number:
            return jsonify({
                'success': False,
                'message': '택배사와 송장번호가 필요합니다.'
            }), 400
        
        # 쿠팡 API 호출
        result = coupang_api.update_shipment(
            shipment_box_id=shipment_box_id,
            delivery_company_code=delivery_company_code,
            invoice_number=invoice_number
        )
        
        # 데이터베이스 업데이트
        order_sheet = CoupangOrderSheet.query.filter_by(
            shipment_box_id=shipment_box_id
        ).first()
        
        if order_sheet:
            # 택배사 코드를 이름으로 변환
            company_name_map = {
                DeliveryCompanyCode.CJ: 'CJ대한통운',
                DeliveryCompanyCode.HANJIN: '한진택배',
                DeliveryCompanyCode.LOTTE: '롯데택배',
                DeliveryCompanyCode.POST: '우체국택배',
                DeliveryCompanyCode.LOGEN: '로젠택배',
                DeliveryCompanyCode.HYUNDAI: '롯데글로벌로지스'
            }
            
            order_sheet.delivery_company_name = company_name_map.get(delivery_company_code, delivery_company_code)
            order_sheet.invoice_number = invoice_number
            order_sheet.status = OrderStatus.DEPARTURE
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '송장 정보 등록 완료',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"송장 정보 등록 실패: {str(e)}")
        return jsonify({
            'success': False,
            'message': '송장 정보 등록 실패',
            'error': str(e)
        }), 500


@bp.route('/api/coupang/sync/history', methods=['GET'])
@login_required
def api_sync_history():
    """동기화 이력 조회 API"""
    try:
        # 최근 동기화 이력 조회
        sync_logs = CoupangOrderSync.query.order_by(
            CoupangOrderSync.sync_date.desc()
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