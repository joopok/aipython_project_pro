from sqlalchemy import Column, Integer, String, Decimal, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db_config import Base

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(100), unique=True, nullable=False)
    platform_id = Column(Integer, ForeignKey('platforms.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    platform_order_id = Column(String(100))
    order_date = Column(DateTime, nullable=False)
    order_status = Column(Enum('pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'), default='pending')
    payment_status = Column(Enum('pending', 'paid', 'failed', 'refunded'), default='pending')
    total_amount = Column(Decimal(10, 2))
    shipping_fee = Column(Decimal(10, 2))
    tax_amount = Column(Decimal(10, 2))
    discount_amount = Column(Decimal(10, 2))
    weight_lb = Column(Decimal(10, 2))
    box_count = Column(Integer, default=1)
    shipping_method = Column(String(50))
    memo = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    platform = relationship("Platform", backref="orders")
    customer = relationship("Customer", backref="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    shipment = relationship("Shipment", uselist=False, back_populates="order")

    def __repr__(self):
        return f"<Order(order_number='{self.order_number}', status='{self.order_status}')>"


class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))
    product_name = Column(String(255), nullable=False)
    product_name_en = Column(String(255))
    sku = Column(String(100))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Decimal(10, 2))
    total_price = Column(Decimal(10, 2))
    hs_code = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", backref="order_items")

    def __repr__(self):
        return f"<OrderItem(product_name='{self.product_name}', quantity={self.quantity})>"