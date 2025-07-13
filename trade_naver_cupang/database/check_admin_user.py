#!/usr/bin/env python3
"""
admin 계정 확인 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent.parent))

from database.db_config import SessionLocal
from database.models.user import User
from app.utils.auth import verify_password

def check_admin_user():
    """admin 계정을 확인합니다."""
    db = SessionLocal()
    
    try:
        # admin 사용자 조회
        admin_user = db.query(User).filter(User.username == 'admin').first()
        
        if not admin_user:
            print("❌ admin 계정이 존재하지 않습니다.")
            print("💡 database/create_admin_user.py를 실행하여 admin 계정을 생성하세요.")
            return
        
        print("✅ admin 계정이 존재합니다.")
        print(f"   - ID: {admin_user.id}")
        print(f"   - Username: {admin_user.username}")
        print(f"   - Email: {admin_user.email}")
        print(f"   - Full Name: {admin_user.full_name}")
        print(f"   - Role: {admin_user.role}")
        print(f"   - Is Active: {admin_user.is_active}")
        print(f"   - Created At: {admin_user.created_at}")
        
        # admin123 비밀번호 테스트
        if verify_password('admin123', admin_user.password):
            print("\n✅ 비밀번호 'admin123'이 맞습니다.")
        else:
            print("\n❌ 비밀번호 'admin123'이 맞지 않습니다.")
            print("💡 올바른 비밀번호를 사용하거나 create_admin_user.py로 비밀번호를 재설정하세요.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_admin_user()