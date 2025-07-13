from datetime import datetime

class BaseModelMixin:
    """모든 모델의 공통 기능을 제공하는 Mixin 클래스"""
    
    def to_dict(self):
        """모델 인스턴스를 딕셔너리로 변환"""
        result = {}
        
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            # datetime 객체 처리
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
                
        return result
    
    def update_from_dict(self, data):
        """딕셔너리 데이터로 모델 업데이트"""
        for key, value in data.items():
            if hasattr(self, key) and key != 'id':  # id는 변경하지 않음
                setattr(self, key, value)