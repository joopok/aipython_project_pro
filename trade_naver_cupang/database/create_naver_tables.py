#!/usr/bin/env python3
"""
네이버 커머스 관련 테이블 생성 스크립트
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

def create_naver_tables():
    """네이버 관련 테이블 생성"""
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
            # 네이버 주문 기본 정보 테이블
            cursor.execute("""
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
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ naver_orders 테이블 생성 완료")
            
            # 네이버 상품 주문 상세 테이블
            cursor.execute("""
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
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ naver_product_orders 테이블 생성 완료")
            
            # 네이버 클레임 정보 테이블
            cursor.execute("""
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
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ naver_claims 테이블 생성 완료")
            
            # 네이버 주문 동기화 이력 테이블
            cursor.execute("""
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
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ naver_order_sync 테이블 생성 완료")
            
            connection.commit()
            
            # 생성된 네이버 테이블 확인
            cursor.execute("SHOW TABLES LIKE 'naver_%'")
            tables = cursor.fetchall()
            print(f"\n📊 생성된 네이버 테이블 ({len(tables)}):")
            for table in tables:
                print(f"   - {table[0]}")
                
        connection.close()
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

def main():
    """메인 함수"""
    print("🚀 네이버 커머스 테이블 생성 시작...")
    print("-" * 50)
    
    if create_naver_tables():
        print("-" * 50)
        print("✨ 네이버 커머스 테이블 생성 완료!")
    else:
        print("❌ 테이블 생성 실패")
        sys.exit(1)

if __name__ == "__main__":
    main()