-- trade_naver_cupang 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS trade_naver_cupang
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE trade_naver_cupang;

-- 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    role ENUM('admin', 'manager', 'user') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 운송사(법송인) 테이블
CREATE TABLE IF NOT EXISTS carriers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    carrier_code VARCHAR(50) UNIQUE NOT NULL,
    carrier_name VARCHAR(100) NOT NULL,
    carrier_name_en VARCHAR(100),
    contact_info VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_carrier_code (carrier_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 플랫폼 테이블 (네이버, 쿠팡 등)
CREATE TABLE IF NOT EXISTS platforms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    api_key VARCHAR(255),
    api_secret VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 고객 테이블
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    phone2 VARCHAR(20),
    email VARCHAR(100),
    customs_number VARCHAR(50) COMMENT '통관부호/사업자번호',
    customer_type ENUM('individual', 'business') DEFAULT 'individual' COMMENT '개인/사업자',
    address_line1 VARCHAR(255) COMMENT '주소1',
    address_line2 VARCHAR(255) COMMENT '주소2',
    city VARCHAR(100),
    state_province VARCHAR(100),
    postal_code VARCHAR(20) COMMENT '우편번호',
    country VARCHAR(50) DEFAULT 'KR',
    memo TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_customer_code (customer_code),
    INDEX idx_name (name),
    INDEX idx_phone (phone),
    INDEX idx_customs_number (customs_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 상품 테이블
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL COMMENT '상품이름',
    name_en VARCHAR(255) COMMENT '상품이름(영문)',
    brand VARCHAR(100) COMMENT '브랜드',
    category VARCHAR(100),
    hs_code VARCHAR(20) COMMENT 'HS CODE',
    unit_price_usd DECIMAL(10,2) COMMENT '단가(USD)',
    weight_lb DECIMAL(10,3) COMMENT '무게(LB)',
    image_url VARCHAR(500),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_sku (sku),
    INDEX idx_name (name),
    INDEX idx_hs_code (hs_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 주문 테이블
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(100) UNIQUE NOT NULL COMMENT '주문번호',
    platform_id INT COMMENT '플랫폼 ID',
    customer_id INT COMMENT '고객 ID',
    carrier_id INT COMMENT '운송사 ID',
    platform_order_number VARCHAR(100) COMMENT '플랫폼 주문번호',
    customs_type ENUM('general', 'list') DEFAULT 'general' COMMENT '통관부호유무점 (목록:1, 개인:1)',
    order_date DATE NOT NULL COMMENT '주문날짜',
    registration_date DATETIME COMMENT '등록날짜',
    shipping_date DATE COMMENT '배송일자(날짜)',
    departure_date DATE COMMENT '출고날짜',
    order_status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled', 'returned') DEFAULT 'pending',
    payment_status ENUM('pending', 'paid', 'failed', 'refunded') DEFAULT 'pending',
    registration_type VARCHAR(50) COMMENT '대행등록형식',
    weight_lb DECIMAL(10,3) COMMENT '무게(총합)',
    box_count INT DEFAULT 1 COMMENT '박스갯수',
    shipping_method VARCHAR(50) COMMENT '배송방법',
    flag_status BOOLEAN DEFAULT FALSE COMMENT 'flag 상태',
    memo TEXT COMMENT '메모',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (platform_id) REFERENCES platforms(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (carrier_id) REFERENCES carriers(id),
    INDEX idx_order_number (order_number),
    INDEX idx_order_date (order_date),
    INDEX idx_order_status (order_status),
    INDEX idx_platform_order_number (platform_order_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 주문 상세 테이블
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT,
    product_name VARCHAR(255) NOT NULL COMMENT '상품이름',
    product_name_en VARCHAR(255) COMMENT '상품이름(영문)',
    sku VARCHAR(100),
    quantity INT NOT NULL COMMENT '갯수',
    unit_price_usd DECIMAL(10,2) COMMENT '단가',
    total_price_usd DECIMAL(10,2) COMMENT '총가격',
    hs_code VARCHAR(20) COMMENT 'HS CODE',
    memo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_order_id (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 배송 추적 테이블
CREATE TABLE IF NOT EXISTS shipments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    tracking_number VARCHAR(100) UNIQUE NOT NULL COMMENT '운송장 번호',
    carrier VARCHAR(50) COMMENT '운송사',
    shipment_status ENUM('preparing', 'in_transit', 'out_for_delivery', 'delivered', 'failed', 'returned') DEFAULT 'preparing' COMMENT '배송상태',
    customs_clearance_status ENUM('pending', 'processing', 'cleared', 'held', 'rejected') DEFAULT 'pending' COMMENT '통관상태',
    shipment_date DATETIME COMMENT '발송일시',
    delivery_date DATETIME COMMENT '배송완료일시',
    customs_clearance_date DATETIME COMMENT '통관완료일시',
    recipient_name VARCHAR(100) COMMENT '수령인',
    recipient_phone VARCHAR(20) COMMENT '수령인 전화번호',
    delivery_address TEXT COMMENT '배송주소',
    
    -- 비용 관련 필드
    product_cost_usd DECIMAL(10,2) COMMENT '화물가격',
    customer_tax_krw DECIMAL(12,2) COMMENT '고객부과세',
    customer_customs_fee_krw DECIMAL(12,2) COMMENT '고객부과관세수수료',
    settlement_tax_krw DECIMAL(12,2) COMMENT '정산부과세',
    carrier_customs_fee_krw DECIMAL(12,2) COMMENT '운송부과관세수수료',
    shipping_fee_krw DECIMAL(12,2) COMMENT '배송료',
    tax_krw DECIMAL(12,2) COMMENT '과세',
    
    memo TEXT COMMENT '비고',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    INDEX idx_tracking_number (tracking_number),
    INDEX idx_shipment_status (shipment_status),
    INDEX idx_shipment_date (shipment_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 재고 테이블
CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    warehouse_location VARCHAR(50) DEFAULT 'US',
    quantity_on_hand INT DEFAULT 0,
    quantity_reserved INT DEFAULT 0,
    quantity_available INT AS (quantity_on_hand - quantity_reserved) STORED,
    reorder_level INT DEFAULT 0,
    last_restock_date DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    UNIQUE KEY unique_product_warehouse (product_id, warehouse_location),
    INDEX idx_product_id (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 재고 거래 내역 테이블
CREATE TABLE IF NOT EXISTS inventory_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    transaction_type ENUM('in', 'out', 'adjustment') NOT NULL,
    quantity INT NOT NULL,
    reference_type VARCHAR(50),
    reference_id INT,
    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    reason VARCHAR(255),
    performed_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (performed_by) REFERENCES users(id),
    INDEX idx_product_id (product_id),
    INDEX idx_transaction_date (transaction_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 정산 테이블
CREATE TABLE IF NOT EXISTS settlements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    settlement_number VARCHAR(50) UNIQUE NOT NULL,
    settlement_date DATE NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_sales_usd DECIMAL(12,2) COMMENT '총매출(USD)',
    total_cost_usd DECIMAL(12,2) COMMENT '총원가(USD)',
    total_shipping_krw DECIMAL(12,2) COMMENT '총배송비(KRW)',
    total_tax_krw DECIMAL(12,2) COMMENT '총세금(KRW)',
    total_fees_krw DECIMAL(12,2) COMMENT '총수수료(KRW)',
    exchange_rate DECIMAL(10,2) COMMENT '환율',
    net_amount_krw DECIMAL(12,2) COMMENT '순이익(KRW)',
    settlement_status ENUM('pending', 'processing', 'completed', 'cancelled') DEFAULT 'pending',
    payment_date DATE,
    memo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_settlement_date (settlement_date),
    INDEX idx_settlement_status (settlement_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 정산 상세 테이블
CREATE TABLE IF NOT EXISTS settlement_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    settlement_id INT NOT NULL,
    order_id INT NOT NULL,
    sales_amount_usd DECIMAL(10,2) COMMENT '매출액(USD)',
    cost_amount_usd DECIMAL(10,2) COMMENT '원가(USD)',
    shipping_fee_krw DECIMAL(10,2) COMMENT '배송비(KRW)',
    customer_tax_krw DECIMAL(10,2) COMMENT '고객부과세(KRW)',
    settlement_tax_krw DECIMAL(10,2) COMMENT '정산부과세(KRW)',
    customs_fee_krw DECIMAL(10,2) COMMENT '관세수수료(KRW)',
    net_amount_krw DECIMAL(10,2) COMMENT '순이익(KRW)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (settlement_id) REFERENCES settlements(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    INDEX idx_settlement_id (settlement_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- HAWB (항공화물운송장) 테이블
CREATE TABLE IF NOT EXISTS hawb_master (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hawb_number VARCHAR(50) UNIQUE NOT NULL COMMENT 'HAWB 번호',
    mawb_number VARCHAR(50) COMMENT 'MAWB 번호',
    flight_date DATE COMMENT '항공일자',
    total_weight_lb DECIMAL(10,3) COMMENT '총무게(LB)',
    total_pieces INT COMMENT '총개수',
    carrier VARCHAR(100) COMMENT '항공사',
    origin_airport VARCHAR(10) COMMENT '출발공항',
    destination_airport VARCHAR(10) COMMENT '도착공항',
    status ENUM('draft', 'confirmed', 'shipped', 'arrived', 'delivered') DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_hawb_number (hawb_number),
    INDEX idx_mawb_number (mawb_number),
    INDEX idx_flight_date (flight_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- HAWB 상세 (주문 연결) 테이블
CREATE TABLE IF NOT EXISTS hawb_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hawb_id INT NOT NULL,
    order_id INT NOT NULL,
    weight_lb DECIMAL(10,3) COMMENT '무게(LB)',
    pieces INT COMMENT '개수',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hawb_id) REFERENCES hawb_master(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    UNIQUE KEY unique_hawb_order (hawb_id, order_id),
    INDEX idx_hawb_id (hawb_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- API 로그 테이블
CREATE TABLE IF NOT EXISTS api_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    platform_id INT,
    api_endpoint VARCHAR(255),
    request_method VARCHAR(10),
    request_data TEXT,
    response_data TEXT,
    response_status INT,
    error_message TEXT,
    execution_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (platform_id) REFERENCES platforms(id),
    INDEX idx_created_at (created_at),
    INDEX idx_platform_id (platform_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 시스템 설정 테이블
CREATE TABLE IF NOT EXISTS system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 파일 업로드 이력 테이블
CREATE TABLE IF NOT EXISTS file_uploads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) COMMENT '엑셀, CSV 등',
    upload_type VARCHAR(50) COMMENT '주문업로드, 재고업로드 등',
    total_rows INT COMMENT '총 행 수',
    success_rows INT COMMENT '성공 행 수',
    failed_rows INT COMMENT '실패 행 수',
    error_log TEXT COMMENT '에러 로그',
    uploaded_by INT,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users(id),
    INDEX idx_upload_date (upload_date),
    INDEX idx_upload_type (upload_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 네이버 주문 기본 정보 테이블
CREATE TABLE IF NOT EXISTS naver_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(50) UNIQUE NOT NULL,
    orderer_id VARCHAR(100),
    orderer_name VARCHAR(100),
    orderer_tel VARCHAR(20),
    payment_date DATETIME,
    payment_means VARCHAR(50),
    total_payment_amount INT DEFAULT 0,
    order_discount_amount INT DEFAULT 0,
    order_date DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_order_id (order_id),
    INDEX idx_order_date (order_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 네이버 상품 주문 상세 테이블
CREATE TABLE IF NOT EXISTS naver_product_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_order_id VARCHAR(50) UNIQUE NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50),
    product_name VARCHAR(500),
    product_option VARCHAR(500),
    quantity INT DEFAULT 1,
    unit_price INT DEFAULT 0,
    total_product_amount INT DEFAULT 0,
    product_order_status VARCHAR(50),
    claim_type VARCHAR(20),
    claim_status VARCHAR(50),
    delivery_method VARCHAR(20),
    delivery_company VARCHAR(50),
    tracking_number VARCHAR(100),
    shipping_due_date DATETIME,
    shipping_start_date DATETIME,
    delivered_date DATETIME,
    shipping_address JSON,
    seller_product_code VARCHAR(100),
    seller_custom_code1 VARCHAR(100),
    seller_custom_code2 VARCHAR(100),
    commission_rate FLOAT DEFAULT 0.0,
    payment_commission INT DEFAULT 0,
    sale_commission INT DEFAULT 0,
    expected_settlement_amount INT DEFAULT 0,
    place_order_date DATETIME,
    decision_date DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES naver_orders(order_id),
    INDEX idx_product_order_id (product_order_id),
    INDEX idx_product_order_status (product_order_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 네이버 클레임 정보 테이블 (취소/반품/교환)
CREATE TABLE IF NOT EXISTS naver_claims (
    id INT AUTO_INCREMENT PRIMARY KEY,
    claim_id VARCHAR(50) UNIQUE NOT NULL,
    product_order_id VARCHAR(50) NOT NULL,
    claim_type VARCHAR(20) NOT NULL,
    claim_status VARCHAR(50) NOT NULL,
    claim_reason VARCHAR(100),
    claim_detailed_reason TEXT,
    request_quantity INT DEFAULT 1,
    request_channel VARCHAR(50),
    claim_request_date DATETIME,
    claim_completed_date DATETIME,
    refund_expected_date DATETIME,
    collect_status VARCHAR(50),
    collect_tracking_number VARCHAR(100),
    collect_delivery_company VARCHAR(50),
    collect_completed_date DATETIME,
    re_delivery_status VARCHAR(50),
    re_delivery_tracking_number VARCHAR(100),
    re_delivery_company VARCHAR(50),
    claim_delivery_fee INT DEFAULT 0,
    etc_fee INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_order_id) REFERENCES naver_product_orders(product_order_id),
    INDEX idx_claim_id (claim_id),
    INDEX idx_claim_type (claim_type),
    INDEX idx_claim_status (claim_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 네이버 주문 동기화 이력 테이블
CREATE TABLE IF NOT EXISTS naver_order_sync (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sync_date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    sync_type VARCHAR(20),
    total_count INT DEFAULT 0,
    success_count INT DEFAULT 0,
    failed_count INT DEFAULT 0,
    error_message TEXT,
    start_time DATETIME,
    end_time DATETIME,
    duration_seconds INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sync_date (sync_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 쿠팡 발주서 테이블
CREATE TABLE IF NOT EXISTS coupang_order_sheets (
    shipment_box_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    vendor_id VARCHAR(20) NOT NULL,
    ordered_at DATETIME NOT NULL,
    paid_at DATETIME,
    status VARCHAR(50) NOT NULL,
    orderer_name VARCHAR(100),
    orderer_email VARCHAR(200),
    orderer_safe_number VARCHAR(50),
    orderer_number VARCHAR(50),
    receiver_name VARCHAR(100),
    receiver_safe_number VARCHAR(50),
    receiver_number VARCHAR(50),
    receiver_addr1 VARCHAR(500),
    receiver_addr2 VARCHAR(500),
    receiver_post_code VARCHAR(10),
    shipping_price INT DEFAULT 0,
    remote_price INT DEFAULT 0,
    remote_area BOOLEAN DEFAULT FALSE,
    parcel_print_message VARCHAR(500),
    split_shipping BOOLEAN DEFAULT FALSE,
    able_split_shipping BOOLEAN DEFAULT FALSE,
    delivery_company_name VARCHAR(50),
    invoice_number VARCHAR(50),
    in_trasit_date_time DATETIME,
    delivered_date DATETIME,
    refer VARCHAR(100),
    shipment_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_order_id (order_id),
    INDEX idx_vendor_id (vendor_id),
    INDEX idx_status (status),
    INDEX idx_ordered_at (ordered_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 쿠팡 주문 아이템 테이블
CREATE TABLE IF NOT EXISTS coupang_order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shipment_box_id BIGINT NOT NULL,
    vendor_item_package_id BIGINT DEFAULT 0,
    vendor_item_package_name VARCHAR(500),
    product_id BIGINT NOT NULL,
    vendor_item_id BIGINT NOT NULL,
    vendor_item_name VARCHAR(500),
    seller_product_id BIGINT,
    seller_product_name VARCHAR(500),
    seller_product_item_name VARCHAR(500),
    first_seller_product_item_name VARCHAR(500),
    shipping_count INT DEFAULT 1,
    sales_price INT DEFAULT 0,
    order_price INT DEFAULT 0,
    discount_price INT DEFAULT 0,
    instant_coupon_discount INT DEFAULT 0,
    downloadable_coupon_discount INT DEFAULT 0,
    coupang_discount INT DEFAULT 0,
    external_vendor_sku_code VARCHAR(100),
    etc_info_header VARCHAR(200),
    etc_info_value VARCHAR(500),
    etc_info_values JSON,
    cancel_count INT DEFAULT 0,
    hold_count_for_cancel INT DEFAULT 0,
    estimated_shipping_date DATE,
    planned_shipping_date DATE,
    invoice_number_upload_date DATETIME,
    extra_properties JSON,
    pricing_badge BOOLEAN DEFAULT FALSE,
    used_product BOOLEAN DEFAULT FALSE,
    confirm_date DATETIME,
    delivery_charge_type_name VARCHAR(50),
    up_bundle_vendor_item_id BIGINT,
    up_bundle_vendor_item_name VARCHAR(500),
    up_bundle_size INT,
    up_bundle_item BOOLEAN DEFAULT FALSE,
    canceled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (shipment_box_id) REFERENCES coupang_order_sheets(shipment_box_id),
    INDEX idx_product_id (product_id),
    INDEX idx_vendor_item_id (vendor_item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 쿠팡 주문 동기화 이력 테이블
CREATE TABLE IF NOT EXISTS coupang_order_sync (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sync_date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    sync_type VARCHAR(50),
    start_time DATETIME,
    end_time DATETIME,
    duration_seconds INT,
    total_count INT DEFAULT 0,
    success_count INT DEFAULT 0,
    failed_count INT DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sync_date (sync_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 초기 데이터 삽입
INSERT INTO platforms (name, code) VALUES
('네이버 스마트스토어', 'NAVER'),
('쿠팡', 'COUPANG'),
('11번가', '11ST'),
('G마켓', 'GMARKET');

INSERT INTO carriers (carrier_code, carrier_name, carrier_name_en) VALUES
('CONNECTLAB', 'Connectlab, Inc (Vita)', 'Connectlab, Inc (Vita)'),
('DHL', 'DHL', 'DHL'),
('FEDEX', 'FedEx', 'FedEx'),
('UPS', 'UPS', 'UPS'),
('USPS', 'USPS', 'USPS');

-- 관리자 계정은 create_admin_user.py 스크립트를 통해 생성합니다.
-- python database/create_admin_user.py

INSERT INTO system_settings (setting_key, setting_value, setting_type, description) VALUES
('default_currency', 'USD', 'string', '기본 통화'),
('exchange_rate_usd_krw', '1300', 'number', 'USD to KRW 환율'),
('default_shipping_method', 'air', 'string', '기본 배송 방법'),
('customs_threshold', '150', 'number', '면세 한도 (USD)'),
('hawb_prefix', 'HAWB', 'string', 'HAWB 번호 접두사'),
('auto_tracking_update', 'true', 'boolean', '자동 배송 추적 업데이트');