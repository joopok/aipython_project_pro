"""
네이버 주문 데이터베이스 모델
"""
from datetime import datetime
from app import db


class NaverOrder(db.Model):
    """네이버 주문 기본 정보"""
    __tablename__ = 'naver_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    orderer_id = db.Column(db.String(100))
    orderer_name = db.Column(db.String(100))
    orderer_tel = db.Column(db.String(20))
    
    # 결제 정보
    payment_date = db.Column(db.DateTime)
    payment_means = db.Column(db.String(50))
    total_payment_amount = db.Column(db.Integer, default=0)
    order_discount_amount = db.Column(db.Integer, default=0)
    
    # 타임스탬프
    order_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    product_orders = db.relationship('NaverProductOrder', backref='order', lazy='dynamic')
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'orderer_name': self.orderer_name,
            'orderer_tel': self.orderer_tel,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_means': self.payment_means,
            'total_payment_amount': self.total_payment_amount,
            'order_date': self.order_date.isoformat() if self.order_date else None
        }


class NaverProductOrder(db.Model):
    """네이버 상품 주문 상세"""
    __tablename__ = 'naver_product_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    product_order_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    order_id = db.Column(db.String(50), db.ForeignKey('naver_orders.order_id'), nullable=False)
    
    # 상품 정보
    product_id = db.Column(db.String(50))
    product_name = db.Column(db.String(500))
    product_option = db.Column(db.String(500))
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Integer, default=0)
    total_product_amount = db.Column(db.Integer, default=0)
    
    # 상태 정보
    product_order_status = db.Column(db.String(50), index=True)
    claim_type = db.Column(db.String(20))
    claim_status = db.Column(db.String(50))
    
    # 배송 정보
    delivery_method = db.Column(db.String(20))
    delivery_company = db.Column(db.String(50))
    tracking_number = db.Column(db.String(100))
    shipping_due_date = db.Column(db.DateTime)
    delivered_date = db.Column(db.DateTime)
    
    # 배송지 정보 (JSON으로 저장)
    shipping_address = db.Column(db.JSON)
    
    # 판매자 정보
    seller_product_code = db.Column(db.String(100))
    seller_custom_code1 = db.Column(db.String(100))
    seller_custom_code2 = db.Column(db.String(100))
    
    # 정산 정보
    commission_rate = db.Column(db.Float, default=0.0)
    payment_commission = db.Column(db.Integer, default=0)
    sale_commission = db.Column(db.Integer, default=0)
    expected_settlement_amount = db.Column(db.Integer, default=0)
    
    # 타임스탬프
    place_order_date = db.Column(db.DateTime)
    decision_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    claims = db.relationship('NaverClaim', backref='product_order', lazy='dynamic')
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'product_order_id': self.product_order_id,
            'order_id': self.order_id,
            'product_name': self.product_name,
            'product_option': self.product_option,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_product_amount': self.total_product_amount,
            'product_order_status': self.product_order_status,
            'claim_type': self.claim_type,
            'claim_status': self.claim_status,
            'tracking_number': self.tracking_number,
            'delivered_date': self.delivered_date.isoformat() if self.delivered_date else None
        }


class NaverClaim(db.Model):
    """네이버 클레임 정보 (취소/반품/교환)"""
    __tablename__ = 'naver_claims'
    
    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    product_order_id = db.Column(db.String(50), db.ForeignKey('naver_product_orders.product_order_id'), nullable=False)
    
    # 클레임 정보
    claim_type = db.Column(db.String(20), nullable=False)  # CANCEL, RETURN, EXCHANGE
    claim_status = db.Column(db.String(50), nullable=False)
    claim_reason = db.Column(db.String(100))
    claim_detailed_reason = db.Column(db.Text)
    request_quantity = db.Column(db.Integer, default=1)
    request_channel = db.Column(db.String(50))
    
    # 날짜 정보
    claim_request_date = db.Column(db.DateTime)
    claim_completed_date = db.Column(db.DateTime)
    refund_expected_date = db.Column(db.DateTime)
    
    # 수거 정보 (반품/교환)
    collect_status = db.Column(db.String(50))
    collect_tracking_number = db.Column(db.String(100))
    collect_delivery_company = db.Column(db.String(50))
    collect_completed_date = db.Column(db.DateTime)
    
    # 재배송 정보 (교환)
    re_delivery_status = db.Column(db.String(50))
    re_delivery_tracking_number = db.Column(db.String(100))
    re_delivery_company = db.Column(db.String(50))
    
    # 비용 정보
    claim_delivery_fee = db.Column(db.Integer, default=0)
    etc_fee = db.Column(db.Integer, default=0)
    
    # 타임스탬프
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'claim_id': self.claim_id,
            'product_order_id': self.product_order_id,
            'claim_type': self.claim_type,
            'claim_status': self.claim_status,
            'claim_reason': self.claim_reason,
            'claim_detailed_reason': self.claim_detailed_reason,
            'request_quantity': self.request_quantity,
            'claim_request_date': self.claim_request_date.isoformat() if self.claim_request_date else None,
            'collect_status': self.collect_status,
            'collect_tracking_number': self.collect_tracking_number
        }


class NaverOrderSync(db.Model):
    """네이버 주문 동기화 이력"""
    __tablename__ = 'naver_order_sync'
    
    id = db.Column(db.Integer, primary_key=True)
    sync_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    sync_type = db.Column(db.String(20))  # FULL, INCREMENTAL
    
    # 동기화 결과
    total_count = db.Column(db.Integer, default=0)
    success_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    
    # 실행 정보
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'sync_date': self.sync_date.isoformat() if self.sync_date else None,
            'sync_type': self.sync_type,
            'total_count': self.total_count,
            'success_count': self.success_count,
            'failed_count': self.failed_count,
            'duration_seconds': self.duration_seconds
        }