import mysql.connector
from mysql.connector import Error

def create_connection():
    print("create_connection 호출")
    """MariaDB 데이터베이스에 연결을 생성합니다."""
    connection = None
    db_info = None
    try:
        connection = mysql.connector.connect(
            host='192.168.0.109',
            user='root',
            password='~Asy10131227',
            port='3307',
            database='pms7'
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

# 예제 사용
if __name__ == "__main__":
    conn, info = create_connection()
    if conn:
        print(info["message"])
        success, message = close_connection(conn)
        print(message)
