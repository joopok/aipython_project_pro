from sqlalchemy import Column, Integer, String, DateTime, Decimal, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db_config import Base

class Shipment(Base):
    __tablename__ = 'shipments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    tracking_number = Column(String(100), unique=True, nullable=False)
    carrier = Column(String(50))
    shipment_status = Column(Enum('preparing', 'in_transit', 'out_for_delivery', 'delivered', 'failed', 'returned'), default='preparing')
    customs_clearance_status = Column(Enum('pending', 'processing', 'cleared', 'held', 'rejected'), default='pending')
    shipment_date = Column(DateTime)
    delivery_date = Column(DateTime)
    customs_clearance_date = Column(DateTime)
    recipient_name = Column(String(100))
    recipient_phone = Column(String(20))
    delivery_address = Column(Text)
    
    # 비용 관련 필드
    product_cost_usd = Column(Decimal(10, 2))
    customer_tax_krw = Column(Decimal(12, 2))
    customer_customs_fee_krw = Column(Decimal(12, 2))
    settlement_tax_krw = Column(Decimal(12, 2))
    carrier_customs_fee_krw = Column(Decimal(12, 2))
    shipping_fee_krw = Column(Decimal(12, 2))
    tax_krw = Column(Decimal(12, 2))
    
    memo = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship
    order = relationship("Order", back_populates="shipment")

    def __repr__(self):
        return f"<Shipment(tracking='{self.tracking_number}', status='{self.shipment_status}')>"