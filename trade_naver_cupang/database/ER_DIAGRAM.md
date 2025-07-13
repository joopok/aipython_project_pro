# 데이터베이스 ER 다이어그램 설명서

## 주요 테이블 구조

### 1. 사용자 관리
- **users**: 시스템 사용자 정보

### 2. 기본 정보 관리
- **carriers**: 운송사(법송인) 정보 관리
- **platforms**: 판매 플랫폼 정보 (네이버, 쿠팡 등)
- **customers**: 고객 정보 (개인/사업자 구분)
- **products**: 상품 마스터 정보

### 3. 주문 관리
- **orders**: 주문 기본 정보
  - platform_id → platforms (플랫폼)
  - customer_id → customers (고객)
  - carrier_id → carriers (운송사)
- **order_items**: 주문 상세 상품 정보
  - order_id → orders (주문)
  - product_id → products (상품)

### 4. 배송 관리
- **shipments**: 배송 추적 및 비용 정보
  - order_id → orders (주문)
  - 각종 비용 정보 포함 (고객부과세, 정산부과세, 관세수수료 등)

### 5. 항공화물 관리
- **hawb_master**: HAWB(항공화물운송장) 마스터 정보
- **hawb_details**: HAWB별 주문 연결 정보
  - hawb_id → hawb_master
  - order_id → orders

### 6. 재고 관리
- **inventory**: 상품별 재고 현황
  - product_id → products
- **inventory_transactions**: 재고 입출고 이력
  - product_id → products
  - performed_by → users

### 7. 정산 관리
- **settlements**: 정산 마스터 정보
- **settlement_details**: 정산 상세 내역
  - settlement_id → settlements
  - order_id → orders

### 8. 시스템 관리
- **api_logs**: API 호출 로그
- **system_settings**: 시스템 설정값
- **file_uploads**: 파일 업로드 이력

## 주요 관계

1. **주문 흐름**
   - 플랫폼 → 주문 → 주문상세 → 상품
   - 주문 → 고객
   - 주문 → 운송사

2. **배송 흐름**
   - 주문 → 배송 → 각종 비용
   - 주문 → HAWB 상세 → HAWB 마스터

3. **재고 흐름**
   - 상품 → 재고 → 재고거래내역

4. **정산 흐름**
   - 주문 → 정산상세 → 정산마스터

## 정규화 특징

1. **3차 정규형 준수**
   - 모든 속성이 기본키에 완전 함수 종속
   - 이행적 종속성 제거

2. **참조 무결성**
   - 외래키 제약조건 설정
   - CASCADE DELETE 적용 (주문-주문상세, 정산-정산상세 등)

3. **인덱스 최적화**
   - 주요 검색 필드에 인덱스 설정
   - 복합 유니크 키 설정 (product_id + warehouse_location)

4. **확장성 고려**
   - 다중 플랫폼 지원
   - 다중 운송사 지원
   - 다중 창고 지원