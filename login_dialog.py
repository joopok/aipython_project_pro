import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

class LoginDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("로그인")
        
        # 항상 최상위에 표시
        self.attributes('-topmost', True)
        
        # 화면 해상도 가져오기
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print(screen_width, screen_height)
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        
        # 로그인 창 크기 설정
        window_width = 400
        window_height = 400
        
        # 화면 중앙 좌표 계산
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        # 창 크기와 위치 설정
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.resizable(False, False)  # 창 크기 조절 불가능하게 설정
        self.configure(fg_color="#f0f0f0")
        
        # 모달 설정
        self.transient(parent)
        self.grab_set()
        self.focus_force()  # 강제로 포커스 설정
        
        # 헤더
        header = ctk.CTkLabel(
            self, 
            text="프로젝트 Pro 로그인", 
            font=('Noto Sans KR', 24, 'bold'),
            text_color="#1a1a1a",  # 진한 검정
            fg_color="transparent"
        )
        header.pack(pady=30)
        
        # 입력 필드 프레임
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill=tk.BOTH, padx=40, pady=20)
        
        # 사용자 ID 입력
        ctk.CTkLabel(
            input_frame,
            text="사용자 ID",
            font=('Noto Sans KR', 12),
            text_color="#333333",  # 중간 톤의 검정
            fg_color="transparent"
        ).pack(pady=5)
        self.username_entry = ctk.CTkEntry(
            input_frame,
            font=('Noto Sans KR', 12),
            placeholder_text="아이디를 입력하세요",
            placeholder_text_color="#666666",  # 연한 검정
            text_color="#1a1a1a",  # 진한 검정
            fg_color="white",
            border_color="#999999"  # 테두리 색상
        )
        self.username_entry.pack(fill=tk.X)
        
        # 비밀번호 입력
        ctk.CTkLabel(
            input_frame,
            text="비밀번호",
            font=('Noto Sans KR', 12),
            text_color="#333333",  # 중간 톤의 검정
            fg_color="transparent"
        ).pack(pady=(15, 5))
        self.password_entry = ctk.CTkEntry(
            input_frame,
            font=('Noto Sans KR', 12),
            show="●",
            placeholder_text="비밀번호를 입력하세요",
            placeholder_text_color="#666666",  # 연한 검정
            text_color="#1a1a1a",  # 진한 검정
            fg_color="white",
            border_color="#999999"  # 테두리 색상
        )
        self.password_entry.pack(fill=tk.X)
        
        # 로그인 버튼
        login_button = ctk.CTkButton(
            self,
            text="로그인",
            command=self._login,
            font=('Noto Sans KR', 14),
            fg_color="#2b2b2b",  # 진한 검정 버튼
            text_color="white",
            hover_color="#1a1a1a",  # 더 진한 검정으로 호버 효과
            height=45
        )
        login_button.pack(pady=30, padx=40, fill=tk.X)
    
    def _login(self):
        """로그인 처리"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # 테스트 계정 검증
        TEST_ID = "test"
        TEST_PASSWORD = "test1234"
        
        if username and password:
            if username == TEST_ID and password == TEST_PASSWORD:
                self.result = True  # 로그인 성공 상태 저장
                self.destroy()
            else:
                messagebox.showerror("오류", "아이디 또는 비밀번호가 올바르지 않습니다.")
        else:
            messagebox.showerror("오류", "아이디와 비밀번호를 모두 입력해주세요.") 