#!/usr/bin/env python3
"""
쿠팡 테이블 생성 스크립트
"""

import os
import sys
import pymysql
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def create_coupang_tables():
    """쿠팡 관련 테이블 생성"""
    # MariaDB 연결 정보
    host = os.getenv('DB_HOST', '192.168.0.109')
    port = int(os.getenv('DB_PORT', '3306'))
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '~Asy10131227')
    db_name = os.getenv('DB_NAME', 'trade_naver_cupang')
    
    try:
        # MariaDB 연결
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 쿠팡 발주서 테이블 생성
            cursor.execute("""
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
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ coupang_order_sheets 테이블 생성 완료")
            
            # 쿠팡 주문 아이템 테이블 생성
            cursor.execute("""
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
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ coupang_order_items 테이블 생성 완료")
            
            # 쿠팡 주문 동기화 이력 테이블 생성
            cursor.execute("""
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
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ coupang_order_sync 테이블 생성 완료")
            
            connection.commit()
            
            # 생성된 테이블 확인
            cursor.execute("SHOW TABLES LIKE 'coupang%'")
            tables = cursor.fetchall()
            print(f"\n📊 쿠팡 테이블 생성 확인 ({len(tables)}개):")
            for table in tables:
                print(f"   - {table[0]}")
                
        connection.close()
        
    except Exception as e:
        print(f"❌ Error creating Coupang tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 쿠팡 테이블 생성 시작...")
    print("-" * 50)
    
    if create_coupang_tables():
        print("-" * 50)
        print("✨ 쿠팡 테이블 생성이 성공적으로 완료되었습니다!")
    else:
        print("❌ 쿠팡 테이블 생성 실패")