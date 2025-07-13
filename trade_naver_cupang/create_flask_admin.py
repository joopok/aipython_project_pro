#!/usr/bin/env python
"""Flask-SQLAlchemy용 admin 사용자 생성 스크립트"""

from app import create_app, db
from app.models import User
from app.utils.auth import hash_password
from datetime import datetime

def create_admin_user():
    app = create_app()
    
    with app.app_context():
        # 기존 admin 사용자 확인
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            print("Admin 사용자가 이미 존재합니다.")
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Role: {admin.role}")
            print(f"Active: {admin.is_active}")
            
            # 비밀번호 업데이트
            admin.password = hash_password('admin123')
            admin.role = 'admin'
            admin.is_active = True
            db.session.commit()
            print("\n✅ Admin 비밀번호를 'admin123'으로 업데이트했습니다.")
        else:
            # 새 admin 사용자 생성
            admin = User(
                username='admin',
                password=hash_password('admin123'),
                email='admin@logiflow.com',
                full_name='시스템 관리자',
                role='admin',
                is_active=True,
                created_at=datetime.now()
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin 사용자를 생성했습니다.")
            print("Username: admin")
            print("Password: admin123")
        
        # 모든 사용자 목록 출력
        print("\n현재 등록된 사용자 목록:")
        users = User.query.all()
        for user in users:
            print(f"- {user.username} ({user.role}) - {user.email}")

if __name__ == '__main__':
    create_admin_user()