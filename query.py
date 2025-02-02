from typing import List, Dict, Any, Tuple, Optional, Union
import mysql.connector
from mysql.connector import Error
from db_maridb import create_connection, close_connection

class DatabaseQuery:
    @staticmethod
    def execute_query(query: str, params: tuple = None) -> Tuple[bool, str, Any]:
        """
        SQL 쿼리를 실행하고 결과를 반환합니다.
        """
        conn, info = create_connection()
        if not conn:
            return False, info["message"], None
        
        try:
            cursor = conn.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = None
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.rowcount
            
            cursor.close()
            success, message = close_connection(conn)
            return True, "쿼리 실행 성공", result
            
        except Error as e:
            return False, f"쿼리 실행 오류: {str(e)}", None
    
    @staticmethod
    def insert(table: str, data: Dict[str, Any]) -> Tuple[bool, str, Optional[int]]:
        """
        데이터를 테이블에 삽입합니다.
        
        :param table: 테이블 이름
        :param data: 삽입할 데이터 딕셔너리
        :return: (성공 여부, 메시지, 삽입된 행의 ID)
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        return DatabaseQuery.execute_query(query, tuple(data.values()))
    
    @staticmethod
    def build_where_clause(where: Dict[str, Any]) -> Tuple[str, tuple]:
        """
        WHERE 절을 생성합니다.
        
        :param where: 조건절 딕셔너리 {'column': value} 또는 {'column': {'op': '>=', 'value': 10}}
        :return: (WHERE 절 문자열, 파라미터 튜플)
        """
        conditions = []
        params = []
        
        for key, value in where.items():
            if isinstance(value, dict):
                # 연산자가 포함된 조건
                operator = value.get('op', '=')
                conditions.append(f"{key} {operator} %s")
                params.append(value.get('value'))
            elif value is None:
                # NULL 체크
                conditions.append(f"{key} IS NULL")
            elif isinstance(value, (list, tuple)):
                # IN 조건
                placeholders = ', '.join(['%s'] * len(value))
                conditions.append(f"{key} IN ({placeholders})")
                params.extend(value)
            else:
                # 기본 같음 비교
                conditions.append(f"{key} = %s")
                params.append(value)
        
        where_clause = ' AND '.join(conditions)
        return where_clause, tuple(params)

    @staticmethod
    def select(
        table: str,
        columns: List[str] = None,
        where: Dict[str, Any] = None,
        order_by: Union[str, List[str]] = None,
        limit: int = None
    ) -> Tuple[bool, str, List[Dict]]:
        """
        테이블에서 데이터를 조회합니다.
        
        :param table: 테이블 이름
        :param columns: 조회할 컬럼 리스트 (None인 경우 전체 컬럼)
        :param where: 조건절 딕셔너리
        :param order_by: 정렬 기준 컬럼
        :param limit: 조회할 최대 행 수
        :return: (성공 여부, 메시지, 조회 결과)
        """
        cols = '*' if not columns else ', '.join(columns)
        query = f"SELECT {cols} FROM {table}"
        params = None
        
        if where:
            print("WHERE 조건:", where)
            where_clause, params = DatabaseQuery.build_where_clause(where)
            print("생성된 WHERE 절:", where_clause)
            query += f" WHERE {where_clause}"
        
        if order_by:
            if isinstance(order_by, list):
                query += f" ORDER BY {', '.join(order_by)}"
            else:
                query += f" ORDER BY {order_by}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        print("최종 실행 쿼리:", query)
        
        # 실제 실행될 때의 쿼리와 파라미터 조합을 보여줌
        if params:
            # 파라미터 값에 따라 적절한 따옴표 처리
            formatted_params = []
            for param in params:
                if isinstance(param, str):
                    formatted_params.append(f"'{param}'")
                else:
                    formatted_params.append(str(param))
            debug_query = query
            for param in formatted_params:
                debug_query = debug_query.replace('%s', param, 1)
            print("실제 실행될 쿼리:", debug_query)
        
        return DatabaseQuery.execute_query(query, params)
    
    @staticmethod
    def update(table: str, data: Dict[str, Any], where: Dict[str, Any]) -> Tuple[bool, str, int]:
        """
        테이블의 데이터를 수정합니다.
        
        :param table: 테이블 이름
        :param data: 수정할 데이터 딕셔너리
        :param where: 조건절 딕셔너리
        :return: (성공 여부, 메시지, 수정된 행 수)
        """
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        where_clause = ' AND '.join([f"{k} = %s" for k in where.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        
        params = tuple(list(data.values()) + list(where.values()))
        return DatabaseQuery.execute_query(query, params)
    
    @staticmethod
    def delete(table: str, where: Dict[str, Any]) -> Tuple[bool, str, int]:
        """
        테이블에서 데이터를 삭제합니다.
        
        :param table: 테이블 이름
        :param where: 조건절 딕셔너리
        :return: (성공 여부, 메시지, 삭제된 행 수)
        """
        where_clause = ' AND '.join([f"{k} = %s" for k in where.keys()])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        
        return DatabaseQuery.execute_query(query, tuple(where.values()))

# 사용 예제
if __name__ == "__main__":
    # 데이터 삽입 예제
    insert_data = {
        "column1": "value1",
        "column2": "value2"
    }
    success, message, result = DatabaseQuery.insert("table_name", insert_data)
    print(f"Insert: {message}")
    
    # 데이터 조회 예제
    success, message, rows = DatabaseQuery.select(
        "table_name",
        columns=["column1", "column2"],
        where={"column1": "value1"}
    )
    print(f"Select: {message}")
    if success:
        for row in rows:
            print(row)
    
    # 데이터 수정 예제
    update_data = {"column2": "new_value"}
    where_condition = {"column1": "value1"}
    success, message, affected_rows = DatabaseQuery.update(
        "table_name",
        update_data,
        where_condition
    )
    print(f"Update: {message}")
    
    # 데이터 삭제 예제
    success, message, affected_rows = DatabaseQuery.delete(
        "table_name",
        {"column1": "value1"}
    )
    print(f"Delete: {message}") 