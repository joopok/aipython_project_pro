"""
쿠팡 주문 데이터베이스 모델 (별도 ORM용)
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime, Boolean, Float, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class CoupangOrderSheet(Base):
    """쿠팡 발주서 모델"""
    __tablename__ = 'coupang_order_sheets'
    
    # 기본 정보
    shipment_box_id = Column(BigInteger, primary_key=True)
    order_id = Column(BigInteger, nullable=False, index=True)
    vendor_id = Column(String(20), nullable=False, index=True)
    
    # 주문 정보
    ordered_at = Column(DateTime, nullable=False)
    paid_at = Column(DateTime)
    status = Column(String(50), nullable=False, index=True)
    
    # 주문자 정보
    orderer_name = Column(String(100))
    orderer_email = Column(String(200))
    orderer_safe_number = Column(String(50))
    orderer_number = Column(String(50))
    
    # 수취인 정보
    receiver_name = Column(String(100))
    receiver_safe_number = Column(String(50))
    receiver_number = Column(String(50))
    receiver_addr1 = Column(String(500))
    receiver_addr2 = Column(String(500))
    receiver_post_code = Column(String(10))
    
    # 배송 정보
    shipping_price = Column(Integer, default=0)
    remote_price = Column(Integer, default=0)
    remote_area = Column(Boolean, default=False)
    parcel_print_message = Column(String(500))
    split_shipping = Column(Boolean, default=False)
    able_split_shipping = Column(Boolean, default=False)
    
    # 배송 추적 정보
    delivery_company_name = Column(String(50))
    invoice_number = Column(String(50))
    in_trasit_date_time = Column(DateTime)
    delivered_date = Column(DateTime)
    
    # 기타 정보
    refer = Column(String(100))
    shipment_type = Column(String(50))
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    order_items = relationship('CoupangOrderItem', backref='order_sheet', lazy='dynamic')


class CoupangOrderItem(Base):
    """쿠팡 주문 아이템 모델"""
    __tablename__ = 'coupang_order_items'
    
    id = Column(Integer, primary_key=True)
    shipment_box_id = Column(BigInteger, ForeignKey('coupang_order_sheets.shipment_box_id'), nullable=False)
    
    # 상품 정보
    vendor_item_package_id = Column(BigInteger, default=0)
    vendor_item_package_name = Column(String(500))
    product_id = Column(BigInteger, nullable=False)
    vendor_item_id = Column(BigInteger, nullable=False)
    vendor_item_name = Column(String(500))
    seller_product_id = Column(BigInteger)
    seller_product_name = Column(String(500))
    seller_product_item_name = Column(String(500))
    first_seller_product_item_name = Column(String(500))
    
    # 수량 및 가격 정보
    shipping_count = Column(Integer, default=1)
    sales_price = Column(Integer, default=0)
    order_price = Column(Integer, default=0)
    discount_price = Column(Integer, default=0)
    instant_coupon_discount = Column(Integer, default=0)
    downloadable_coupon_discount = Column(Integer, default=0)
    coupang_discount = Column(Integer, default=0)
    
    # SKU 정보
    external_vendor_sku_code = Column(String(100))
    etc_info_header = Column(String(200))
    etc_info_value = Column(String(500))
    etc_info_values = Column(JSON)
    
    # 취소 및 배송 정보
    cancel_count = Column(Integer, default=0)
    hold_count_for_cancel = Column(Integer, default=0)
    estimated_shipping_date = Column(DateTime)
    planned_shipping_date = Column(DateTime)
    invoice_number_upload_date = Column(DateTime)
    
    # 기타 정보
    extra_properties = Column(JSON)
    pricing_badge = Column(Boolean, default=False)
    used_product = Column(Boolean, default=False)
    confirm_date = Column(DateTime)
    delivery_charge_type_name = Column(String(50))
    
    # 묶음 배송 정보
    up_bundle_vendor_item_id = Column(BigInteger)
    up_bundle_vendor_item_name = Column(String(500))
    up_bundle_size = Column(Integer)
    up_bundle_item = Column(Boolean, default=False)
    
    # 상태
    canceled = Column(Boolean, default=False)
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CoupangOrderSync(Base):
    """쿠팡 주문 동기화 로그"""
    __tablename__ = 'coupang_order_sync'
    
    id = Column(Integer, primary_key=True)
    sync_date = Column(DateTime, default=datetime.utcnow)
    sync_type = Column(String(50))  # FULL, INCREMENTAL
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer)
    total_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    error_message = Column(Text)