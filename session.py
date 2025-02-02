from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import json
from pathlib import Path

class SessionManager:
    _instance = None
    _SESSION_FILE = Path('session.json')
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """세션 데이터 초기화"""
        self._session_data: Dict[str, Any] = {
            'session_id': None,
            'user_id': None,
            'user_name': None,
            'login_time': None,
            'is_authenticated': False,
            'user_level': None,
            'last_access': None,
            'additional_info': {}
        }
    
    def start_session(self, user_info: Dict[str, Any]) -> None:
        """
        새로운 세션을 시작합니다.
        
        :param user_info: 데이터베이스에서 가져온 사용자 정보
        """
        self._session_data.update({
            'session_id': str(uuid.uuid4()),
            'user_id': user_info.get('user_id'),
            'user_name': user_info.get('user_name'),
            'login_time': datetime.now(),
            'is_authenticated': True,
            'user_level': user_info.get('user_level', 1),
            'last_access': datetime.now(),
            'additional_info': user_info
        })
    
    def end_session(self) -> None:
        """현재 세션을 종료합니다."""
        self._initialize()
    
    def is_authenticated(self) -> bool:
        """사용자가 인증되었는지 확인합니다."""
        return self._session_data['is_authenticated']
    
    def get_user_id(self) -> Optional[str]:
        """현재 로그인한 사용자의 ID를 반환합니다."""
        return self._session_data['user_id']
    
    def get_user_name(self) -> Optional[str]:
        """현재 로그인한 사용자의 이름을 반환합니다."""
        return self._session_data['user_name']
    
    def get_user_level(self) -> Optional[int]:
        """현재 로그인한 사용자의 레벨을 반환합니다."""
        return self._session_data['user_level']
    
    def get_login_time(self) -> Optional[datetime]:
        """현재 세션의 로그인 시간을 반환합니다."""
        return self._session_data['login_time']
    
    def update_last_access(self) -> None:
        """마지막 접근 시간을 현재 시간으로 업데이트합니다."""
        self._session_data['last_access'] = datetime.now()
    
    def get_session_data(self) -> Dict[str, Any]:
        """전체 세션 데이터를 반환합니다."""
        return self._session_data.copy()
    
    def set_additional_info(self, key: str, value: Any) -> None:
        """
        추가 정보를 세션에 저장합니다.
        
        :param key: 저장할 데이터의 키
        :param value: 저장할 데이터의 값
        """
        self._session_data['additional_info'][key] = value
    
    def get_additional_info(self, key: str, default: Any = None) -> Any:
        """
        세션에서 추가 정보를 가져옵니다.
        
        :param key: 가져올 데이터의 키
        :param default: 키가 없을 경우 반환할 기본값
        :return: 저장된 값 또는 기본값
        """
        return self._session_data['additional_info'].get(key, default)
    
    def get_session_id(self) -> Optional[str]:
        """현재 세션의 ID를 반환합니다."""
        return self._session_data['session_id']

    def save_session_to_file(self) -> None:
        """세션 데이터를 파일에 저장합니다."""
        session_data = self.get_session_data()
        # datetime 객체를 문자열로 변환
        if session_data['login_time']:
            session_data['login_time'] = session_data['login_time'].isoformat()
        if session_data['last_access']:
            session_data['last_access'] = session_data['last_access'].isoformat()
        
        self._SESSION_FILE.write_text(
            json.dumps(session_data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

    def load_session_from_file(self) -> bool:
        """파일에서 세션 데이터를 불러옵니다."""
        try:
            session_data = json.loads(self._SESSION_FILE.read_text(encoding='utf-8'))
            # 문자열을 datetime 객체로 변환
            if session_data['login_time']:
                session_data['login_time'] = datetime.fromisoformat(session_data['login_time'])
            if session_data['last_access']:
                session_data['last_access'] = datetime.fromisoformat(session_data['last_access'])
            
            self._session_data = session_data
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False

# 전역 세션 매니저 인스턴스
session = SessionManager()

# 사용 예제
#if __name__ == "__main__":
    # 세션 시작 예제
    #user_data = {
    #    'user_id': 'test_user',
    #    'user_name': '홍길동',
    #    'user_level': 1,
    #    'department': '개발팀'
    #}
    
    # 세션 시작
    #session.start_session(user_data)
    
    # 세션 정보 확인
    #print(f"인증 상태: {session.is_authenticated()}")
    #print(f"사용자 ID: {session.get_user_id()}")
    #print(f"사용자 이름: {session.get_user_name()}")
    #print(f"로그인 시간: {session.get_login_time()}")
    
    # 추가 정보 저장
    #session.set_additional_info('last_project', 'Project A')
    
    # 추가 정보 확인
    #print(f"마지막 프로젝트: {session.get_additional_info('last_project')}")
    
    # 전체 세션 데이터 확인
    #print("\n전체 세션 데이터:")
    #print(session.get_session_data())
    
    # 세션 종료
    #session.end_session() 