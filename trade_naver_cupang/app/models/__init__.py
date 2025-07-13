from app import db
from datetime import datetime
from app.models.base import BaseModelMixin
from app.models.user import User


class MarketplaceProduct(BaseModelMixin, db.Model):
    __tablename__ = 'marketplace_products'
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(20), nullable=False)  # 'naver' or 'coupang'
    product_id = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    original_price = db.Column(db.Integer)
    discount_rate = db.Column(db.Integer)
    rating = db.Column(db.Float)
    review_count = db.Column(db.Integer)
    seller = db.Column(db.String(100))
    url = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    


class SearchHistory(BaseModelMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(20), nullable=False)
    result_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
