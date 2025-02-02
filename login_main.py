import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from db_maridb import create_connection, close_connection
from query import DatabaseQuery
from session import session  # 상단에 추가
import subprocess
import sys
import os

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("로그인")
        
        # 로그인 창 크기 설정
        window_width = 800
        window_height = 600
        
        # 화면 해상도 가져오기
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # 화면 중앙 좌표 계산
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 창 크기와 위치 설정
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.configure(fg_color="#f0f0f0")
        
        # 헤더
        header = ctk.CTkLabel(
            self, 
            text="Welcome to MyApp", 
            font=('Noto Sans KR', 24, 'bold'),
            text_color="#1a1a1a"
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
            text_color="#333333"
        ).grid(row=0, column=0, pady=5, sticky="e")
        self.username_entry = ctk.CTkEntry(
            input_frame,
            font=('Noto Sans KR', 12),
            placeholder_text="아이디를 입력하세요",
            placeholder_text_color="#666666",
            text_color="#1a1a1a",
            fg_color="white",
            border_color="#999999"
        )
        self.username_entry.grid(row=0, column=1, padx=5, sticky="ew")
        
        # 초기 포커스 및 영문 입력 모드 설정
        self.username_entry.focus()
        self.after(100, lambda: self.event_generate('<<SetEnglishMode>>'))
        self.bind('<<SetEnglishMode>>', self._set_english_mode)
        
        # 비밀번호 입력
        ctk.CTkLabel(
            input_frame,
            text="비밀번호",
            font=('Noto Sans KR', 12),
            text_color="#333333"
        ).grid(row=1, column=0, pady=(15, 5), sticky="e")
        self.password_entry = ctk.CTkEntry(
            input_frame,
            font=('Noto Sans KR', 12),
            show="●",
            placeholder_text="비밀번호를 입력하세요",
            placeholder_text_color="#666666",
            text_color="#1a1a1a",
            fg_color="white",
            border_color="#999999"
        )
        self.password_entry.grid(row=1, column=1, padx=5, sticky="ew")
        
        # 엔터키 이벤트 바인딩
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self._login())
        
        # 그라데이션 캔버스
        gradient_canvas = tk.Canvas(input_frame, width=135, height=135, highlightthickness=0)
        gradient_canvas.grid(row=1, column=2, padx=5, pady=(15, 5))
        self._create_gradient(gradient_canvas, "#0000FF", "#FFFFFF")
        
        # 로그인 버튼
        login_button = ctk.CTkButton(
            input_frame,
            text="로그인",
            command=self._login,
            font=('Noto Sans KR', 12),
            fg_color="transparent",
            text_color="#0e6efd",
            height=140
        )
        login_button.place(in_=gradient_canvas, relx=0.5, rely=0.5, anchor="center")
        
        # 데이터베이스 연결 테스트 버튼
        test_db_button = ctk.CTkButton(
            input_frame,
            text="DB 연결 테스트",
            command=self._test_db_connection,
            font=('Noto Sans KR', 12),
            fg_color="#0e6efd",
            text_color="white",
            height=35,
            width=120
        )
        test_db_button.grid(row=2, column=1, pady=(20, 0), sticky="e")
        
        # 열 크기 조정
        input_frame.grid_columnconfigure(1, weight=1)
    
    def _create_gradient(self, canvas, color1, color2):
        """그라데이션 효과 생성"""
        width = canvas.winfo_reqwidth()
        height = canvas.winfo_reqheight()
        limit = width  # 그라데이션의 범위
        (r1, g1, b1) = self.winfo_rgb(color1)
        (r2, g2, b2) = self.winfo_rgb(color2)
        r_ratio = float(r2 - r1) / limit
        g_ratio = float(g2 - g1) / limit
        b_ratio = float(b2 - b1) / limit

        for i in range(limit):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = f'#{nr:04x}{ng:04x}{nb:04x}'
            canvas.create_line(i, 0, i, height, fill=color, width=1)
    
    def _test_db_connection(self):
        """데이터베이스 연결을 테스트합니다."""
        try:
            conn, info = create_connection()
            if conn:
                messagebox.showinfo(
                    "연결 성공",
                    info["message"],
                    parent=self
                )
                success, close_message = close_connection(conn)
                if not success:
                    messagebox.showwarning(
                        "경고",
                        f"연결 종료 중 문제 발생:\n{close_message}",
                        parent=self
                    )
            else:
                messagebox.showerror(
                    "연결 실패",
                    info["message"],
                    parent=self
                )
        except Exception as e:
            messagebox.showerror(
                "오류",
                f"예기치 않은 오류가 발생했습니다:\n{str(e)}",
                parent=self
            )
    
    def _login(self):
        """로그인 처리"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("오류", "아이디와 비밀번호를 모두 입력해주세요.....", parent=self)
            return
        
        try:
            success, message, rows = DatabaseQuery.select(
                table="user",
                columns=["user_id", "user_pwd", "user_name"],
                where={
                    "user_id": username,
                    "user_pwd": password,
                }
            )
            
            if not success:
                messagebox.showerror("오류", f"데이터베이스 오류: {message}", parent=self)
                return
            
            if not rows:
                messagebox.showerror(
                    "로그인 실패",
                    "아이디 또는 비밀번호가 올바르지 않습니다.",
                    parent=self
                )
                return
            
            # 로그인 성공
            user_info = rows[0]
            
            # 세션 시작
            session.start_session(user_info)
            session.save_session_to_file()  # 세션 정보 저장
            print(f"세션 정보: {session.get_session_id()}")
            print(f"사용자 ID: {session.get_user_id()}")
            print(f"사용자 이름: {session.get_user_name()}")
            print(f"로그인 시간: {session._session_data['login_time']}")
            print(f"사용자 레벨: {session._session_data['user_level']}")
            print(f"인증 상태: {session.is_authenticated()}")
            
            messagebox.showinfo(
                "로그인 성공",
                f"환영합니다, {session.get_user_name()}님!",
                parent=self
            )
            
            # 로그인 창 닫기
            self.destroy()
            
            # start.py 실행
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                start_path = os.path.join(current_dir, 'start.py')
                
                # Python 실행 경로 가져오기
                python_executable = sys.executable
                
                # start.py 실행
                subprocess.Popen([python_executable, start_path])
            except Exception as e:
                messagebox.showerror(
                    "오류",
                    f"메인 프로그램 실행 중 오류가 발생했습니다:\n{str(e)}"
                )
                
        except Exception as e:
            messagebox.showerror(
                "오류",
                f"로그인 처리 중 오류가 발생했습니다:\n{str(e)}",
                parent=self
            )

    def _set_english_mode(self, event=None):
        """입력 모드를 영문으로 설정"""
        try:
            if sys.platform == 'darwin':  # macOS
                os.system('defaults write com.apple.HIToolbox AppleCurrentKeyboardLayoutInputSourceID com.apple.keylayout.ABC')
            elif sys.platform == 'win32':  # Windows
                try:
                    import win32api
                    import win32con
                    win32api.LoadKeyboardLayout('00000409', win32con.KLF_ACTIVATE)
                except ImportError:
                    print("Windows 환경에서 win32api를 불러올 수 없습니다.")
            else:
                print(f"현재 OS({sys.platform})에서는 자동 영문 전환을 지원하지 않습니다.")
        except Exception as e:
            print(f"키보드 레이아웃 변경 중 오류 발생: {e}")

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop() 