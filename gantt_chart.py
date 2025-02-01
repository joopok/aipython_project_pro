import tkinter as tk
from datetime import datetime, timedelta
import calendar
from typing import List, Dict, Any
from constants import GANTT_COLORS

class GanttChart:
    def __init__(self, parent):
        # frame 생성
        self.frame = tk.Frame(parent)
        
        # 캔버스 생성
        self.canvas = tk.Canvas(
            self.frame,
            bg='white',
            highlightthickness=0
        )
        
        # 스크롤바 추가
        self.x_scrollbar = tk.Scrollbar(
            self.frame,
            orient="horizontal",
            command=self.canvas.xview
        )
        self.y_scrollbar = tk.Scrollbar(
            self.frame,
            orient="vertical",
            command=self.canvas.yview
        )
        
        # 스크롤바 설정
        self.canvas.configure(
            xscrollcommand=self.x_scrollbar.set,
            yscrollcommand=self.y_scrollbar.set
        )
        
        # 레이아웃 설정
        self.x_scrollbar.pack(side="bottom", fill="x")
        self.y_scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # 기본 설정
        self.cell_width = 25
        self.row_height = 35
        self.header_height = 50
        self.colors = GANTT_COLORS
        
        self.start_date = None
        self.end_date = None
        self.tasks = []
    
    def set_date_range(self, start_date: datetime, end_date: datetime):
        """차트의 시작일과 종료일 설정"""
        self.start_date = start_date
        self.end_date = end_date
        
        # 시작일을 해당 월의 1일로 조정
        self.start_date = self.start_date.replace(day=1)
        
        # 종료일을 해당 월의 말일로 조정
        last_day = calendar.monthrange(self.end_date.year, self.end_date.month)[1]
        self.end_date = self.end_date.replace(day=last_day)
    
    def draw(self, tasks: List[Dict[str, Any]]):
        """간트 차트 그리기"""
        self.tasks = tasks
        self.canvas.delete("all")  # 캔버스 초기화
        
        # 달력 헤더 그리기
        self.draw_calendar_header()
        
        # 그리드 그리기
        self.draw_grid()
        
        # 오늘 날짜 선 그리기
        self.draw_today_line()
        
        # 작업 바 그리기
        self.draw_task_bars()
        
        # 스크롤 영역 설정
        self.set_scroll_region()
    
    def draw_calendar_header(self):
        """달력 헤더 그리기"""
        current_date = self.start_date
        x = 0
        
        while current_date <= self.end_date:
            # 월 표시
            month_width = self.get_month_width(current_date)
            month_text = current_date.strftime("%Y년 %m월")
            
            self.canvas.create_rectangle(
                x, 0,
                x + month_width, self.header_height // 2,
                fill=self.colors['header_bg'],
                outline=self.colors['header_border']
            )
            self.canvas.create_text(
                x + month_width // 2,
                self.header_height // 4,
                text=month_text,
                font=("Noto Sans KR", 12, "bold")
            )
            
            # 일자 표시
            days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]
            for day in range(1, days_in_month + 1):
                day_x = x + (day - 1) * self.cell_width
                date = current_date.replace(day=day)
                
                # 주말 배경색 설정
                fill_color = self.colors['weekend_bg'] if date.weekday() >= 5 else "white"
                
                self.canvas.create_rectangle(
                    day_x, self.header_height // 2,
                    day_x + self.cell_width, self.header_height,
                    fill=fill_color,
                    outline=self.colors['grid']
                )
                self.canvas.create_text(
                    day_x + self.cell_width // 2,
                    self.header_height * 3 // 4,
                    text=str(day),
                    font=("Noto Sans KR", 12)
                )
            
            x += month_width
            current_date = self.get_next_month(current_date)
    
    def draw_grid(self):
        """그리드 라인 그리기"""
        total_width = self.get_total_width()
        total_height = self.header_height + len(self.tasks) * self.row_height
        
        # 세로선
        x = 0
        current_date = self.start_date
        while current_date <= self.end_date:
            self.canvas.create_line(
                x, self.header_height,
                x, total_height,
                fill=self.colors['grid']
            )
            x += self.cell_width
            current_date += timedelta(days=1)
        
        # 가로선
        for i in range(len(self.tasks) + 1):
            y = self.header_height + i * self.row_height
            self.canvas.create_line(
                0, y,
                total_width, y,
                fill=self.colors['grid']
            )
    
    def draw_task_bars(self):
        """작업 바 그리기"""
        for i, task in enumerate(self.tasks):
            start = task['start_date']
            end = task['end_date']
            progress = task['progress']
            
            # 작업 바의 위치 계산
            x1 = self.get_x_position(start)
            x2 = self.get_x_position(end) + self.cell_width
            y1 = self.header_height + i * self.row_height + 8
            y2 = y1 + self.row_height - 16
            
            # 작업 바 그리기
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=self.colors['bar_fill']['normal'],
                outline=self.colors['bar_border']
            )
            
            # 진행률 표시
            progress_width = (x2 - x1) * progress / 100
            if progress > 0:
                self.canvas.create_rectangle(
                    x1, y1,
                    x1 + progress_width, y2,
                    fill=self.colors['progress'],
                    outline=""
                )
            
            # 작업명 표시
            self.canvas.create_text(
                x1 + 5, y1 + (y2 - y1) // 2,
                text=task['name'],
                anchor="w",
                font=("Noto Sans KR", 12)
            )
    
    def draw_today_line(self):
        """오늘 날짜 선 그리기"""
        today = datetime.now()
        if self.start_date <= today <= self.end_date:
            x = self.get_x_position(today)
            total_height = self.header_height + len(self.tasks) * self.row_height
            
            self.canvas.create_line(
                x, self.header_height,
                x, total_height,
                fill=self.colors['today'],
                width=2,
                dash=(4, 4)
            )
    
    def get_month_width(self, date: datetime) -> int:
        """해당 월의 너비 계산"""
        days_in_month = calendar.monthrange(date.year, date.month)[1]
        return days_in_month * self.cell_width
    
    def get_next_month(self, date: datetime) -> datetime:
        """다음 달의 첫날 반환"""
        if date.month == 12:
            return date.replace(year=date.year + 1, month=1, day=1)
        return date.replace(month=date.month + 1, day=1)
    
    def get_x_position(self, date: datetime) -> int:
        """날짜의 x 좌표 계산"""
        days_diff = (date - self.start_date).days
        return days_diff * self.cell_width
    
    def get_total_width(self) -> int:
        """전체 차트의 너비 계산"""
        days_diff = (self.end_date - self.start_date).days + 1
        return days_diff * self.cell_width
    
    def set_scroll_region(self):
        """스크롤 영역 설정"""
        total_width = self.get_total_width()
        total_height = self.header_height + len(self.tasks) * self.row_height
        self.canvas.configure(scrollregion=(0, 0, total_width, total_height)) 