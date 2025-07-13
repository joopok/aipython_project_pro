
import http.client
import json
import base64
import hmac
import hashlib
import time
import urllib.parse
import pandas as pd
import os
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum


class OrderStatus(Enum):
    """주문 상태"""
    PAYED = "PAYED"  # 결제완료
    PLACE = "PLACE"  # 발주확인
    DISPATCHED = "DISPATCHED"  # 출고완료
    DELIVERED = "DELIVERED"  # 배송완료
    CANCELED = "CANCELED"  # 취소
    RETURNED = "RETURNED"  # 반품
    EXCHANGED = "EXCHANGED"  # 교환


class ProductStatus(Enum):
    """상품 상태"""
    SALE = "SALE"  # 판매중
    OUTOFSTOCK = "OUTOFSTOCK"  # 품절
    SUSPENSION = "SUSPENSION"  # 판매중지
    CLOSE = "CLOSE"  # 판매종료


class NaverCommerceAPI:
    """네이버 커머스 API v2.59.0 완전 통합 클라이언트"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "api.commerce.naver.com"
        self.token = None
        self.token_expires_at = None
        self.last_request_time = 0
        self.request_interval = 0.5  # 초당 2회 제한
        
    def _get_signature(self, timestamp: str) -> str:
        """API 서명 생성"""
        message = f"{self.client_id}\n{timestamp}"
        signature = base64.b64encode(
            hmac.new(
                self.client_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode()
        return signature
    
    def _rate_limit(self):
        """Rate limit 처리 (초당 2회)"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.request_interval:
            time.sleep(self.request_interval - time_since_last_request)
        
        self.last_request_time = time.time()
    
    # ===== 1. 인증 API (1개) =====
    def get_access_token(self) -> str:
        """1.1 OAuth 2.0 액세스 토큰 발급"""
        if self.token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.token
            
        timestamp = str(int(time.time() * 1000))
        client_secret_sign = self._get_signature(timestamp)
        
        payload = urllib.parse.urlencode({
            'client_id': self.client_id,
            'timestamp': timestamp,
            'client_secret_sign': client_secret_sign,
            'grant_type': 'client_credentials',
            'type': 'SELF'
        })
        
        conn = http.client.HTTPSConnection(self.base_url)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        try:
            conn.request("POST", "/external/v1/oauth2/token", payload, headers)
            res = conn.getresponse()
            data = json.loads(res.read().decode("utf-8"))
            
            if 'access_token' in data:
                self.token = data['access_token']
                self.token_expires_at = datetime.now() + timedelta(hours=3, minutes=-5)
                print("✅ 토큰 발급 성공")
                return self.token
            else:
                raise Exception(f"토큰 발급 실패: {data}")
                
        except Exception as e:
            print(f"❌ 인증 오류: {str(e)}")
            raise
        finally:
            conn.close()
    
    def _api_request(self, method: str, endpoint: str, body: Optional[Dict] = None, 
                    params: Optional[Dict] = None, is_file: bool = False) -> Union[Dict, bytes]:
        """API 요청 공통 메서드"""
        self._rate_limit()
        token = self.get_access_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        if body and not is_file:
            headers['Content-Type'] = 'application/json'
            
        url = endpoint
        if params:
            url += '?' + urllib.parse.urlencode(params)
            
        conn = http.client.HTTPSConnection(self.base_url)
        
        try:
            if body:
                if is_file:
                    conn.request(method, url, body, headers)
                else:
                    conn.request(method, url, json.dumps(body), headers)
            else:
                conn.request(method, url, headers=headers)
                
            res = conn.getresponse()
            data = res.read()
            
            if res.status in [200, 201]:
                if is_file:
                    return data
                return json.loads(data.decode('utf-8')) if data else {}
            else:
                error_data = json.loads(data.decode('utf-8')) if data else {}
                raise Exception(f"API 오류 (상태: {res.status}): {error_data}")
                
        except Exception as e:
            print(f"❌ API 요청 실패: {str(e)}")
            raise
        finally:
            conn.close()
    
    # ===== 2. API데이터솔루션(통계) (5개) =====
    def get_daily_sales_stats(self, start_date: str, end_date: str, data_type: str = "PAYMENT_DATE") -> Dict:
        """2.1 일별 매출 통계 조회"""
        params = {
            'startDate': start_date,
            'endDate': end_date,
            'dataType': data_type
        }
        return self._api_request("GET", "/external/v1/pay-stat/seller/daily", params=params)
    
    def get_product_sales_stats(self, start_date: str, end_date: str) -> Dict:
        """2.2 상품별 매출 통계 조회"""
        params = {
            'startDate': start_date,
            'endDate': end_date
        }
        return self._api_request("GET", "/external/v1/pay-stat/seller/product", params=params)
    
    def get_category_sales_stats(self, start_date: str, end_date: str) -> Dict:
        """2.3 카테고리별 매출 통계 조회"""
        params = {
            'startDate': start_date,
            'endDate': end_date
        }
        return self._api_request("GET", "/external/v1/pay-stat/seller/category", params=params)
    
    def get_customer_stats(self, start_date: str, end_date: str) -> Dict:
        """2.4 구매자 통계 조회"""
        params = {
            'startDate': start_date,
            'endDate': end_date
        }
        return self._api_request("GET", "/external/v1/pay-stat/seller/customer", params=params)
    
    def get_traffic_stats(self, start_date: str, end_date: str) -> Dict:
        """2.5 방문자 통계 조회"""
        params = {
            'startDate': start_date,
            'endDate': end_date
        }
        return self._api_request("GET", "/external/v1/traffic-stat/seller/daily", params=params)
    
    # ===== 3. 문의 (3개) =====
    def get_customer_inquiries(self, start_date: str, end_date: str, 
                             answered: Optional[bool] = None, page: int = 1, size: int = 100) -> Dict:
        """3.1 고객 문의 목록 조회"""
        params = {
            'startDate': start_date,
            'endDate': end_date,
            'page': page,
            'size': size
        }
        if answered is not None:
            params['answered'] = 'true' if answered else 'false'
            
        return self._api_request("GET", "/external/v1/customer-inquiries", params=params)
    
    def answer_inquiry(self, inquiry_id: str, answer: str) -> Dict:
        """3.2 문의 답변 등록"""
        body = {"answer": answer}
        return self._api_request("POST", f"/external/v1/customer-inquiries/{inquiry_id}/answer", body)
    
    def update_inquiry_status(self, inquiry_id: str, status: str) -> Dict:
        """3.3 문의 상태 변경"""
        body = {"status": status}
        return self._api_request("PUT", f"/external/v1/customer-inquiries/{inquiry_id}/status", body)
    
    # ===== 4. 상품 (21개) =====
    def search_products(self, query: str, size: int = 100, page: int = 1) -> Dict:
        """4.1 상품 검색"""
        body = {
            "query": query,
            "size": size,
            "page": page
        }
        return self._api_request("POST", "/external/v1/products/search", body)
    
    def get_product(self, product_id: str) -> Dict:
        """4.2 상품 상세 조회"""
        return self._api_request("GET", f"/external/v1/products/{product_id}")
    
    def get_product_list(self, page: int = 1, size: int = 100, status: Optional[str] = None) -> Dict:
        """4.3 상품 목록 조회"""
        params = {
            'page': page,
            'size': size
        }
        if status:
            params['status'] = status
        return self._api_request("GET", "/external/v1/products", params=params)
    
    def create_product(self, product_data: Dict) -> Dict:
        """4.4 상품 등록"""
        return self._api_request("POST", "/external/v2/products", product_data)
    
    def update_product(self, product_id: str, product_data: Dict) -> Dict:
        """4.5 상품 수정"""
        return self._api_request("PUT", f"/external/v2/products/{product_id}", product_data)
    
    def delete_product(self, product_id: str) -> Dict:
        """4.6 상품 삭제"""
        return self._api_request("DELETE", f"/external/v2/products/{product_id}")
    
    def change_product_status(self, product_id: str, status: str) -> Dict:
        """4.7 상품 상태 변경"""
        body = {"status": status}
        return self._api_request("PATCH", f"/external/v2/products/{product_id}/status", body)
    
    def get_product_reviews(self, product_id: str, page: int = 1, size: int = 100) -> Dict:
        """4.8 상품 리뷰 조회"""
        params = {
            'page': page,
            'size': size
        }
        return self._api_request("GET", f"/external/v1/products/{product_id}/reviews", params=params)
    
    def get_product_questions(self, product_id: str, page: int = 1, size: int = 100) -> Dict:
        """4.9 상품 문의 조회"""
        params = {
            'page': page,
            'size': size
        }
        return self._api_request("GET", f"/external/v1/products/{product_id}/questions", params=params)
    
    def answer_product_question(self, product_id: str, question_id: str, answer: str) -> Dict:
        """4.10 상품 문의 답변"""
        body = {"answer": answer}
        return self._api_request("POST", f"/external/v1/products/{product_id}/questions/{question_id}/answer", body)
    
    def get_categories(self, category_id: Optional[str] = None) -> Dict:
        """4.11 카테고리 조회"""
        params = {}
        if category_id:
            params['categoryId'] = category_id
        return self._api_request("GET", "/external/v1/categories", params=params)
    
    def get_category_attributes(self, category_id: str) -> Dict:
        """4.12 카테고리 속성 조회"""
        return self._api_request("GET", f"/external/v1/categories/{category_id}/attributes")
    
    def bulk_create_products(self, products: List[Dict]) -> Dict:
        """4.13 상품 일괄 등록"""
        body = {"products": products}
        return self._api_request("POST", "/external/v2/products/bulk", body)
    
    def bulk_update_products(self, products: List[Dict]) -> Dict:
        """4.14 상품 일괄 수정"""
        body = {"products": products}
        return self._api_request("PUT", "/external/v2/products/bulk", body)
    
    def get_product_options(self, product_id: str) -> Dict:
        """4.15 상품 옵션 조회"""
        return self._api_request("GET", f"/external/v1/products/{product_id}/options")
    
    def update_product_options(self, product_id: str, options: List[Dict]) -> Dict:
        """4.16 상품 옵션 수정"""
        body = {"options": options}
        return self._api_request("PUT", f"/external/v1/products/{product_id}/options", body)
    
    def get_product_inventory(self, product_id: str) -> Dict:
        """4.17 상품 재고 조회"""
        return self._api_request("GET", f"/external/v1/products/{product_id}/inventory")
    
    def update_product_inventory(self, product_id: str, inventory_data: Dict) -> Dict:
        """4.18 상품 재고 수정"""
        return self._api_request("PUT", f"/external/v1/products/{product_id}/inventory", inventory_data)
    
    def get_product_images(self, product_id: str) -> Dict:
        """4.19 상품 이미지 조회"""
        return self._api_request("GET", f"/external/v1/products/{product_id}/images")
    
    def upload_product_image(self, product_id: str, image_data: bytes, image_order: int = 0) -> Dict:
        """4.20 상품 이미지 업로드"""
        # 이미지 업로드는 multipart/form-data 형식 필요
        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Content-Type': 'multipart/form-data'
        }
        # 실제 구현시 multipart 인코딩 필요
        return {"message": "이미지 업로드 API는 별도 구현 필요"}
    
    def delete_product_image(self, product_id: str, image_id: str) -> Dict:
        """4.21 상품 이미지 삭제"""
        return self._api_request("DELETE", f"/external/v1/products/{product_id}/images/{image_id}")
    
    # ===== 5. 정산 (2개) =====
    def get_daily_settlement(self, start_date: str, end_date: str) -> Dict:
        """5.1 일별 정산 내역 조회"""
        params = {
            'startDate': start_date,
            'endDate': end_date
        }
        return self._api_request("GET", "/external/v1/pay-settle/seller/daily-settlement", params=params)
    
    def get_product_settlement(self, start_date: str, end_date: str) -> Dict:
        """5.2 상품별 정산 내역 조회"""
        params = {
            'startDate': start_date,
            'endDate': end_date
        }
        return self._api_request("GET", "/external/v1/pay-settle/seller/product-settlement", params=params)
    
    # ===== 6. 주문 (5개) =====
    def get_order_list(self, start_date: datetime, end_date: datetime, 
                      status: Optional[str] = None, page: int = 1, size: int = 100) -> Dict:
        """6.1 주문 목록 조회"""
        params = {
            'lastChangedFrom': start_date.strftime('%Y-%m-%dT%H:%M:%S.000+09:00'),
            'lastChangedTo': end_date.strftime('%Y-%m-%dT%H:%M:%S.000+09:00'),
            'page': page,
            'size': size
        }
        if status:
            params['productOrderStatus'] = status
            
        return self._api_request("GET", "/external/v1/pay-order/seller/orders", params=params)
    
    def get_order_details(self, product_order_ids: List[str]) -> List[Dict]:
        """6.2 주문 상세 조회 (최대 300개)"""
        all_details = []
        
        for i in range(0, len(product_order_ids), 300):
            batch = product_order_ids[i:i+300]
            body = {"productOrderIds": batch}
            result = self._api_request("POST", "/external/v1/pay-order/seller/product-orders/query", body)
            all_details.extend(result.get('productOrders', []))
            
        return all_details
    
    def confirm_orders(self, product_order_ids: List[str]) -> List[Dict]:
        """6.3 발주 확인"""
        results = []
        
        for i in range(0, len(product_order_ids), 300):
            batch = product_order_ids[i:i+300]
            body = {"productOrderIds": batch}
            
            try:
                result = self._api_request("POST", "/external/v1/pay-order/seller/product-orders/confirm", body)
                results.append({
                    'success': True,
                    'count': len(batch),
                    'response': result
                })
                print(f"✅ 발주 확인 성공: {len(batch)}건")
            except Exception as e:
                results.append({
                    'success': False,
                    'count': len(batch),
                    'error': str(e)
                })
                print(f"❌ 발주 확인 실패: {str(e)}")
                
        return results
    
    def ship_order(self, order_id: str, delivery_company: str, tracking_number: str, 
                  send_date: Optional[str] = None) -> Dict:
        """6.4 출고 처리"""
        body = {
            "deliveryCompany": delivery_company,
            "trackingNumber": tracking_number
        }
        if send_date:
            body['sendDate'] = send_date
            
        return self._api_request("POST", f"/external/v1/pay-order/seller/orders/{order_id}/ship", body)
    
    def cancel_order(self, product_order_id: str, cancel_reason: str = "INTENT_CHANGED", 
                    detailed_reason: str = "") -> Dict:
        """6.5 주문 취소"""
        body = {
            "cancelReason": cancel_reason,
            "cancelDetailedReason": detailed_reason
        }
        
        return self._api_request("POST", 
            f"/external/v1/pay-order/seller/product-orders/{product_order_id}/cancel", body)
    
    # ===== 7. 커머스솔루션 (4개) =====
    def get_recommended_tags(self, keyword: str, limit: int = 10) -> Dict:
        """7.1 추천 태그 조회"""
        params = {
            'keyword': keyword,
            'limit': limit
        }
        return self._api_request("GET", "/external/v1/tags/recommended", params=params)
    
    def get_restricted_tags(self) -> Dict:
        """7.2 제한 태그 조회"""
        return self._api_request("GET", "/external/v1/tags/restricted")
    
    def get_shopping_window_products(self, page: int = 1, size: int = 100) -> Dict:
        """7.3 쇼핑윈도 상품 조회"""
        params = {
            'page': page,
            'size': size
        }
        return self._api_request("GET", "/external/v1/shopping-window/products", params=params)
    
    def register_shopping_window_product(self, product_id: str, window_data: Dict) -> Dict:
        """7.4 쇼핑윈도 상품 등록"""
        body = {
            "productId": product_id,
            **window_data
        }
        return self._api_request("POST", "/external/v1/shopping-window/products", body)
    
    # ===== 8. 판매자정보 (4개) =====
    def get_seller_info(self) -> Dict:
        """8.1 판매자 정보 조회"""
        return self._api_request("GET", "/external/v1/seller/info")
    
    def update_seller_info(self, seller_data: Dict) -> Dict:
        """8.2 판매자 정보 수정"""
        return self._api_request("PUT", "/external/v1/seller/info", seller_data)
    
    def get_address_book(self, page: int = 1, size: int = 100) -> Dict:
        """8.3 주소록 목록 조회"""
        params = {
            'page': page,
            'size': size
        }
        return self._api_request("GET", "/external/v1/seller/address-book", params=params)
    
    def get_address(self, address_id: str) -> Dict:
        """8.4 주소록 단건 조회"""
        return self._api_request("GET", f"/external/v1/seller/address-book/{address_id}")
    
    # ===== 유틸리티 메서드 =====
    def save_to_excel(self, data: Union[List[Dict], Dict], filename: str) -> str:
        """데이터를 엑셀로 저장"""
        if isinstance(data, dict) and 'data' in data:
            data = data['data']
        elif isinstance(data, dict):
            data = [data]
            
        df = pd.json_normalize(data)
        path = os.path.join(os.path.expanduser("~/Downloads"), filename)
        df.to_excel(path, index=False, engine='openpyxl')
        print(f"✅ 저장 완료: {path}")
        return path
    
    def save_to_json(self, data: Any, filename: str) -> str:
        """데이터를 JSON으로 저장"""
        path = os.path.join(os.path.expanduser("~/Downloads"), filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON 저장 완료: {path}")
        return path


def print_api_summary():
    """API 요약 정보 출력"""
    summary = """
    ╔════════════════════════════════════════════════════════════════╗
    ║         네이버 커머스 API v2.59.0 - 전체 45개 엔드포인트          ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ 카테고리         │ 개수 │ 주요 기능                             ║
    ╠═════════════════╪══════╪═══════════════════════════════════════╣
    ║ 1. 인증         │  1   │ OAuth 2.0 토큰 발급                    ║
    ║ 2. 통계         │  5   │ 매출, 상품, 카테고리, 고객, 방문자      ║
    ║ 3. 문의         │  3   │ 조회, 답변, 상태변경                   ║
    ║ 4. 상품         │  21  │ CRUD, 검색, 옵션, 재고, 이미지         ║
    ║ 5. 정산         │  2   │ 일별정산, 상품별정산                   ║
    ║ 6. 주문         │  5   │ 조회, 발주확인, 출고, 취소             ║
    ║ 7. 커머스솔루션  │  4   │ 태그, 쇼핑윈도                        ║
    ║ 8. 판매자정보    │  4   │ 정보조회/수정, 주소록                  ║
    ╠═════════════════╪══════╪═══════════════════════════════════════╣
    ║ 합계            │  45  │                                      ║
    ╚════════════════════════════════════════════════════════════════╝
    """
    print(summary)


def main():
    """CLI 인터페이스"""
    parser = argparse.ArgumentParser(
        description='네이버 커머스 API v2.59.0 완전 통합 클라이언트',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 하위 명령어
    subparsers = parser.add_subparsers(dest='category', help='API 카테고리')
    
    # 1. 인증
    auth_parser = subparsers.add_parser('auth', help='인증 관련')
    auth_parser.add_argument('--token', action='store_true', help='토큰 발급')
    
    # 2. 통계
    stats_parser = subparsers.add_parser('stats', help='통계 조회')
    stats_parser.add_argument('--type', choices=['daily', 'product', 'category', 'customer', 'traffic'], 
                            required=True, help='통계 유형')
    stats_parser.add_argument('--start', required=True, help='시작일 (YYYY-MM-DD)')
    stats_parser.add_argument('--end', required=True, help='종료일 (YYYY-MM-DD)')
    
    # 3. 문의
    inquiry_parser = subparsers.add_parser('inquiry', help='문의 관리')
    inquiry_parser.add_argument('--list', action='store_true', help='문의 목록 조회')
    inquiry_parser.add_argument('--answer', type=str, help='문의 ID와 답변')
    inquiry_parser.add_argument('--start', help='시작일')
    inquiry_parser.add_argument('--end', help='종료일')
    
    # 4. 상품
    product_parser = subparsers.add_parser('product', help='상품 관리')
    product_parser.add_argument('--action', choices=['list', 'search', 'get', 'create', 'update', 'delete'], 
                              required=True, help='작업')
    product_parser.add_argument('--id', help='상품 ID')
    product_parser.add_argument('--query', help='검색어')
    product_parser.add_argument('--status', choices=['SALE', 'OUTOFSTOCK', 'SUSPENSION', 'CLOSE'], 
                              help='상품 상태')
    product_parser.add_argument('--data', help='상품 데이터 (JSON 파일 경로)')
    
    # 5. 정산
    settle_parser = subparsers.add_parser('settle', help='정산 조회')
    settle_parser.add_argument('--type', choices=['daily', 'product'], default='daily', help='정산 유형')
    settle_parser.add_argument('--start', required=True, help='시작일 (YYYY-MM-DD)')
    settle_parser.add_argument('--end', required=True, help='종료일 (YYYY-MM-DD)')
    
    # 6. 주문
    order_parser = subparsers.add_parser('order', help='주문 관리')
    order_parser.add_argument('--action', choices=['list', 'detail', 'confirm', 'ship', 'cancel'], 
                            required=True, help='작업')
    order_parser.add_argument('--hours', type=int, default=24, help='최근 N시간')
    order_parser.add_argument('--status', help='주문 상태')
    order_parser.add_argument('--order-id', help='주문 ID')
    order_parser.add_argument('--company', help='택배사')
    order_parser.add_argument('--tracking', help='송장번호')
    
    # 7. 커머스솔루션
    solution_parser = subparsers.add_parser('solution', help='커머스 솔루션')
    solution_parser.add_argument('--tags', action='store_true', help='태그 관련')
    solution_parser.add_argument('--window', action='store_true', help='쇼핑윈도')
    solution_parser.add_argument('--keyword', help='키워드')
    
    # 8. 판매자정보
    seller_parser = subparsers.add_parser('seller', help='판매자 정보')
    seller_parser.add_argument('--info', action='store_true', help='판매자 정보 조회')
    seller_parser.add_argument('--address', action='store_true', help='주소록 조회')
    
    # 공통 옵션
    parser.add_argument('--client-id', help='클라이언트 ID')
    parser.add_argument('--client-secret', help='클라이언트 시크릿')
    parser.add_argument('--output', choices=['excel', 'json', 'print'], default='excel', 
                      help='출력 형식')
    parser.add_argument('--summary', action='store_true', help='API 요약 정보 출력')
    
    args = parser.parse_args()
    
    # API 요약 정보 출력
    if args.summary:
        print_api_summary()
        return
    
    if not args.category:
        parser.print_help()
        print("\n💡 Tip: --summary 옵션으로 전체 API 요약을 볼 수 있습니다.")
        return
    
    # 인증 정보 확인
    client_id = args.client_id or os.environ.get('NAVER_CLIENT_ID', '')
    client_secret = args.client_secret or os.environ.get('NAVER_CLIENT_SECRET', '')
    
    if not client_id or not client_secret:
        print("❌ 인증 정보가 필요합니다.")
        print("   --client-id와 --client-secret을 지정하거나")
        print("   환경변수 NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 설정하세요.")
        return
    
    # API 클라이언트 초기화
    api = NaverCommerceAPI(client_id, client_secret)
    
    try:
        result = None
        filename_prefix = f"{args.category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 카테고리별 처리
        if args.category == 'auth':
            if args.token:
                token = api.get_access_token()
                result = {"token": token, "expires_in": "3 hours"}
                
        elif args.category == 'stats':
            if args.type == 'daily':
                result = api.get_daily_sales_stats(args.start, args.end)
            elif args.type == 'product':
                result = api.get_product_sales_stats(args.start, args.end)
            elif args.type == 'category':
                result = api.get_category_sales_stats(args.start, args.end)
            elif args.type == 'customer':
                result = api.get_customer_stats(args.start, args.end)
            elif args.type == 'traffic':
                result = api.get_traffic_stats(args.start, args.end)
                
        elif args.category == 'inquiry':
            if args.list:
                result = api.get_customer_inquiries(args.start or '2024-01-01', 
                                                  args.end or datetime.now().strftime('%Y-%m-%d'))
            elif args.answer:
                # 형식: --answer "inquiry_id:답변내용"
                parts = args.answer.split(':', 1)
                if len(parts) == 2:
                    result = api.answer_inquiry(parts[0], parts[1])
                    
        elif args.category == 'product':
            if args.action == 'list':
                result = api.get_product_list(status=args.status)
            elif args.action == 'search' and args.query:
                result = api.search_products(args.query)
            elif args.action == 'get' and args.id:
                result = api.get_product(args.id)
            elif args.action == 'create' and args.data:
                with open(args.data, 'r', encoding='utf-8') as f:
                    product_data = json.load(f)
                result = api.create_product(product_data)
            elif args.action == 'update' and args.id and args.data:
                with open(args.data, 'r', encoding='utf-8') as f:
                    product_data = json.load(f)
                result = api.update_product(args.id, product_data)
            elif args.action == 'delete' and args.id:
                result = api.delete_product(args.id)
                
        elif args.category == 'settle':
            if args.type == 'daily':
                result = api.get_daily_settlement(args.start, args.end)
            else:
                result = api.get_product_settlement(args.start, args.end)
                
        elif args.category == 'order':
            if args.action == 'list':
                end_date = datetime.now()
                start_date = end_date - timedelta(hours=args.hours)
                result = api.get_order_list(start_date, end_date, args.status)
                
            elif args.action == 'confirm':
                # 최근 PAYED 상태 주문 조회 후 확인
                end_date = datetime.now()
                start_date = end_date - timedelta(hours=24)
                orders = api.get_order_list(start_date, end_date, 'PAYED')
                
                if orders.get('orders'):
                    product_order_ids = []
                    for order in orders['orders']:
                        # 상품 주문 ID 조회 로직 필요
                        pass
                    
                    if product_order_ids:
                        confirm = input(f"{len(product_order_ids)}건 발주 확인? (y/n): ")
                        if confirm.lower() == 'y':
                            result = api.confirm_orders(product_order_ids)
                            
            elif args.action == 'ship' and all([args.order_id, args.company, args.tracking]):
                result = api.ship_order(args.order_id, args.company, args.tracking)
                
        elif args.category == 'solution':
            if args.tags and args.keyword:
                result = api.get_recommended_tags(args.keyword)
            elif args.tags:
                result = api.get_restricted_tags()
            elif args.window:
                result = api.get_shopping_window_products()
                
        elif args.category == 'seller':
            if args.info:
                result = api.get_seller_info()
            elif args.address:
                result = api.get_address_book()
        
        # 결과 출력
        if result:
            if args.output == 'print':
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif args.output == 'json':
                filename = f"{filename_prefix}.json"
                api.save_to_json(result, filename)
            else:  # excel
                filename = f"{filename_prefix}.xlsx"
                api.save_to_excel(result, filename)
        else:
            print("⚠️ 결과가 없습니다. 파라미터를 확인하세요.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return 1
    
    return 0


# 사용 예제
def example_usage():
    """사용 예제 코드"""
    # 환경변수에서 인증정보 로드
    client_id = os.environ.get('NAVER_CLIENT_ID', 'your_client_id')
    client_secret = os.environ.get('NAVER_CLIENT_SECRET', 'your_client_secret')
    
    # API 클라이언트 생성
    api = NaverCommerceAPI(client_id, client_secret)
    
    # 1. 최근 24시간 주문 조회
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=24)
    orders = api.get_order_list(start_date, end_date)
    print(f"최근 24시간 주문: {len(orders.get('orders', []))}건")
    
    # 2. 상품 검색
    products = api.search_products("티셔츠")
    print(f"'티셔츠' 검색 결과: {len(products.get('products', []))}개")
    
    # 3. 매출 통계 조회
    stats = api.get_daily_sales_stats('2024-01-01', '2024-01-31')
    print(f"1월 매출 통계: {stats}")
    
    # 4. 정산 조회
    settlement = api.get_daily_settlement('2024-01-01', '2024-01-31')
    print(f"1월 정산 내역: {settlement}")
    
    # 5. 고객 문의 조회
    inquiries = api.get_customer_inquiries('2024-01-01', '2024-01-31', answered=False)
    print(f"미답변 문의: {len(inquiries.get('inquiries', []))}건")


if __name__ == "__main__":
    exit(main())
