import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from datetime import datetime
from tkcalendar import DateEntry
from constants import COLORS, PRIORITY_LEVELS, TASK_STATUS

class TaskDialog(ctk.CTkToplevel):
    def __init__(self, parent, name=None, values=None):
        super().__init__(parent)
        self.title("작업 추가/수정")
        self.geometry("500x700")
        
        # 팝업 창을 화면 중앙에 위치시키기
        self.update_idletasks()  # 창 크기 업데이트
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
        
        # 모달 설정
        self.transient(parent)
        self.grab_set()
        
        # 작업명
        ctk.CTkLabel(self, text="작업명:", font=('Noto Sans KR', 12)).pack(pady=5)
        self.task_name = ctk.CTkEntry(self, font=('Noto Sans KR', 12))
        self.task_name.pack(fill=tk.X, padx=20)
        
        # 날짜 선택
        date_frame = ctk.CTkFrame(self)
        date_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ctk.CTkLabel(date_frame, text="시작일:", font=('Noto Sans KR', 12)).pack(side=tk.LEFT, padx=5)
        self.start_date = DateEntry(date_frame, font=('Noto Sans KR', 12), date_pattern="yyyy-mm-dd")
        self.start_date.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkLabel(date_frame, text="종료일:", font=('Noto Sans KR', 12)).pack(side=tk.LEFT, padx=5)
        self.end_date = DateEntry(date_frame, font=('Noto Sans KR', 12), date_pattern="yyyy-mm-dd")
        self.end_date.pack(side=tk.LEFT, padx=5)
        
        # 진행률
        ctk.CTkLabel(self, text="진행률:", font=('Noto Sans KR', 12)).pack(pady=5)
        self.progress = ctk.CTkSlider(self, from_=0, to=100, number_of_steps=100)
        self.progress.pack(fill=tk.X, padx=20)
        self.progress_label = ctk.CTkLabel(self, text="0%", font=('Noto Sans KR', 12))
        self.progress_label.pack()
        self.progress.bind("<Motion>", self._update_progress_label)
        
        # 담당자
        ctk.CTkLabel(self, text="담당자:", font=('Noto Sans KR', 12)).pack(pady=5)
        self.manager = ctk.CTkEntry(self, font=('Noto Sans KR', 12))
        self.manager.pack(fill=tk.X, padx=20)
        
        # 우선순위
        ctk.CTkLabel(self, text="우선순위:", font=('Noto Sans KR', 12)).pack(pady=5)
        self.priority = ttk.Combobox(self, values=[level[0] for level in PRIORITY_LEVELS], font=('Noto Sans KR', 12))
        self.priority.pack(fill=tk.X, padx=20)
        
        # 상태
        ctk.CTkLabel(self, text="상태:", font=('Noto Sans KR', 12)).pack(pady=5)
        self.status = ttk.Combobox(self, values=TASK_STATUS, font=('Noto Sans KR', 12))
        self.status.pack(fill=tk.X, padx=20)
        
        # 리소스
        ctk.CTkLabel(self, text="리소스:", font=('Noto Sans KR', 12)).pack(pady=5)
        self.resources = ctk.CTkEntry(self, font=('Noto Sans KR', 12))
        self.resources.pack(fill=tk.X, padx=20)
        
        # 저장/취소 버튼
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        save_button = ctk.CTkButton(button_frame, text="저장", command=self._save, font=('Noto Sans KR', 12))
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ctk.CTkButton(button_frame, text="취소", command=self.destroy, font=('Noto Sans KR', 12))
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # 기존 값 설정
        if name and values:
            self.task_name.insert(0, name)
            self.start_date.set_date(datetime.strptime(values[0], "%Y-%m-%d"))
            self.end_date.set_date(datetime.strptime(values[1], "%Y-%m-%d"))
            self.progress.set(float(values[2].replace("%", "")))
            self.manager.insert(0, values[3])
            self.priority.set(values[4])
            self.status.set(values[5])
            self.resources.insert(0, values[6])
    
    def _update_progress_label(self, event):
        """진행률 슬라이더 값 업데이트"""
        self.progress_label.configure(text=f"{int(self.progress.get())}%")
    
    def _save(self):
        """입력된 값 저장"""
        self.result = {
            "name": self.task_name.get(),
            "start_date": self.start_date.get_date(),
            "end_date": self.end_date.get_date(),
            "progress": self.progress.get(),
            "manager": self.manager.get(),
            "priority": self.priority.get(),
            "status": self.status.get(),
            "resources": [res.strip() for res in self.resources.get().split(",")] if self.resources.get() else []
        }
        self.destroy()

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("설정")
        self.geometry("400x300")
        
        # 팝업 창을 화면 중앙에 위치시키기
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
        
        # 모달 설정
        self.transient(parent)
        self.grab_set()
        
        # 설정 옵션들
        ctk.CTkLabel(self, text="테마:", font=('Noto Sans KR', 12)).pack(pady=5)
        self.theme_option = ttk.Combobox(self, values=["light", "dark"], font=('Noto Sans KR', 12))
        self.theme_option.pack(fill=tk.X, padx=20)
        
        # 적용/취소 버튼
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        apply_button = ctk.CTkButton(button_frame, text="적용", command=self._apply, font=('Noto Sans KR', 12))
        apply_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ctk.CTkButton(button_frame, text="취소", command=self.destroy, font=('Noto Sans KR', 12))
        cancel_button.pack(side=tk.LEFT, padx=5)
    
    def _apply(self):
        """설정 적용"""
        theme = self.theme_option.get()
        ctk.set_appearance_mode(theme)
        self.destroy()

class FilterDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("필터")
        self.geometry("400x300")
        
        # 팝업 창을 화면 중앙에 위치시키기
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
        
        # 모달 설정
        self.transient(parent)
        self.grab_set()
        
        # 필터 옵션들
        ctk.CTkLabel(self, text="상태:", font=('Noto Sans KR', 12)).pack(pady=5)
        self.status_filter = ttk.Combobox(self, values=TASK_STATUS, font=('Noto Sans KR', 12))
        self.status_filter.pack(fill=tk.X, padx=20)
        
        ctk.CTkLabel(self, text="우선순위:", font=('Noto Sans KR', 12)).pack(pady=5)
        self.priority_filter = ttk.Combobox(self, values=[level[0] for level in PRIORITY_LEVELS], font=('Noto Sans KR', 12))
        self.priority_filter.pack(fill=tk.X, padx=20)
        
        # 적용/취소 버튼
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        apply_button = ctk.CTkButton(button_frame, text="적용", command=self._apply, font=('Noto Sans KR', 12))
        apply_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ctk.CTkButton(button_frame, text="취소", command=self.destroy, font=('Noto Sans KR', 12))
        cancel_button.pack(side=tk.LEFT, padx=5)
    
    def _apply(self):
        """필터 적용"""
        status = self.status_filter.get()
        priority = self.priority_filter.get()
        print(f"필터 적용: 상태={status}, 우선순위={priority}")
        self.destroy()

class ResourceDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("리소스 관리")
        self.geometry("800x600")
        
        # 팝업 창을 화면 중앙에 위치시키기
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
        
        # 모달 설정
        self.transient(parent)
        self.grab_set()
        
        # 리소스 목록
        self._create_resource_list()
        
        # 리소스 할당
        self._create_resource_assignment()
        
        # 확인/취소 버튼
        self._create_buttons() 