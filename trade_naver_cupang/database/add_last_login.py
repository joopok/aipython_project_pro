#!/usr/bin/env python
"""users 테이블에 last_login 컬럼 추가"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_config import engine
from sqlalchemy import text

def add_last_login_column():
    with engine.connect() as conn:
        try:
            # last_login 컬럼 추가
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS last_login DATETIME NULL
            """))
            conn.commit()
            print("✅ last_login 컬럼을 추가했습니다.")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("last_login 컬럼이 이미 존재합니다.")
            else:
                print(f"오류 발생: {e}")

if __name__ == '__main__':
    add_last_login_column()