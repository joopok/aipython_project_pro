from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db_config import Base

class Inventory(Base):
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    warehouse_location = Column(String(50), default='US')
    quantity_on_hand = Column(Integer, default=0)
    quantity_reserved = Column(Integer, default=0)
    reorder_level = Column(Integer, default=0)
    last_restock_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship
    product = relationship("Product", backref="inventory_records")

    def __repr__(self):
        return f"<Inventory(product_id={self.product_id}, on_hand={self.quantity_on_hand})>"


class InventoryTransaction(Base):
    __tablename__ = 'inventory_transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    transaction_type = Column(Enum('in', 'out', 'adjustment'), nullable=False)
    quantity = Column(Integer, nullable=False)
    reference_type = Column(String(50))
    reference_id = Column(Integer)
    transaction_date = Column(DateTime, server_default=func.now())
    reason = Column(String(255))
    performed_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    product = relationship("Product", backref="transactions")
    user = relationship("User", backref="inventory_actions")

    def __repr__(self):
        return f"<InventoryTransaction(type='{self.transaction_type}', qty={self.quantity})>"