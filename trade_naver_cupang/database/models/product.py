from sqlalchemy import Column, Integer, String, Decimal, Text, Boolean, DateTime
from sqlalchemy.sql import func
from database.db_config import Base

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    name_en = Column(String(255))
    brand = Column(String(100))
    category = Column(String(100))
    hs_code = Column(String(20))
    unit_price_usd = Column(Decimal(10, 2))
    weight_lb = Column(Decimal(10, 3))
    image_url = Column(String(500))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Product(sku='{self.sku}', name='{self.name}')>"