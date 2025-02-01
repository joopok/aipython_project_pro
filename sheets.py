import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from datetime import datetime, timedelta
from constants import *

class BaseSheet:
    def __init__(self, parent):
        self.frame = ctk.CTkFrame(parent)
        self.tree = None
        self._setup_treeview()
        
    def _setup_treeview(self):
        raise NotImplementedError

class ScheduleSheet(BaseSheet):
    def _setup_treeview(self):
        self.tree = ttk.Treeview(self.frame, columns=[col[0] for col in SCHEDULE_COLUMNS])
        for col, width in SCHEDULE_COLUMNS:
            self.tree.column(col, width=width)
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

class ProgressSheet(BaseSheet):
    def _setup_treeview(self):
        self.tree = ttk.Treeview(self.frame, columns=[col[0] for col in PROGRESS_COLUMNS])
        for col, width in PROGRESS_COLUMNS:
            self.tree.column(col, width=width)
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

class AnalysisSheet(BaseSheet):
    def _setup_treeview(self):
        self.tree = ttk.Treeview(self.frame, columns=[col[0] for col in ANALYSIS_COLUMNS])
        for col, width in ANALYSIS_COLUMNS:
            self.tree.column(col, width=width)
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
    def update_statistics(self, tasks):
        # tasks가 튜플인 경우 첫 번째 요소(리스트)를 사용
        if isinstance(tasks, tuple):
            tasks = tasks[0]
            
        total = len(tasks)
        completed = sum(1 for task in tasks if task["progress"] == 100)
        in_progress = sum(1 for task in tasks if 0 < task["progress"] < 100)
        delayed = sum(1 for task in tasks if task.get("status") == "지연")
        planned = sum(1 for task in tasks if task["progress"] == 0)
        
        # 기존 데이터 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 새 데이터 추가
        self.tree.insert("", "end", values=(
            "전체현황",
            total,
            completed,
            in_progress,
            delayed,
            planned,
            f"{(completed/total*100):.1f}%" if total > 0 else "0%"
        ))

class CalendarSheet(BaseSheet):
    def _setup_treeview(self):
        self.tree = ttk.Treeview(self.frame, columns=[col[0] for col in CALENDAR_COLUMNS])
        for col, width in CALENDAR_COLUMNS:
            self.tree.column(col, width=width)
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

class WorkloadSheet(BaseSheet):
    def _setup_treeview(self):
        self.tree = ttk.Treeview(self.frame, columns=[col[0] for col in WORKLOAD_COLUMNS])
        for col, width in WORKLOAD_COLUMNS:
            self.tree.column(col, width=width)
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True) 