from sqlalchemy import Column, Integer, String, Date, Decimal, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db_config import Base

class Settlement(Base):
    __tablename__ = 'settlements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    settlement_number = Column(String(50), unique=True, nullable=False)
    settlement_date = Column(Date, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_sales_usd = Column(Decimal(12, 2))
    total_cost_usd = Column(Decimal(12, 2))
    total_shipping_krw = Column(Decimal(12, 2))
    total_tax_krw = Column(Decimal(12, 2))
    total_fees_krw = Column(Decimal(12, 2))
    exchange_rate = Column(Decimal(10, 2))
    net_amount_krw = Column(Decimal(12, 2))
    settlement_status = Column(Enum('pending', 'processing', 'completed', 'cancelled'), default='pending')
    payment_date = Column(Date)
    memo = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship
    details = relationship("SettlementDetail", back_populates="settlement", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Settlement(number='{self.settlement_number}', date='{self.settlement_date}')>"


class SettlementDetail(Base):
    __tablename__ = 'settlement_details'

    id = Column(Integer, primary_key=True, autoincrement=True)
    settlement_id = Column(Integer, ForeignKey('settlements.id', ondelete='CASCADE'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    sales_amount_usd = Column(Decimal(10, 2))
    cost_amount_usd = Column(Decimal(10, 2))
    shipping_fee_krw = Column(Decimal(10, 2))
    customer_tax_krw = Column(Decimal(10, 2))
    settlement_tax_krw = Column(Decimal(10, 2))
    customs_fee_krw = Column(Decimal(10, 2))
    net_amount_krw = Column(Decimal(10, 2))
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    settlement = relationship("Settlement", back_populates="details")
    order = relationship("Order", backref="settlement_details")

    def __repr__(self):
        return f"<SettlementDetail(settlement_id={self.settlement_id}, order_id={self.order_id})>"