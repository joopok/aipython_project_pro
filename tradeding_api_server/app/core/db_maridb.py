import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def create_connection():
    """MariaDB 데이터베이스에 연결을 생성합니다."""
    connection = None
    db_info = None
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            port=os.getenv('DB_PORT', '3306'),
            database=os.getenv('DB_NAME', 'pms7')
        )
        if connection.is_connected():
            db_info = connection.get_server_info()
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()[0]
            cursor.close()
            return connection, {
                "status": "success",
                "message": f"MariaDB 연결 성공 (버전: {db_info})\n데이터베이스: {db_name}",
                "version": db_info,
                "database": db_name
            }
    except Error as e:
        return None, {
            "status": "error",
            "message": f"데이터베이스 연결 오류:\n{str(e)}"
        }

def close_connection(connection):
    """데이터베이스 연결을 닫습니다."""
    try:
        if connection and connection.is_connected():
            connection.close()
            return True, "데이터베이스 연결이 정상적으로 종료되었습니다."
    except Error as e:
        return False, f"연결 종료 중 오류 발생: {str(e)}"
    return False, "연결이 이미 종료되었습니다."

def execute_query(connection, query, params=None):
    """쿼리를 실행하고 결과를 반환합니다."""
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query.strip().upper().startswith(('SELECT', 'SHOW')):
            result = cursor.fetchall()
            return True, result
        else:
            connection.commit()
            return True, {"affected_rows": cursor.rowcount}
    except Error as e:
        return False, f"쿼리 실행 중 오류 발생: {str(e)}"
    finally:
        if cursor:
            cursor.close()

# 예제 사용
if __name__ == "__main__":
    conn, info = create_connection()
    if conn:
        print(info["message"])
        success, message = close_connection(conn)
        print(message)
