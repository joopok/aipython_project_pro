from typing import Dict

# 색상 테마
COLORS: Dict[str, str] = {
    'primary': '#2D3250',    # 진한 남색
    'secondary': '#424769',  # 중간 톤의 남색
    'accent': '#676F9D',     # 연한 남색
    'background': '#FFFFFF', # 흰색
    'text': '#2D3250',       # 진한 남색
    'success': '#4CAF50',    # 초록색
    'warning': '#FF9800',    # 주황색
    'error': '#F44336'       # 빨간색
}

# 트리뷰 설정
TREE_COLUMNS = [
    ("시작일", 100),
    ("종료일", 100),
    ("진행률", 70),
    ("담당자", 80),
    ("우선순위", 80),
    ("상태", 80),
    ("리소스", 150)
]

# 메뉴 버튼 설정
MENU_BUTTONS = [
    ("새 프로젝트", "➕", "new_project"),
    ("저장", "💾", "save_project"),
    ("작업 추가", "📝", "add_task"),
    ("리소스 관리", "👥", "manage_resources"),
    ("보고서", "📊", "generate_report"),
    ("설정", "⚙️", "open_settings"),
    ("필터", "🔍", "show_filters"),
    ("타임라인", "📅", "toggle_timeline"),
    ("새로고침", "🔄", "refresh")
]

# 윈도우 설정
WINDOW_MIN_SIZE = (900, 600)
WINDOW_SIZE_RATIO = 0.85

# 기존 코드에 추가
GANTT_COLORS = {
    'header_bg': '#E3F2FD',
    'header_border': '#90CAF9',
    'weekend_bg': '#F5F5F5',
    'grid': '#E0E0E0',
    'bar_fill': {
        'normal': '#4CAF50',
        'delayed': '#F44336',
        'completed': '#2196F3',
        'milestone': '#FFC107'
    },
    'bar_border': '#388E3C',  # 작업 바 테두리 색상 추가
    'progress': '#81C784',
    'dependency': '#90A4AE',
    'today': '#FF5252'  # 오늘 날짜 표시 색상 추가
}

# 작업 상태 설정
TASK_STATUS = [
    "대기중",
    "진행중",
    "완료",
    "지연",
    "보류",
    "취소"
]

# 우선순위 설정
PRIORITY_LEVELS = [
    ("매우 높음", "VERY_HIGH"),
    ("높음", "HIGH"),
    ("보통", "MEDIUM"),
    ("낮음", "LOW"),
    ("매우 낮음", "VERY_LOW")
]

# 컨텍스트 메뉴 항목
CONTEXT_MENU_ITEMS = [
    ("작업 추가", "add_task"),
    ("하위작업 추가", "add_subtask"),
    ("작업 수정", "edit_task"),
    ("작업 삭제", "delete_task"),
    ("---", None),  # 구분선
    ("위로 이동", "move_task_up"),
    ("아래로 이동", "move_task_down"),
    ("---", None),
    ("모두 펼치기", "expand_all"),
    ("모두 접기", "collapse_all"),
    ("---", None),
    ("CSV 내보내기", "export_to_csv"),
    ("MS Project 내보내기", "export_to_mpp")
] 