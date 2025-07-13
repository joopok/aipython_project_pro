from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from database.db_config import Base

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    phone2 = Column(String(20))
    email = Column(String(100))
    customs_number = Column(String(50))
    customer_type = Column(Enum('individual', 'business'), default='individual')
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state_province = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(50), default='KR')
    memo = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Customer(code='{self.customer_code}', name='{self.name}')>"