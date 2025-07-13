"""
통합 주문 조회 API 라우트
"""
from flask import Blueprint, request, jsonify, render_template
from datetime import datetime, timedelta
import logging
from app.services.integrated_orders import IntegratedOrderService
from app.utils.auth import login_required

logger = logging.getLogger(__name__)

bp = Blueprint('integrated', __name__, url_prefix='/integrated')


@bp.route('/orders')
@login_required
def orders():
    """통합 주문조회 페이지"""
    return render_template('integrated_orders.html')


@bp.route('/api/orders', methods=['GET'])
@login_required
def api_get_orders():
    """통합 주문 목록 조회 API"""
    try:
        # 파라미터 추출
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        platform = request.args.get('platform')  # NAVER, COUPANG, 또는 None(전체)
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        search = request.args.get('search')
        
        # 날짜 파싱
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_date = datetime.now() - timedelta(days=30)
            
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)
        else:
            end_date = datetime.now()
        
        # 통합 주문 조회
        result = IntegratedOrderService.get_integrated_orders(
            start_date=start_date,
            end_date=end_date,
            platform=platform,
            status=status,
            search=search,
            page=page,
            per_page=per_page
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"통합 주문 목록 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'message': '주문 목록 조회 실패',
            'error': str(e)
        }), 500


@bp.route('/api/orders/export', methods=['GET'])
@login_required
def api_export_orders():
    """통합 주문 엑셀 다운로드 API"""
    try:
        # 파라미터 추출
        platform = request.args.get('platform')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        search = request.args.get('search')
        
        # 날짜 파싱
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_date = datetime.now() - timedelta(days=30)
            
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)
        else:
            end_date = datetime.now()
        
        # 전체 데이터 조회 (페이지네이션 없이)
        result = IntegratedOrderService.get_integrated_orders(
            start_date=start_date,
            end_date=end_date,
            platform=platform,
            status=status,
            search=search,
            page=1,
            per_page=10000  # 최대 10000건
        )
        
        if not result['success']:
            raise Exception("주문 조회 실패")
        
        # Excel 파일 생성
        import io
        import pandas as pd
        from flask import send_file
        
        # DataFrame 생성
        orders_data = []
        for order in result['orders']:
            orders_data.append({
                '플랫폼': order['platform'],
                '주문번호': order['orderId'],
                '플랫폼주문번호': order['platformOrderId'],
                '주문일시': order['orderDate'],
                '주문자': order['ordererName'],
                '수취인': order['receiverName'],
                '상품명': order['productName'],
                '수량': order['quantity'],
                '주문금액': order['orderAmount'],
                '상태': order['status'],
                '택배사': order['deliveryCompany'] or '',
                '송장번호': order['trackingNumber'] or '',
                '배송지': order['shippingAddress'],
                '우편번호': order['postalCode']
            })
        
        df = pd.DataFrame(orders_data)
        
        # Excel 파일로 변환
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='통합주문목록', index=False)
            
            # 열 너비 자동 조정
            worksheet = writer.sheets['통합주문목록']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        # 파일명 생성
        filename = f'통합주문목록_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"주문 엑셀 다운로드 실패: {str(e)}")
        return jsonify({
            'success': False,
            'message': '엑셀 다운로드 실패',
            'error': str(e)
        }), 500


@bp.route('/api/orders/statistics', methods=['GET'])
@login_required
def api_get_statistics():
    """통합 주문 통계 조회 API"""
    try:
        # 날짜 파라미터
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 날짜 파싱
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_date = datetime.now() - timedelta(days=30)
            
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)
        else:
            end_date = datetime.now()
        
        # 통계 조회
        service = IntegratedOrderService()
        statistics = service._calculate_statistics(start_date, end_date)
        
        return jsonify({
            'success': True,
            'statistics': statistics
        })
        
    except Exception as e:
        logger.error(f"통계 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'message': '통계 조회 실패',
            'error': str(e)
        }), 500