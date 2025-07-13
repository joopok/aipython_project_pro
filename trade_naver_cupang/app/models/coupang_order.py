"""
쿠팡 주문 데이터베이스 모델
"""
from datetime import datetime
from app import db


class CoupangOrderSheet(db.Model):
    """쿠팡 발주서 모델"""
    __tablename__ = 'coupang_order_sheets'
    
    # 기본 정보
    shipment_box_id = db.Column(db.BigInteger, primary_key=True)
    order_id = db.Column(db.BigInteger, nullable=False, index=True)
    vendor_id = db.Column(db.String(20), nullable=False, index=True)
    
    # 주문 정보
    ordered_at = db.Column(db.DateTime, nullable=False)
    paid_at = db.Column(db.DateTime)
    status = db.Column(db.String(50), nullable=False, index=True)
    
    # 주문자 정보
    orderer_name = db.Column(db.String(100))
    orderer_email = db.Column(db.String(200))
    orderer_safe_number = db.Column(db.String(50))
    orderer_number = db.Column(db.String(50))
    
    # 수취인 정보
    receiver_name = db.Column(db.String(100))
    receiver_safe_number = db.Column(db.String(50))
    receiver_number = db.Column(db.String(50))
    receiver_addr1 = db.Column(db.String(500))
    receiver_addr2 = db.Column(db.String(500))
    receiver_post_code = db.Column(db.String(10))
    
    # 배송 정보
    shipping_price = db.Column(db.Integer, default=0)
    remote_price = db.Column(db.Integer, default=0)
    remote_area = db.Column(db.Boolean, default=False)
    parcel_print_message = db.Column(db.String(500))
    split_shipping = db.Column(db.Boolean, default=False)
    able_split_shipping = db.Column(db.Boolean, default=False)
    
    # 배송 추적 정보
    delivery_company_name = db.Column(db.String(50))
    invoice_number = db.Column(db.String(50))
    in_trasit_date_time = db.Column(db.DateTime)
    delivered_date = db.Column(db.DateTime)
    
    # 기타 정보
    refer = db.Column(db.String(100))
    shipment_type = db.Column(db.String(50))
    
    # 타임스탬프
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    order_items = db.relationship('CoupangOrderItem', backref='order_sheet', lazy='dynamic')
    
    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            'shipmentBoxId': self.shipment_box_id,
            'orderId': self.order_id,
            'orderedAt': self.ordered_at.isoformat() if self.ordered_at else None,
            'orderer': {
                'name': self.orderer_name,
                'email': self.orderer_email,
                'safeNumber': self.orderer_safe_number,
                'ordererNumber': self.orderer_number
            },
            'paidAt': self.paid_at.isoformat() if self.paid_at else None,
            'status': self.status,
            'shippingPrice': self.shipping_price,
            'remotePrice': self.remote_price,
            'remoteArea': self.remote_area,
            'parcelPrintMessage': self.parcel_print_message,
            'splitShipping': self.split_shipping,
            'ableSplitShipping': self.able_split_shipping,
            'receiver': {
                'name': self.receiver_name,
                'safeNumber': self.receiver_safe_number,
                'receiverNumber': self.receiver_number,
                'addr1': self.receiver_addr1,
                'addr2': self.receiver_addr2,
                'postCode': self.receiver_post_code
            },
            'orderItems': [item.to_dict() for item in self.order_items],
            'deliveryCompanyName': self.delivery_company_name,
            'invoiceNumber': self.invoice_number,
            'inTrasitDateTime': self.in_trasit_date_time.isoformat() if self.in_trasit_date_time else None,
            'deliveredDate': self.delivered_date.isoformat() if self.delivered_date else None,
            'refer': self.refer,
            'shipmentType': self.shipment_type
        }


class CoupangOrderItem(db.Model):
    """쿠팡 주문 아이템 모델"""
    __tablename__ = 'coupang_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    shipment_box_id = db.Column(db.BigInteger, db.ForeignKey('coupang_order_sheets.shipment_box_id'), nullable=False)
    
    # 상품 정보
    vendor_item_package_id = db.Column(db.BigInteger, default=0)
    vendor_item_package_name = db.Column(db.String(500))
    product_id = db.Column(db.BigInteger, nullable=False)
    vendor_item_id = db.Column(db.BigInteger, nullable=False)
    vendor_item_name = db.Column(db.String(500))
    seller_product_id = db.Column(db.BigInteger)
    seller_product_name = db.Column(db.String(500))
    seller_product_item_name = db.Column(db.String(500))
    first_seller_product_item_name = db.Column(db.String(500))
    
    # 수량 및 가격 정보
    shipping_count = db.Column(db.Integer, default=1)
    sales_price = db.Column(db.Integer, default=0)
    order_price = db.Column(db.Integer, default=0)
    discount_price = db.Column(db.Integer, default=0)
    instant_coupon_discount = db.Column(db.Integer, default=0)
    downloadable_coupon_discount = db.Column(db.Integer, default=0)
    coupang_discount = db.Column(db.Integer, default=0)
    
    # SKU 정보
    external_vendor_sku_code = db.Column(db.String(100))
    etc_info_header = db.Column(db.String(200))
    etc_info_value = db.Column(db.String(500))
    etc_info_values = db.Column(db.JSON)
    
    # 취소 및 배송 정보
    cancel_count = db.Column(db.Integer, default=0)
    hold_count_for_cancel = db.Column(db.Integer, default=0)
    estimated_shipping_date = db.Column(db.Date)
    planned_shipping_date = db.Column(db.Date)
    invoice_number_upload_date = db.Column(db.DateTime)
    
    # 기타 정보
    extra_properties = db.Column(db.JSON)
    pricing_badge = db.Column(db.Boolean, default=False)
    used_product = db.Column(db.Boolean, default=False)
    confirm_date = db.Column(db.DateTime)
    delivery_charge_type_name = db.Column(db.String(50))
    
    # 묶음 배송 정보
    up_bundle_vendor_item_id = db.Column(db.BigInteger)
    up_bundle_vendor_item_name = db.Column(db.String(500))
    up_bundle_size = db.Column(db.Integer)
    up_bundle_item = db.Column(db.Boolean, default=False)
    
    # 상태
    canceled = db.Column(db.Boolean, default=False)
    
    # 타임스탬프
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            'vendorItemPackageId': self.vendor_item_package_id,
            'vendorItemPackageName': self.vendor_item_package_name,
            'productId': self.product_id,
            'vendorItemId': self.vendor_item_id,
            'vendorItemName': self.vendor_item_name,
            'shippingCount': self.shipping_count,
            'salesPrice': self.sales_price,
            'orderPrice': self.order_price,
            'discountPrice': self.discount_price,
            'instantCouponDiscount': self.instant_coupon_discount,
            'downloadableCouponDiscount': self.downloadable_coupon_discount,
            'coupangDiscount': self.coupang_discount,
            'externalVendorSkuCode': self.external_vendor_sku_code,
            'etcInfoHeader': self.etc_info_header,
            'etcInfoValue': self.etc_info_value,
            'etcInfoValues': self.etc_info_values,
            'sellerProductId': self.seller_product_id,
            'sellerProductName': self.seller_product_name,
            'sellerProductItemName': self.seller_product_item_name,
            'firstSellerProductItemName': self.first_seller_product_item_name,
            'cancelCount': self.cancel_count,
            'holdCountForCancel': self.hold_count_for_cancel,
            'estimatedShippingDate': self.estimated_shipping_date.isoformat() if self.estimated_shipping_date else '',
            'plannedShippingDate': self.planned_shipping_date.isoformat() if self.planned_shipping_date else '',
            'invoiceNumberUploadDate': self.invoice_number_upload_date.isoformat() if self.invoice_number_upload_date else None,
            'extraProperties': self.extra_properties or {},
            'pricingBadge': self.pricing_badge,
            'usedProduct': self.used_product,
            'confirmDate': self.confirm_date.isoformat() if self.confirm_date else None,
            'deliveryChargeTypeName': self.delivery_charge_type_name,
            'upBundleVendorItemId': self.up_bundle_vendor_item_id,
            'upBundleVendorItemName': self.up_bundle_vendor_item_name,
            'upBundleSize': self.up_bundle_size,
            'upBundleItem': self.up_bundle_item,
            'canceled': self.canceled
        }


class CoupangOrderSync(db.Model):
    """쿠팡 주문 동기화 로그"""
    __tablename__ = 'coupang_order_sync'
    
    id = db.Column(db.Integer, primary_key=True)
    sync_date = db.Column(db.DateTime, default=datetime.utcnow)
    sync_type = db.Column(db.String(50))  # FULL, INCREMENTAL
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer)
    total_count = db.Column(db.Integer, default=0)
    success_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    
    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'syncDate': self.sync_date.isoformat() if self.sync_date else None,
            'syncType': self.sync_type,
            'startTime': self.start_time.isoformat() if self.start_time else None,
            'endTime': self.end_time.isoformat() if self.end_time else None,
            'durationSeconds': self.duration_seconds,
            'totalCount': self.total_count,
            'successCount': self.success_count,
            'failedCount': self.failed_count,
            'errorMessage': self.error_message
        }


# 상수 정의
class OrderStatus:
    """주문 상태 상수"""
    ACCEPT = "ACCEPT"  # 결제완료
    INSTRUCT = "INSTRUCT"  # 상품준비중
    DEPARTURE = "DEPARTURE"  # 배송지시
    DELIVERING = "DELIVERING"  # 배송중
    FINAL_DELIVERY = "FINAL_DELIVERY"  # 배송완료
    NONE_TRACKING = "NONE_TRACKING"  # 업체직송


class ShipmentType:
    """배송 타입 상수"""
    THIRD_PARTY = "THIRD_PARTY"  # 업체배송
    COUPANG = "COUPANG"  # 쿠팡배송