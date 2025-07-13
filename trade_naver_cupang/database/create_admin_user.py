#!/usr/bin/env python3
"""
관리자 계정 생성 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent.parent))

from database.db_config import SessionLocal, engine
from database.models.user import User
from app.utils.auth import hash_password
import getpass

def create_admin_user():
    """관리자 계정을 생성합니다."""
    print("=== 관리자 계정 생성 ===")
    
    # 사용자 입력 받기
    username = input("관리자 아이디: ").strip()
    if not username:
        print("❌ 아이디는 필수 입력 항목입니다.")
        return
        
    email = input("이메일 주소: ").strip()
    if not email:
        print("❌ 이메일은 필수 입력 항목입니다.")
        return
        
    full_name = input("이름: ").strip()
    if not full_name:
        print("❌ 이름은 필수 입력 항목입니다.")
        return
    
    # 비밀번호 입력 (보안을 위해 getpass 사용)
    while True:
        password = getpass.getpass("비밀번호: ")
        password_confirm = getpass.getpass("비밀번호 확인: ")
        
        if password != password_confirm:
            print("❌ 비밀번호가 일치하지 않습니다. 다시 입력해주세요.")
            continue
            
        if len(password) < 6:
            print("❌ 비밀번호는 최소 6자 이상이어야 합니다.")
            continue
            
        break
    
    # 데이터베이스 세션 생성
    db = SessionLocal()
    
    try:
        # 기존 사용자 확인
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            print(f"❌ 이미 존재하는 사용자입니다. (username: {existing_user.username}, email: {existing_user.email})")
            
            # 비밀번호 변경 옵션
            change = input("비밀번호를 변경하시겠습니까? (y/n): ").lower()
            if change == 'y':
                existing_user.password = hash_password(password)
                db.commit()
                print("✅ 비밀번호가 변경되었습니다.")
            return
        
        # 새 사용자 생성
        new_user = User(
            username=username,
            password=hash_password(password),
            email=email,
            full_name=full_name,
            role='admin',
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        
        print("✅ 관리자 계정이 생성되었습니다!")
        print(f"   - 아이디: {username}")
        print(f"   - 이메일: {email}")
        print(f"   - 이름: {full_name}")
        print(f"   - 권한: admin")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 오류 발생: {str(e)}")
        
    finally:
        db.close()

# 기본 관리자 계정 생성 기능 제거 (보안상 하드코딩 제거)

if __name__ == "__main__":
    create_admin_user()