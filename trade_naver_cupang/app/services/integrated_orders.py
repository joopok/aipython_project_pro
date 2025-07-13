"""
통합 주문 조회 서비스
네이버와 쿠팡 주문을 통합하여 조회하는 기능
"""
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import text
from app import db
import logging

logger = logging.getLogger(__name__)


class IntegratedOrderService:
    """통합 주문 조회 서비스"""
    
    @staticmethod
    def get_integrated_orders(
        start_date: datetime,
        end_date: datetime,
        platform: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        네이버와 쿠팡 주문을 통합하여 조회
        
        Args:
            start_date: 조회 시작일
            end_date: 조회 종료일
            platform: 플랫폼 필터 ('NAVER', 'COUPANG', None)
            status: 주문 상태 필터
            search: 검색어 (주문번호, 고객명)
            page: 페이지 번호
            per_page: 페이지당 항목 수
            
        Returns:
            통합 주문 목록과 페이지네이션 정보
        """
        try:
            # UNION 쿼리로 네이버와 쿠팡 주문 통합
            # 상태 매핑을 위한 CASE 문 사용
            query = """
                SELECT * FROM (
                    -- 네이버 주문
                    SELECT 
                        'NAVER' as platform,
                        CAST(npo.product_order_id AS CHAR) as order_id,
                        no.order_id as platform_order_id,
                        no.orderer_name as orderer_name,
                        JSON_UNQUOTE(JSON_EXTRACT(npo.shipping_address, '$.name')) as receiver_name,
                        npo.product_name as product_name,
                        npo.quantity as quantity,
                        npo.total_product_amount as order_amount,
                        CASE npo.product_order_status
                            WHEN 'PAYMENT_WAITING' THEN 'PAYMENT_WAITING'
                            WHEN 'PAYED' THEN 'ACCEPT'
                            WHEN 'DELIVERING' THEN 'DELIVERING'
                            WHEN 'DELIVERED' THEN 'FINAL_DELIVERY'
                            WHEN 'PURCHASE_DECIDED' THEN 'FINAL_DELIVERY'
                            ELSE npo.product_order_status
                        END as status,
                        npo.delivery_company as delivery_company,
                        npo.tracking_number as tracking_number,
                        no.order_date as order_date,
                        npo.shipping_due_date as shipping_due_date,
                        npo.delivered_date as delivered_date,
                        CONCAT(
                            JSON_UNQUOTE(JSON_EXTRACT(npo.shipping_address, '$.baseAddress')), ' ',
                            JSON_UNQUOTE(JSON_EXTRACT(npo.shipping_address, '$.detailAddress'))
                        ) as shipping_address,
                        JSON_UNQUOTE(JSON_EXTRACT(npo.shipping_address, '$.zipCode')) as postal_code,
                        npo.product_order_id as sort_key
                    FROM naver_product_orders npo
                    JOIN naver_orders no ON npo.order_id = no.order_id
                    WHERE no.order_date BETWEEN :start_date AND :end_date
                    
                    UNION ALL
                    
                    -- 쿠팡 주문
                    SELECT 
                        'COUPANG' as platform,
                        CAST(cos.shipment_box_id AS CHAR) as order_id,
                        CAST(cos.order_id AS CHAR) as platform_order_id,
                        cos.orderer_name as orderer_name,
                        cos.receiver_name as receiver_name,
                        (SELECT GROUP_CONCAT(coi.vendor_item_name SEPARATOR ', ')
                         FROM coupang_order_items coi 
                         WHERE coi.shipment_box_id = cos.shipment_box_id
                         LIMIT 1) as product_name,
                        (SELECT SUM(coi.shipping_count) 
                         FROM coupang_order_items coi 
                         WHERE coi.shipment_box_id = cos.shipment_box_id) as quantity,
                        (SELECT SUM(coi.order_price) 
                         FROM coupang_order_items coi 
                         WHERE coi.shipment_box_id = cos.shipment_box_id) as order_amount,
                        cos.status as status,
                        cos.delivery_company_name as delivery_company,
                        cos.invoice_number as tracking_number,
                        cos.ordered_at as order_date,
                        NULL as shipping_due_date,
                        cos.delivered_date as delivered_date,
                        CONCAT(cos.receiver_addr1, ' ', cos.receiver_addr2) as shipping_address,
                        cos.receiver_post_code as postal_code,
                        CAST(cos.shipment_box_id AS CHAR) as sort_key
                    FROM coupang_order_sheets cos
                    WHERE cos.ordered_at BETWEEN :start_date AND :end_date
                ) AS integrated_orders
                WHERE 1=1
            """
            
            # 동적 필터 추가
            params = {
                'start_date': start_date,
                'end_date': end_date
            }
            
            # 플랫폼 필터
            if platform:
                query += " AND platform = :platform"
                params['platform'] = platform
            
            # 상태 필터
            if status:
                query += " AND status = :status"
                params['status'] = status
            
            # 검색 필터
            if search:
                query += """ AND (
                    order_id LIKE :search OR 
                    platform_order_id LIKE :search OR
                    orderer_name LIKE :search OR 
                    receiver_name LIKE :search OR
                    product_name LIKE :search OR
                    tracking_number LIKE :search
                )"""
                params['search'] = f'%{search}%'
            
            # 정렬
            query += " ORDER BY order_date DESC"
            
            # 전체 카운트 조회
            count_query = f"SELECT COUNT(*) as total FROM ({query}) AS count_table"
            total_count = db.session.execute(text(count_query), params).scalar()
            
            # 페이지네이션
            offset = (page - 1) * per_page
            query += f" LIMIT {per_page} OFFSET {offset}"
            
            # 실행
            result = db.session.execute(text(query), params)
            orders = []
            
            for row in result:
                order = {
                    'platform': row.platform,
                    'orderId': row.order_id,
                    'platformOrderId': row.platform_order_id,
                    'ordererName': row.orderer_name,
                    'receiverName': row.receiver_name,
                    'productName': row.product_name,
                    'quantity': row.quantity,
                    'orderAmount': row.order_amount or 0,
                    'status': row.status,
                    'deliveryCompany': row.delivery_company,
                    'trackingNumber': row.tracking_number,
                    'orderDate': row.order_date.isoformat() if row.order_date else None,
                    'shippingDueDate': row.shipping_due_date.isoformat() if row.shipping_due_date else None,
                    'deliveredDate': row.delivered_date.isoformat() if row.delivered_date else None,
                    'shippingAddress': row.shipping_address,
                    'postalCode': row.postal_code
                }
                orders.append(order)
            
            # 통계 정보 계산
            statistics = IntegratedOrderService._calculate_statistics(start_date, end_date)
            
            return {
                'success': True,
                'orders': orders,
                'pagination': {
                    'total_items': total_count,
                    'total_pages': (total_count + per_page - 1) // per_page,
                    'current_page': page,
                    'per_page': per_page
                },
                'statistics': statistics
            }
            
        except Exception as e:
            logger.error(f"통합 주문 조회 오류: {str(e)}")
            raise
    
    @staticmethod
    def _calculate_statistics(start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """통계 정보 계산"""
        try:
            # 네이버 통계
            naver_stats = db.session.execute(text("""
                SELECT 
                    COUNT(DISTINCT npo.product_order_id) as total,
                    SUM(CASE WHEN npo.product_order_status = 'PAYED' THEN 1 ELSE 0 END) as new_orders,
                    SUM(CASE WHEN npo.product_order_status = 'DELIVERING' THEN 1 ELSE 0 END) as delivering,
                    SUM(npo.total_product_amount) as total_amount
                FROM naver_product_orders npo
                JOIN naver_orders no ON npo.order_id = no.order_id
                WHERE no.order_date BETWEEN :start_date AND :end_date
            """), {'start_date': start_date, 'end_date': end_date}).first()
            
            # 쿠팡 통계
            coupang_stats = db.session.execute(text("""
                SELECT 
                    COUNT(DISTINCT cos.shipment_box_id) as total,
                    SUM(CASE WHEN cos.status = 'ACCEPT' THEN 1 ELSE 0 END) as new_orders,
                    SUM(CASE WHEN cos.status = 'DELIVERING' THEN 1 ELSE 0 END) as delivering,
                    (SELECT SUM(coi.order_price) 
                     FROM coupang_order_items coi 
                     JOIN coupang_order_sheets cos2 ON coi.shipment_box_id = cos2.shipment_box_id
                     WHERE cos2.ordered_at BETWEEN :start_date AND :end_date) as total_amount
                FROM coupang_order_sheets cos
                WHERE cos.ordered_at BETWEEN :start_date AND :end_date
            """), {'start_date': start_date, 'end_date': end_date}).first()
            
            return {
                'total': (naver_stats.total or 0) + (coupang_stats.total or 0),
                'new_orders': (naver_stats.new_orders or 0) + (coupang_stats.new_orders or 0),
                'delivering': (naver_stats.delivering or 0) + (coupang_stats.delivering or 0),
                'total_amount': (naver_stats.total_amount or 0) + (coupang_stats.total_amount or 0),
                'naver': {
                    'total': naver_stats.total or 0,
                    'amount': naver_stats.total_amount or 0
                },
                'coupang': {
                    'total': coupang_stats.total or 0,
                    'amount': coupang_stats.total_amount or 0
                }
            }
            
        except Exception as e:
            logger.error(f"통계 계산 오류: {str(e)}")
            return {
                'total': 0,
                'new_orders': 0,
                'delivering': 0,
                'total_amount': 0,
                'naver': {'total': 0, 'amount': 0},
                'coupang': {'total': 0, 'amount': 0}
            }