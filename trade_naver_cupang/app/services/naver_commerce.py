"""
네이버 커머스 API 서비스 모듈
네이버 스마트스토어 주문 조회 및 관리 기능
"""
import os
import requests
import hmac
import hashlib
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class NaverCommerceAPI:
    """네이버 커머스 API 클라이언트"""
    
    def __init__(self):
        """API 클라이언트 초기화"""
        self.client_id = os.getenv('NAVER_CLIENT_ID')
        self.client_secret = os.getenv('NAVER_CLIENT_SECRET')
        self.base_url = "https://api.commerce.naver.com"
        
        if not self.client_id or not self.client_secret:
            logger.warning("네이버 API 인증 정보가 설정되지 않았습니다.")
    
    def _generate_signature(self, method: str, url: str, timestamp: str) -> str:
        """API 요청 서명 생성"""
        message = f"{method} {url}\n{timestamp}\n{self.client_id}"
        signature = hmac.new(
            self.client_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return signature.hex()
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """API 요청 실행"""
        url = f"{self.base_url}{endpoint}"
        timestamp = str(int(time.time() * 1000))
        
        headers = {
            'Authorization': f'CEA algorithm=HmacSHA256, access-key={self.client_id}, signed-date={timestamp}, signature={self._generate_signature(method, endpoint, timestamp)}',
            'Content-Type': 'application/json',
            'X-Timestamp': timestamp
        }
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"네이버 API 요청 실패: {str(e)}")
            raise
    
    def get_product_orders(self, 
                          start_date: datetime = None,
                          end_date: datetime = None,
                          status: str = None,
                          page: int = 1,
                          size: int = 50) -> Dict[str, Any]:
        """
        상품 주문 목록 조회
        
        Args:
            start_date: 조회 시작일
            end_date: 조회 종료일
            status: 주문 상태 필터
            page: 페이지 번호
            size: 페이지 크기
            
        Returns:
            주문 목록 및 페이징 정보
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()
            
        params = {
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'page': page,
            'size': size
        }
        
        if status:
            params['productOrderStatus'] = status
            
        return self._make_request('GET', '/external/v1/pay-order/seller/product-orders', params=params)
    
    def get_product_order_detail(self, product_order_id: str) -> Dict[str, Any]:
        """
        상품 주문 상세 정보 조회
        
        Args:
            product_order_id: 상품 주문 ID
            
        Returns:
            주문 상세 정보
        """
        params = {'productOrderId': product_order_id}
        return self._make_request('GET', '/external/v1/pay-order/seller/product-orders/details', params=params)
    
    def get_changed_product_orders(self,
                                  last_changed_from: datetime,
                                  last_changed_to: datetime = None,
                                  change_type: str = None) -> Dict[str, Any]:
        """
        변경된 상품 주문 조회
        
        Args:
            last_changed_from: 변경 시작 시간
            last_changed_to: 변경 종료 시간
            change_type: 변경 유형 (CANCEL, RETURN, EXCHANGE)
            
        Returns:
            변경된 주문 목록
        """
        if not last_changed_to:
            last_changed_to = datetime.now()
            
        params = {
            'lastChangedFrom': last_changed_from.isoformat(),
            'lastChangedTo': last_changed_to.isoformat()
        }
        
        if change_type:
            params['lastChangedType'] = change_type
            
        return self._make_request('GET', '/external/v1/pay-order/seller/product-orders/changed', params=params)
    
    def update_product_order_status(self, 
                                   product_order_id: str,
                                   status: str,
                                   dispatch_date: datetime = None) -> Dict[str, Any]:
        """
        상품 주문 상태 변경
        
        Args:
            product_order_id: 상품 주문 ID
            status: 변경할 상태
            dispatch_date: 발송일 (발송 처리 시)
            
        Returns:
            처리 결과
        """
        data = {
            'productOrderIds': [product_order_id],
            'status': status
        }
        
        if dispatch_date and status == 'DISPATCHED':
            data['dispatchDate'] = dispatch_date.strftime('%Y-%m-%d')
            
        return self._make_request('PUT', '/external/v1/pay-order/seller/product-orders/status', data=data)
    
    def process_cancel(self,
                      product_order_id: str,
                      cancel_reason: str,
                      cancel_detailed_reason: str = None) -> Dict[str, Any]:
        """
        주문 취소 처리
        
        Args:
            product_order_id: 상품 주문 ID
            cancel_reason: 취소 사유 코드
            cancel_detailed_reason: 상세 취소 사유
            
        Returns:
            처리 결과
        """
        data = {
            'productOrderId': product_order_id,
            'cancelReason': cancel_reason
        }
        
        if cancel_detailed_reason:
            data['cancelDetailedReason'] = cancel_detailed_reason
            
        return self._make_request('POST', '/external/v1/pay-order/seller/product-orders/cancel', data=data)
    
    def process_return(self,
                      product_order_id: str,
                      return_reason: str,
                      collect_address: Dict[str, str],
                      return_detailed_reason: str = None) -> Dict[str, Any]:
        """
        반품 처리
        
        Args:
            product_order_id: 상품 주문 ID
            return_reason: 반품 사유 코드
            collect_address: 수거지 주소
            return_detailed_reason: 상세 반품 사유
            
        Returns:
            처리 결과
        """
        data = {
            'productOrderId': product_order_id,
            'returnReason': return_reason,
            'collectAddress': collect_address
        }
        
        if return_detailed_reason:
            data['returnDetailedReason'] = return_detailed_reason
            
        return self._make_request('POST', '/external/v1/pay-order/seller/product-orders/return', data=data)
    
    def process_exchange(self,
                        product_order_id: str,
                        exchange_reason: str,
                        collect_address: Dict[str, str],
                        exchange_detailed_reason: str = None) -> Dict[str, Any]:
        """
        교환 처리
        
        Args:
            product_order_id: 상품 주문 ID
            exchange_reason: 교환 사유 코드
            collect_address: 수거지 주소
            exchange_detailed_reason: 상세 교환 사유
            
        Returns:
            처리 결과
        """
        data = {
            'productOrderId': product_order_id,
            'exchangeReason': exchange_reason,
            'collectAddress': collect_address
        }
        
        if exchange_detailed_reason:
            data['exchangeDetailedReason'] = exchange_detailed_reason
            
        return self._make_request('POST', '/external/v1/pay-order/seller/product-orders/exchange', data=data)
    
    def update_tracking_info(self,
                           product_order_id: str,
                           delivery_company: str,
                           tracking_number: str) -> Dict[str, Any]:
        """
        송장 정보 업데이트
        
        Args:
            product_order_id: 상품 주문 ID
            delivery_company: 택배사 코드
            tracking_number: 송장번호
            
        Returns:
            처리 결과
        """
        data = {
            'productOrderId': product_order_id,
            'deliveryCompany': delivery_company,
            'trackingNumber': tracking_number
        }
        
        return self._make_request('PUT', '/external/v1/pay-order/seller/product-orders/tracking', data=data)
    
    def sync_orders(self, hours: int = 24) -> Dict[str, Any]:
        """
        최근 주문 동기화
        
        Args:
            hours: 동기화할 시간 범위 (기본 24시간)
            
        Returns:
            동기화 결과
        """
        try:
            # API 인증 정보 확인
            if not self.client_id or not self.client_secret:
                # 테스트용 더미 데이터 생성
                logger.info("API 인증 정보가 없어 테스트 데이터를 생성합니다.")
                return self._create_dummy_orders()
            
            # 변경된 주문 조회
            changed_orders = self.get_changed_product_orders(
                last_changed_from=datetime.now() - timedelta(hours=hours)
            )
            
            sync_result = {
                'total': 0,
                'synced': 0,
                'failed': 0,
                'errors': []
            }
            
            if 'data' in changed_orders:
                sync_result['total'] = len(changed_orders['data'])
                
                for order in changed_orders['data']:
                    try:
                        # 상세 정보 조회
                        detail = self.get_product_order_detail(order['productOrderId'])
                        # TODO: 데이터베이스에 저장
                        sync_result['synced'] += 1
                    except Exception as e:
                        sync_result['failed'] += 1
                        sync_result['errors'].append({
                            'productOrderId': order['productOrderId'],
                            'error': str(e)
                        })
                        
            return sync_result
            
        except Exception as e:
            logger.error(f"주문 동기화 실패: {str(e)}")
            raise
    
    def _create_dummy_orders(self) -> Dict[str, Any]:
        """테스트용 더미 주문 데이터 생성"""
        try:
            from app.models.naver_order import NaverOrder, NaverProductOrder
            from app import db
            import random
            
            # 샘플 데이터
            sample_products = [
                "에어팟 프로 2세대", "갤럭시 버즈2 프로", "애플워치 시리즈 9",
                "아이패드 에어 5세대", "갤럭시 탭 S9", "맥북 에어 M2",
                "LG 그램 17인치", "삼성 갤럭시북3 프로", "아이폰 15 프로",
                "갤럭시 S24 울트라"
            ]
            
            sample_names = ["김철수", "이영희", "박민수", "정수진", "최지훈", "강미영", "조현우", "임소정", "윤서준", "한지민"]
            
            statuses = [
                OrderStatus.PAYED, OrderStatus.PAYED, OrderStatus.PAYED,
                OrderStatus.DELIVERING, OrderStatus.DELIVERING,
                OrderStatus.DELIVERED, OrderStatus.DELIVERED,
                OrderStatus.PURCHASE_DECIDED
            ]
            
            created_count = 0
            
            # 10개의 더미 주문 생성
            for i in range(10):
                try:
                    # 주문 정보
                    order_date = datetime.now() - timedelta(days=random.randint(0, 7))
                    order_id = f"TEST{order_date.strftime('%Y%m%d')}{i:04d}"
                    
                    order = NaverOrder(
                        order_id=order_id,
                        order_date=order_date,
                        orderer_name=random.choice(sample_names),
                        orderer_tel=f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                        payment_date=order_date,
                        payment_amount=random.randint(50000, 2000000),
                        payment_method="CARD"
                    )
                    db.session.add(order)
                    
                    # 상품 주문 정보
                    product_order_id = f"{order_id}_001"
                    product_name = random.choice(sample_products)
                    quantity = random.randint(1, 3)
                    unit_price = random.randint(50000, 1500000)
                    
                    product_order = NaverProductOrder(
                        product_order_id=product_order_id,
                        order_id=order_id,
                        product_id=f"PROD{i:04d}",
                        product_name=product_name,
                        product_option=random.choice(["", "블랙", "화이트", "실버", "스페이스 그레이"]),
                        quantity=quantity,
                        unit_price=unit_price,
                        total_product_amount=unit_price * quantity,
                        product_order_status=random.choice(statuses),
                        recipient_name=order.orderer_name,
                        recipient_tel=order.orderer_tel,
                        recipient_zipcode=f"{random.randint(10000,99999)}",
                        recipient_address=f"서울특별시 강남구 테헤란로 {random.randint(1,500)}",
                        recipient_address_detail=f"{random.randint(1,20)}층 {random.randint(101,2099)}호",
                        shipping_memo="부재시 경비실에 맡겨주세요"
                    )
                    
                    # 배송중/배송완료 상태인 경우 송장번호 추가
                    if product_order.product_order_status in [OrderStatus.DELIVERING, OrderStatus.DELIVERED, OrderStatus.PURCHASE_DECIDED]:
                        product_order.delivery_company = random.choice(["CJGLS", "HANJIN", "LOTTE", "POST"])
                        product_order.tracking_number = f"{random.randint(100000000000, 999999999999)}"
                    
                    db.session.add(product_order)
                    created_count += 1
                    
                except Exception as e:
                    logger.error(f"더미 주문 생성 실패: {str(e)}")
            
            db.session.commit()
            
            return {
                'success': True,
                'total': created_count,
                'synced': created_count,
                'failed': 0,
                'message': f'테스트용 더미 주문 {created_count}건이 생성되었습니다.'
            }
            
        except Exception as e:
            logger.error(f"더미 데이터 생성 오류: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'total': 0,
                'synced': 0,
                'failed': 0,
                'error': str(e)
            }


# 상수 정의
class OrderStatus:
    """주문 상태 상수"""
    PAYED = "PAYED"  # 결제완료
    DELIVERING = "DELIVERING"  # 배송중
    DELIVERED = "DELIVERED"  # 배송완료
    PURCHASE_DECIDED = "PURCHASE_DECIDED"  # 구매확정
    CANCELED = "CANCELED"  # 취소
    RETURNED = "RETURNED"  # 반품
    EXCHANGED = "EXCHANGED"  # 교환


class ClaimType:
    """클레임 유형 상수"""
    CANCEL = "CANCEL"
    RETURN = "RETURN"
    EXCHANGE = "EXCHANGE"


class CancelReason:
    """취소 사유 코드"""
    CUSTOMER_CHANGE = "CUSTOMER_CHANGE"  # 고객 변심
    SOLD_OUT = "SOLD_OUT"  # 품절
    SHIPPING_DELAY = "SHIPPING_DELAY"  # 배송 지연
    
    
class DeliveryCompany:
    """택배사 코드"""
    CJ = "CJGLS"  # CJ대한통운
    HANJIN = "HANJIN"  # 한진택배
    LOTTE = "LOTTE"  # 롯데택배
    POST = "POST"  # 우체국택배
    LOGEN = "LOGEN"  # 로젠택배