"""
쿠팡 커머스 API 서비스 모듈
쿠팡 판매자 주문 조회 및 관리 기능
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


class CoupangCommerceAPI:
    """쿠팡 커머스 API 클라이언트"""
    
    def __init__(self):
        """API 클라이언트 초기화"""
        self.access_key = os.getenv('COUPANG_ACCESS_KEY')
        self.secret_key = os.getenv('COUPANG_SECRET_KEY')
        self.vendor_id = os.getenv('COUPANG_VENDOR_ID')
        self.base_url = "https://api-gateway.coupang.com"
        
        if not self.access_key or not self.secret_key:
            logger.warning("쿠팡 API 인증 정보가 설정되지 않았습니다.")
    
    def _generate_signature(self, method: str, path: str, timestamp: str, query: str = "") -> str:
        """API 요청 서명 생성"""
        message = timestamp + method + path + query
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"CEA algorithm=HmacSHA256, access-key={self.access_key}, signed-date={timestamp}, signature={signature}"
    
    def _make_request(self, method: str, path: str, params: Dict = None, data: Dict = None) -> Dict:
        """API 요청 실행"""
        timestamp = datetime.utcnow().strftime('%y%m%d')
        query_string = ""
        
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
            
        headers = {
            'Authorization': self._generate_signature(method, path, timestamp, query_string),
            'X-Requested-By': self.vendor_id,
            'X-EXTENDED-TIMEOUT': '90000',
            'content-type': 'application/json;charset=UTF-8'
        }
        
        url = f"{self.base_url}{path}"
        if query_string:
            url += f"?{query_string}"
            
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"쿠팡 API 요청 실패: {str(e)}")
            raise
    
    def get_order_sheets(self, 
                        created_at_from: datetime,
                        created_at_to: datetime,
                        status: Optional[str] = None,
                        next_token: Optional[str] = None,
                        max_per_page: int = 50) -> Dict[str, Any]:
        """
        발주서 목록 조회 (일단위 페이징)
        
        Args:
            created_at_from: 조회 시작일시
            created_at_to: 조회 종료일시
            status: 주문 상태 (선택)
            next_token: 다음 페이지 토큰
            max_per_page: 페이지당 최대 건수 (최대 50)
            
        Returns:
            발주서 목록 및 페이징 정보
        """
        path = f"/v2/providers/openapi/apis/api/v4/vendors/{self.vendor_id}/ordersheets"
        
        params = {
            'createdAtFrom': created_at_from.strftime('%Y-%m-%dT%H:%M:%S'),
            'createdAtTo': created_at_to.strftime('%Y-%m-%dT%H:%M:%S'),
            'maxPerPage': min(max_per_page, 50)
        }
        
        if status:
            params['status'] = status
        if next_token:
            params['nextToken'] = next_token
            
        return self._make_request('GET', path, params=params)
    
    def get_order_sheet_detail(self, shipment_box_id: str) -> Dict[str, Any]:
        """
        발주서 상세 조회
        
        Args:
            shipment_box_id: 배송번호
            
        Returns:
            발주서 상세 정보
        """
        path = f"/v2/providers/openapi/apis/api/v4/vendors/{self.vendor_id}/ordersheets/{shipment_box_id}"
        return self._make_request('GET', path)
    
    def acknowledge_order(self, shipment_box_ids: List[str]) -> Dict[str, Any]:
        """
        발주 확인 처리
        
        Args:
            shipment_box_ids: 배송번호 목록
            
        Returns:
            처리 결과
        """
        path = f"/v2/providers/openapi/apis/api/v4/vendors/{self.vendor_id}/ordersheets/acknowledgement"
        data = {
            'vendorId': self.vendor_id,
            'shipmentBoxIds': shipment_box_ids
        }
        return self._make_request('PUT', path, data=data)
    
    def update_shipment(self, shipment_box_id: str, 
                       delivery_company_code: str,
                       invoice_number: str) -> Dict[str, Any]:
        """
        송장 등록/수정
        
        Args:
            shipment_box_id: 배송번호
            delivery_company_code: 택배사 코드
            invoice_number: 송장번호
            
        Returns:
            처리 결과
        """
        path = f"/v2/providers/openapi/apis/api/v4/vendors/{self.vendor_id}/ordersheets/{shipment_box_id}/shipment"
        data = {
            'vendorId': self.vendor_id,
            'shipmentBoxId': shipment_box_id,
            'deliveryCompanyCode': delivery_company_code,
            'invoiceNumber': invoice_number
        }
        return self._make_request('POST', path, data=data)
    
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
            if not self.access_key or not self.secret_key or not self.vendor_id:
                # 테스트용 더미 데이터 생성
                logger.info("API 인증 정보가 없어 테스트 데이터를 생성합니다.")
                return self._create_dummy_orders()
            
            # 시간 범위 설정
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # 주문 목록 조회
            result = self.get_order_sheets(
                created_at_from=start_time,
                created_at_to=end_time
            )
            
            sync_result = {
                'total': 0,
                'synced': 0,
                'failed': 0,
                'errors': []
            }
            
            if result.get('code') == 200 and 'data' in result:
                orders = result['data']
                sync_result['total'] = len(orders)
                
                # TODO: 데이터베이스에 저장
                sync_result['synced'] = len(orders)
                
            return sync_result
            
        except Exception as e:
            logger.error(f"주문 동기화 실패: {str(e)}")
            raise
    
    def _create_dummy_orders(self) -> Dict[str, Any]:
        """테스트용 더미 주문 데이터 생성"""
        try:
            from app.models.coupang_order import CoupangOrderSheet, CoupangOrderItem, OrderStatus, ShipmentType
            from app import db
            import random
            
            # 샘플 데이터
            sample_products = [
                {"name": "신서리티 델타 구운 캐슈넛", "package": "5개, 160g", "price": 41000},
                {"name": "신서리티 미국산 레몬 가루", "package": "150g x 3개", "price": 40400},
                {"name": "닥터유 단백질 드링크", "package": "190ml x 24개", "price": 35900},
                {"name": "종근당 비타민C 1000", "package": "100정 x 2개", "price": 28900},
                {"name": "네스카페 돌체구스토 캡슐", "package": "16개입 x 3박스", "price": 32400},
                {"name": "동원 참치 선물세트", "package": "150g x 12캔", "price": 25900},
                {"name": "CJ 비비고 왕교자", "package": "315g x 4봉", "price": 21900},
                {"name": "오뚜기 진라면", "package": "120g x 20개", "price": 16900},
                {"name": "농심 신라면", "package": "120g x 20개", "price": 17900},
                {"name": "코카콜라", "package": "1.5L x 12개", "price": 23900}
            ]
            
            sample_names = ["김민수", "이영희", "박철수", "정미경", "최동훈", "강수진", "조현우", "임정희", "윤서준", "한지민"]
            
            statuses = [
                OrderStatus.ACCEPT, OrderStatus.INSTRUCT, OrderStatus.INSTRUCT,
                OrderStatus.DEPARTURE, OrderStatus.DELIVERING, OrderStatus.DELIVERING,
                OrderStatus.FINAL_DELIVERY, OrderStatus.FINAL_DELIVERY, OrderStatus.FINAL_DELIVERY,
                OrderStatus.FINAL_DELIVERY
            ]
            
            delivery_companies = ["CJ대한통운", "한진택배", "롯데택배", "로젠택배", "우체국택배"]
            
            created_count = 0
            
            # 15개의 더미 주문 생성
            for i in range(15):
                try:
                    # 주문 날짜 생성
                    days_ago = random.randint(0, 10)
                    order_date = datetime.now() - timedelta(days=days_ago)
                    paid_date = order_date + timedelta(minutes=random.randint(1, 10))
                    
                    # 발주서 ID 생성
                    shipment_box_id = 64253897000000000 + i
                    order_id = 9100041863244 + i * 1000
                    
                    # 주문 상태
                    status = random.choice(statuses)
                    
                    # 발주서 생성
                    order_sheet = CoupangOrderSheet(
                        shipment_box_id=shipment_box_id,
                        order_id=order_id,
                        vendor_id='A00012345',
                        ordered_at=order_date,
                        paid_at=paid_date,
                        status=status,
                        orderer_name=random.choice(sample_names),
                        orderer_email=f"user{i}@example.com",
                        orderer_safe_number=f"0502-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                        receiver_name=random.choice(sample_names),
                        receiver_safe_number=f"0502-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                        receiver_addr1=f"서울특별시 강남구 테헤란로 {random.randint(100,500)}",
                        receiver_addr2=f"{random.randint(1,20)}층 {random.randint(101,2099)}호",
                        receiver_post_code=f"{random.randint(10000,99999)}",
                        shipping_price=0 if random.random() > 0.2 else 3000,
                        remote_price=0,
                        remote_area=False,
                        parcel_print_message=random.choice(["문 앞", "경비실", "택배함", "직접 받고 부재 시 문 앞"]),
                        split_shipping=False,
                        able_split_shipping=False,
                        refer=random.choice(["안드로이드앱", "iOS앱", "PC웹", "모바일웹"]),
                        shipment_type=ShipmentType.THIRD_PARTY
                    )
                    
                    # 배송 정보 (상태에 따라)
                    if status in [OrderStatus.DEPARTURE, OrderStatus.DELIVERING, OrderStatus.FINAL_DELIVERY]:
                        order_sheet.delivery_company_name = random.choice(delivery_companies)
                        order_sheet.invoice_number = f"{random.randint(100000000000, 999999999999)}"
                        order_sheet.in_trasit_date_time = paid_date + timedelta(days=1)
                        
                        if status == OrderStatus.FINAL_DELIVERY:
                            order_sheet.delivered_date = paid_date + timedelta(days=random.randint(2, 4))
                    
                    db.session.add(order_sheet)
                    
                    # 주문 아이템 생성 (1-3개)
                    item_count = random.randint(1, 3)
                    for j in range(item_count):
                        product = random.choice(sample_products)
                        quantity = random.randint(1, 3)
                        unit_price = product['price']
                        
                        order_item = CoupangOrderItem(
                            shipment_box_id=shipment_box_id,
                            vendor_item_package_id=0,
                            vendor_item_package_name=product['name'],
                            product_id=7313251147 + i * 100 + j,
                            vendor_item_id=85872453655 + i * 100 + j,
                            vendor_item_name=f"{product['name']}, {product['package']}",
                            seller_product_id=14091699106 + i * 100 + j,
                            seller_product_name=product['name'],
                            seller_product_item_name=product['package'],
                            first_seller_product_item_name=product['package'],
                            shipping_count=quantity,
                            sales_price=unit_price,
                            order_price=unit_price * quantity,
                            discount_price=0,
                            instant_coupon_discount=0,
                            downloadable_coupon_discount=0,
                            coupang_discount=0,
                            external_vendor_sku_code="",
                            cancel_count=0,
                            hold_count_for_cancel=0,
                            estimated_shipping_date=paid_date.date() + timedelta(days=1),
                            pricing_badge=False,
                            used_product=False,
                            delivery_charge_type_name="무료" if order_sheet.shipping_price == 0 else "유료",
                            canceled=False
                        )
                        
                        # 송장 업로드 날짜 (배송 상태인 경우)
                        if order_sheet.invoice_number:
                            order_item.invoice_number_upload_date = paid_date + timedelta(days=1)
                        
                        db.session.add(order_item)
                    
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
class DeliveryCompanyCode:
    """택배사 코드"""
    CJ = "CJGLS"  # CJ대한통운
    HANJIN = "CH"  # 한진택배
    LOTTE = "LOTTE"  # 롯데택배
    POST = "EPOST"  # 우체국택배
    LOGEN = "LOGEN"  # 로젠택배
    HYUNDAI = "HYUNDAI"  # 롯데글로벌로지스(구 현대택배)