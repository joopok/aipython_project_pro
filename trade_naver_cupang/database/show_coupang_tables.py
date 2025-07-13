#!/usr/bin/env python3
"""
쿠팡 테이블 정보 조회 스크립트
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

def show_coupang_tables():
    """쿠팡 관련 테이블 정보 출력"""
    # MariaDB 연결 정보
    host = os.getenv('DB_HOST', '192.168.0.109')
    port = int(os.getenv('DB_PORT', '3306'))
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '~Asy10131227')
    db_name = os.getenv('DB_NAME', 'trade_naver_cupang')
    
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
        
        cursor = connection.cursor()
        
        print('=== 쿠팡 관련 테이블 정보 ===\n')
        
        tables = ['coupang_order_sheets', 'coupang_order_items', 'coupang_order_sync']
        
        for table_name in tables:
            print(f'\n📋 테이블명: {table_name}')
            print('-' * 100)
            
            # 테이블 구조 조회
            cursor.execute(f'DESCRIBE {table_name}')
            columns = cursor.fetchall()
            
            print(f'총 컬럼 수: {len(columns)}개\n')
            print(f"{'컬럼명':<30} {'타입':<25} {'Null':<6} {'Key':<5} {'기본값':<15}")
            print('=' * 100)
            
            for col in columns:
                col_name = col[0]
                col_type = col[1]
                col_null = col[2]
                col_key = col[3]
                col_default = col[4] if col[4] is not None else ''
                
                print(f'{col_name:<30} {col_type:<25} {col_null:<6} {col_key:<5} {str(col_default):<15}')
            
            # 인덱스 정보
            cursor.execute(f'SHOW INDEX FROM {table_name}')
            indexes = cursor.fetchall()
            
            if indexes:
                print(f'\n인덱스 정보:')
                index_dict = {}
                for idx in indexes:
                    index_name = idx[2]
                    column_name = idx[4]
                    if index_name not in index_dict:
                        index_dict[index_name] = []
                    index_dict[index_name].append(column_name)
                
                for idx_name, cols in index_dict.items():
                    print(f'  - {idx_name}: {", ".join(cols)}')
            
            # 레코드 수 조회
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
            print(f'\n현재 레코드 수: {count}건')
            
            # 외래키 정보
            cursor.execute(f"""
                SELECT 
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM 
                    INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE 
                    TABLE_SCHEMA = '{db_name}'
                    AND TABLE_NAME = '{table_name}'
                    AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            foreign_keys = cursor.fetchall()
            
            if foreign_keys:
                print(f'\n외래키 정보:')
                for fk in foreign_keys:
                    print(f'  - {fk[0]} -> {fk[1]}.{fk[2]}')
            
            print('-' * 100)
        
        # 전체 통계
        print('\n📊 전체 통계:')
        for table_name in tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
            print(f'  - {table_name}: {count}건')
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    show_coupang_tables()