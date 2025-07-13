#!/usr/bin/env python3
"""
데이터베이스 초기화 스크립트
- MariaDB에 데이터베이스 생성
- 테이블 스키마 적용
"""

import os
import sys
import pymysql
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def create_database():
    """데이터베이스 생성"""
    # MariaDB 연결 정보
    host = os.getenv('DB_HOST', '192.168.0.109')
    port = int(os.getenv('DB_PORT', '3306'))
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '~Asy10131227')
    db_name = os.getenv('DB_NAME', 'trade_naver_cupang')
    
    try:
        # MariaDB 연결 (데이터베이스 없이)
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 데이터베이스 생성
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Database '{db_name}' created successfully!")
            
        connection.close()
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False
    
    return True

def execute_schema():
    """스키마 SQL 실행"""
    # MariaDB 연결 정보
    host = os.getenv('DB_HOST', '192.168.0.109')
    port = int(os.getenv('DB_PORT', '3306'))
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '~Asy10131227')
    db_name = os.getenv('DB_NAME', 'trade_naver_cupang')
    
    # schema.sql 파일 경로
    schema_path = Path(__file__).parent / 'schema.sql'
    
    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        return False
    
    try:
        # MariaDB 연결
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # schema.sql 파일 읽기
            with open(schema_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            # SQL 문장을 세미콜론으로 분리하여 실행
            sql_commands = sql_script.split(';')
            
            for command in sql_commands:
                command = command.strip()
                if command and not command.startswith('--'):
                    try:
                        cursor.execute(command)
                    except pymysql.err.Warning as w:
                        # 경고는 무시 (테이블이 이미 존재하는 경우 등)
                        pass
                    except Exception as e:
                        print(f"⚠️  Warning executing command: {e}")
            
            connection.commit()
            print("✅ Schema applied successfully!")
            
            # 생성된 테이블 확인
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"\n📊 Created tables ({len(tables)}):")
            for table in tables:
                print(f"   - {table[0]}")
                
        connection.close()
        
    except Exception as e:
        print(f"❌ Error executing schema: {e}")
        return False
    
    return True

def main():
    """메인 함수"""
    print("🚀 Starting database initialization...")
    print("-" * 50)
    
    # 1. 데이터베이스 생성
    if not create_database():
        print("Failed to create database. Exiting...")
        sys.exit(1)
    
    # 2. 스키마 적용
    if not execute_schema():
        print("Failed to execute schema. Exiting...")
        sys.exit(1)
    
    print("-" * 50)
    print("✨ Database initialization completed successfully!")
    print("\nNext steps:")
    print("1. Update .env file with your MariaDB credentials")
    print("2. Run 'flask run' to start the application")

if __name__ == "__main__":
    main()