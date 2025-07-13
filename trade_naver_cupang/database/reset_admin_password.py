#!/usr/bin/env python3
"""
admin 계정 비밀번호를 admin123으로 재설정하는 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent.parent))

from database.db_config import SessionLocal
from database.models.user import User
from app.utils.auth import hash_password

def reset_admin_password():
    """admin 계정의 비밀번호를 admin123으로 재설정합니다."""
    db = SessionLocal()
    
    try:
        # admin 사용자 조회
        admin_user = db.query(User).filter(User.username == 'admin').first()
        
        if not admin_user:
            print("❌ admin 계정이 존재하지 않습니다.")
            return
        
        # 비밀번호를 admin123으로 변경
        admin_user.password = hash_password('admin123')
        db.commit()
        
        print("✅ admin 계정의 비밀번호를 'admin123'으로 변경했습니다.")
        print(f"   - Username: {admin_user.username}")
        print(f"   - Email: {admin_user.email}")
        print("   - Password: admin123")
        print("\n이제 admin/admin123으로 로그인할 수 있습니다.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 오류 발생: {str(e)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()