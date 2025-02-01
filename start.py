import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
import customtkinter as ctk
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from dummy_data import generate_dummy_data
import csv
from gantt_chart import GanttChart
from dialogs import TaskDialog, SettingsDialog, FilterDialog
from constants import COLORS, WINDOW_MIN_SIZE, WINDOW_SIZE_RATIO, TREE_COLUMNS
from ui_components import ProjectTreeView, MenuBar
from sheets import ScheduleSheet, ProgressSheet, AnalysisSheet, CalendarSheet, WorkloadSheet
from login_dialog import LoginDialog

class GanttApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 로그인 검증 부분 제거
        self._load_fonts()  # 글꼴 로드 추가
        self._setup_window()
        self._setup_styles()
        self._init_ui()
        self._load_data()
    
    def _load_fonts(self):
        """글꼴 로드"""
        font_path = os.path.join("Noto_Sans_KR", "NotoSansKR-Black.otf")
        if os.path.exists(font_path):
            self.default_font = font.Font(family="Noto Sans KR", size=12)
            self.option_add("*Font", self.default_font)
    
    def _setup_window(self):
        self.title("프로젝트 Pro")
        self.configure(fg_color=COLORS['background'])
        
        # 화면 해상도 확인
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # 창 크기 설정
        window_width = int(screen_width * WINDOW_SIZE_RATIO)
        window_height = int(screen_height * WINDOW_SIZE_RATIO)
        
        # 최소 크기 설정
        min_width, min_height = WINDOW_MIN_SIZE
        window_width = max(window_width, min_width)
        window_height = max(window_height, min_height)
        
        # 창 위치 설정
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.minsize(min_width, min_height)
        
        # 창 최대화
        self.after(0, self._maximize_window)
    
    def _maximize_window(self):
        """창을 최대화"""
        self.state('zoomed')
    
    def _setup_styles(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        style = ttk.Style()
        style.theme_use('clam')
        self._configure_treeview_style(style)
    
    def _configure_treeview_style(self, style):
        style.configure(
            "Treeview",
            background=COLORS['background'],
            fieldbackground=COLORS['background'],
            foreground=COLORS['text'],
            rowheight=30,
            font=('Noto Sans KR', 10)  # 폰트 크기 10으로 설정
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS['primary'],
            foreground='white',
            relief="flat",
            font=('Noto Sans KR', 10, 'bold')  # 폰트 크기 10으로 설정
        )
    
    def _init_ui(self):
        self._setup_main_container()
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._configure_treeview_style(self.style)
        
        # 메뉴바 생성
        self.menu_bar = MenuBar(self.main_container, self)
        
        # 노트북(탭) 생성
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        
        # 각 시트 생성
        self.schedule_sheet = ScheduleSheet(self.notebook)
        self.progress_sheet = ProgressSheet(self.notebook)
        self.analysis_sheet = AnalysisSheet(self.notebook)
        self.calendar_sheet = CalendarSheet(self.notebook)
        self.workload_sheet = WorkloadSheet(self.notebook)
        
        # 노트북에 시트 추가
        self.notebook.add(self.schedule_sheet.frame, text="일정")
        self.notebook.add(self.progress_sheet.frame, text="진척")
        self.notebook.add(self.analysis_sheet.frame, text="분석")
        self.notebook.add(self.calendar_sheet.frame, text="캘린더")
        self.notebook.add(self.workload_sheet.frame, text="작업부하")
        
        # 간트 차트 생성 및 추가
        self.gantt_chart = GanttChart(self.main_container)
        self.gantt_chart.frame.grid(row=2, column=0, sticky="nsew")
        
        self._bind_events()
    
    def _setup_main_container(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.main_container = ctk.CTkFrame(
            self,
            fg_color=COLORS['background'],
            corner_radius=15
        )
        self.main_container.grid(
            row=0, column=0,
            sticky="nsew",
            padx=20, pady=20
        )
    
    def _setup_layout(self):
        self.menu_bar.frame.grid(
            row=0, column=0,
            columnspan=2,
            sticky="ew",
            pady=(0, 20)
        )
        
        self.project_tree.frame.grid(
            row=1, column=0,
            sticky="nsew",
            padx=(0, 10)
        )
        
        self.gantt_chart.frame.grid(
            row=1, column=1,
            sticky="nsew"
        )
    
    def _bind_events(self):
        """이벤트 바인딩"""
        self.bind("<Configure>", self.on_window_resize)
        # 각 시트의 트리뷰에 우클릭 메뉴 바인딩
        self.schedule_sheet.tree.bind("<Button-3>", self.show_context_menu)
        self.progress_sheet.tree.bind("<Button-3>", self.show_context_menu)
        self.analysis_sheet.tree.bind("<Button-3>", self.show_context_menu)
        self.calendar_sheet.tree.bind("<Button-3>", self.show_context_menu)
        self.workload_sheet.tree.bind("<Button-3>", self.show_context_menu)
    
    def _load_data(self):
        """데이터 로드"""
        projects = generate_dummy_data()
        
        # 각 시트에 데이터 로드
        self._load_schedule_data(projects)
        self._load_progress_data(projects)
        self._load_analysis_data(projects)
        self._load_calendar_data()
        self._load_workload_data(projects)
        
        # 간트 차트 데이터 로드
        self._load_gantt_data(projects)
        
        # 모든 항목 펼치기
        self._expand_all_items(self.schedule_sheet.tree)
        self._expand_all_items(self.progress_sheet.tree)
    
    def _load_schedule_data(self, projects):
        """일정 시트에 데이터 로드"""
        self._load_tree_data(projects, parent="", tree=self.schedule_sheet.tree)
    
    def _load_progress_data(self, projects):
        """진척 시트에 데이터 로드"""
        all_tasks = self._flatten_tasks(projects)
        if isinstance(all_tasks, tuple):
            all_tasks = all_tasks[0]  # 튜플이면 첫 번째 요소(tasks 리스트)만 사용
        
        for task in all_tasks:
            self.progress_sheet.tree.insert("", "end", values=(
                task["id"],
                task["name"],
                task["start_date"].strftime("%Y-%m-%d"),  # 계획 시작일
                task["end_date"].strftime("%Y-%m-%d"),    # 계획 종료일
                task.get("actual_start", "-"),            # 실제 시작일
                task.get("actual_end", "-"),              # 실제 종료일
                f"{task['progress']}%",
                task.get("delay_days", "0"),              # 지연일수
                task.get("status", "대기중")               # 상태
            ))
    
    def _load_analysis_data(self, projects):
        """분석 시트에 데이터 로드"""
        all_tasks = self._flatten_tasks(projects)
        self.analysis_sheet.update_statistics(all_tasks)
    
    def _load_calendar_data(self):
        """캘린더 시트에 데이터 로드"""
        # 공휴일 및 특별일정 로드
        holidays = [
            ("2024-01-01", "공휴일", "신정"),
            ("2024-02-09", "공휴일", "설날"),
            ("2024-03-01", "공휴일", "삼일절"),
            # ... 추가 일정
        ]
        
        for date, type_, note in holidays:
            self.calendar_sheet.tree.insert("", "end", values=(date, type_, note))
    
    def _load_workload_data(self, projects):
        """작업부하 시트에 데이터 로드"""
        all_tasks = self._flatten_tasks(projects)
        if isinstance(all_tasks, tuple):
            all_tasks = all_tasks[0]
        
        resource_workload = {}
        
        for task in all_tasks:
            # 작업 기간 계산 (종료일 - 시작일)
            duration = (task["end_date"] - task["start_date"]).days + 1
            
            for resource in task.get("resources", []):
                if resource not in resource_workload:
                    resource_workload[resource] = {"tasks": 0, "total_hours": 0}
                resource_workload[resource]["tasks"] += 1
                resource_workload[resource]["total_hours"] += duration * 8  # 8시간/일 기준
        
        # 기존 데이터 삭제
        for item in self.workload_sheet.tree.get_children():
            self.workload_sheet.tree.delete(item)
        
        # 새 데이터 추가
        for resource, data in resource_workload.items():
            available_hours = data["total_hours"] * 1.2  # 예시: 가용시간은 총시간의 120%
            workload_rate = f"{(data['total_hours']/available_hours*100):.1f}%"
            
            self.workload_sheet.tree.insert("", "end", values=(
                resource,
                data["tasks"],
                data["total_hours"],
                available_hours,
                workload_rate
            ))
    
    def _load_tree_data(self, projects, parent="", tree=None):
        """트리뷰에 데이터 로드"""
        for project in projects:
            item_id = tree.insert(
                parent,
                "end",
                text=project["name"],
                values=(
                    project["start_date"].strftime("%Y-%m-%d"),
                    project["end_date"].strftime("%Y-%m-%d"),
                    f"{int(project['progress'])}%",
                    project.get("manager", ""),
                    project.get("priority", ""),
                    project.get("status", ""),
                    ", ".join(project.get("resources", []))
                ),
                tags=("project",)
            )
            if "children" in project:
                self._load_tree_data(project["children"], item_id, tree)
            
            # 점선 스타일 적용
            if parent:
                tree.item(item_id, tags=("Dashed",))
    
    def _flatten_tasks(self, projects, task_id=1):
        """프로젝트의 모든 작업을 평면화된 리스트로 변환"""
        tasks = []
        for project in projects:
            task = {
                "id": f"TASK-{task_id:04d}",
                "name": project["name"],
                "start_date": project["start_date"],
                "end_date": project["end_date"],
                "progress": project["progress"],
                "status": project.get("status", "대기중"),
                "actual_start": project.get("actual_start", None),
                "actual_end": project.get("actual_end", None),
                "delay_days": self._calculate_delay(project),
            }
            tasks.append(task)
            task_id += 1
            
            if "children" in project:
                child_tasks = self._flatten_tasks(project["children"], task_id)
                if isinstance(child_tasks, tuple):
                    child_tasks, task_id = child_tasks
                tasks.extend(child_tasks)
        
        if task_id == 1:
            return tasks
        return tasks, task_id
    
    def _calculate_delay(self, task):
        """작업의 지연일수 계산"""
        if task.get("actual_end") and task["end_date"]:
            actual_end = task["actual_end"] if isinstance(task["actual_end"], datetime) else datetime.strptime(task["actual_end"], "%Y-%m-%d")
            planned_end = task["end_date"]
            delay = (actual_end - planned_end).days
            return max(0, delay)
        return 0
    
    def on_window_resize(self, event):
        if event.widget == self:
            # 최소 크기 제한
            if event.width < 900:
                self.geometry(f"900x{event.height}")
            if event.height < 600:
                self.geometry(f"{event.width}x600")
            
            # 프로젝트 목록과 차트 영역의 크기 조정
            total_width = self.winfo_width()
            total_height = self.winfo_height()
            project_tree_width = int(total_width * 0.3)  # 프로젝트 목록의 너비를 전체의 30%로 설정
            gantt_chart_width = total_width - project_tree_width  # 차트 영역의 나머지 너비
            
            # 프로젝트 목록의 너비 조정
            self.project_tree.frame.configure(width=project_tree_width)
            self.project_tree.tree.column("#0", width=int(project_tree_width * 0.4))
            self.project_tree.tree.column("시작일", width=int(project_tree_width * 0.2))
            self.project_tree.tree.column("종료일", width=int(project_tree_width * 0.2))
            self.project_tree.tree.column("진행률", width=int(project_tree_width * 0.2))
            
            # 차트 영역의 너비 및 높이 조정
            self.gantt_chart.frame.configure(width=gantt_chart_width, height=total_height - self.menu_bar.frame.winfo_height())
    
    def refresh(self):
        """프로그램 새로고침"""
        # 기존 데이터 초기화
        for sheet in [self.schedule_sheet, self.progress_sheet, 
                     self.analysis_sheet, self.calendar_sheet, 
                     self.workload_sheet]:
            sheet.tree.delete(*sheet.tree.get_children())
        
        # 데이터 다시 로드
        self._load_data()
        
        # 화면 크기에 맞게 조정
        self.update_idletasks()
        
        # 현재 창 크기 가져오기
        current_width = self.winfo_width()
        current_height = self.winfo_height()
        
        # 각 시트의 크기 조정
        self._resize_components()
    
    def _resize_components(self):
        """컴포넌트 크기 조정"""
        total_width = self.winfo_width()
        total_height = self.winfo_height()
        
        # 메뉴바를 제외한 높이 계산
        content_height = total_height - self.menu_bar.frame.winfo_height()
        
        # 노트북 크기 조정
        self.notebook.configure(width=total_width, height=content_height)
        
        # 각 시트의 프레임 크기 조정
        for sheet in [self.schedule_sheet, self.progress_sheet, 
                     self.analysis_sheet, self.calendar_sheet, 
                     self.workload_sheet]:
            sheet.frame.configure(width=total_width, height=content_height)
    
    def show_context_menu(self, event):
        """우클릭 메뉴 표시"""
        tree = event.widget  # 이벤트가 발생한 트리뷰 위젯
        item = tree.identify_row(event.y)
        if item:
            tree.selection_set(item)
            self.menu_bar.context_menu.post(event.x_root, event.y_root)
    
    def export_to_csv(self):
        """CSV 파일로 내보내기"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                # 헤더 작성
                writer.writerow([
                    "작업ID",
                    "작업명",
                    "시작일",
                    "종료일",
                    "진행률",
                    "담당자",
                    "우선순위",
                    "상태",
                    "리소스"
                ])
                
                # 현재 활성화된 시트의 데이터 내보내기
                current_tab = self.notebook.select()
                current_sheet = self.notebook.tab(current_tab, "text")
                
                if current_sheet == "일정":
                    tree = self.schedule_sheet.tree
                elif current_sheet == "진척":
                    tree = self.progress_sheet.tree
                else:
                    tree = self.schedule_sheet.tree  # 기본값
                
                self._export_items(writer, tree=tree)
            
            messagebox.showinfo("알림", "CSV 파일로 내보내기가 완료되었습니다.")
    
    def _export_items(self, writer, parent="", tree=None):
        """재귀적으로 모든 항목 내보내기"""
        for item in tree.get_children(parent):
            values = tree.item(item)['values']
            writer.writerow([
                item,  # 작업ID
                tree.item(item)['text'],  # 작업명
                *values  # 나머지 값들
            ])
            self._export_items(writer, item, tree)
    
    def add_task(self):
        """작업 추가"""
        # 현재 활성화된 시트의 트리뷰 가져오기
        current_tab = self.notebook.select()
        current_sheet = self.notebook.tab(current_tab, "text")
        
        if current_sheet == "일정":
            tree = self.schedule_sheet.tree
        elif current_sheet == "진척":
            tree = self.progress_sheet.tree
        else:
            messagebox.showwarning("경고", "일정 또는 진척 탭에서만 작업을 추가할 수 있습니다.")
            return
        
        dialog = TaskDialog(self)
        self.wait_window(dialog)
        if hasattr(dialog, 'result') and dialog.result:
            tree.insert(
                "",
                "end",
                text=dialog.result["name"],
                values=(
                    dialog.result["start_date"].strftime("%Y-%m-%d"),
                    dialog.result["end_date"].strftime("%Y-%m-%d"),
                    f"{int(dialog.result['progress'])}%",
                    dialog.result.get("manager", ""),
                    dialog.result.get("priority", ""),
                    dialog.result.get("status", ""),
                    ", ".join(dialog.result.get("resources", []))
                ),
                tags=("task",)
            )
    
    def edit_task(self):
        """작업 수정"""
        # 현재 활성화된 시트의 트리뷰 가져오기
        current_tab = self.notebook.select()
        current_sheet = self.notebook.tab(current_tab, "text")
        
        if current_sheet == "일정":
            tree = self.schedule_sheet.tree
        elif current_sheet == "진척":
            tree = self.progress_sheet.tree
        else:
            messagebox.showwarning("경고", "일정 또는 진척 탭에서만 작업을 수정할 수 있습니다.")
            return
        
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("경고", "수정할 작업을 선택해주세요.")
            return
        
        item = selected[0]
        current_values = tree.item(item)
        
        dialog = TaskDialog(
            self,
            name=current_values['text'],
            values=current_values['values']
        )
        self.wait_window(dialog)
        
        if hasattr(dialog, 'result') and dialog.result:
            tree.item(
                item,
                text=dialog.result["name"],
                values=(
                    dialog.result["start_date"].strftime("%Y-%m-%d"),
                    dialog.result["end_date"].strftime("%Y-%m-%d"),
                    f"{int(dialog.result['progress'])}%",
                    dialog.result.get("manager", ""),
                    dialog.result.get("priority", ""),
                    dialog.result.get("status", ""),
                    ", ".join(dialog.result.get("resources", []))
                )
            )
    
    def delete_task(self):
        """작업 삭제"""
        # 현재 활성화된 시트의 트리뷰 가져오기
        current_tab = self.notebook.select()
        current_sheet = self.notebook.tab(current_tab, "text")
        
        if current_sheet == "일정":
            tree = self.schedule_sheet.tree
        elif current_sheet == "진척":
            tree = self.progress_sheet.tree
        else:
            messagebox.showwarning("경고", "일정 또는 진척 탭에서만 작업을 삭제할 수 있습니다.")
            return
        
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("경고", "삭제할 작업을 선택해주세요.")
            return
        
        if messagebox.askyesno("확인", "선택한 작업을 삭제하시겠습니까?"):
            for item in selected:
                tree.delete(item)
    
    def add_subtask(self):
        """하위 작업 추가"""
        # 현재 활성화된 시트의 트리뷰 가져오기
        current_tab = self.notebook.select()
        current_sheet = self.notebook.tab(current_tab, "text")
        
        if current_sheet == "일정":
            tree = self.schedule_sheet.tree
        elif current_sheet == "진척":
            tree = self.progress_sheet.tree
        else:
            messagebox.showwarning("경고", "일정 또는 진척 탭에서만 하위 작업을 추가할 수 있습니다.")
            return
        
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("경고", "상위 작업을 선택해주세요.")
            return
        
        parent_item = selected[0]
        dialog = TaskDialog(self)
        self.wait_window(dialog)
        
        if hasattr(dialog, 'result') and dialog.result:
            tree.insert(
                parent_item,  # 선택된 항목의 하위로 추가
                "end",
                text=dialog.result["name"],
                values=(
                    dialog.result["start_date"].strftime("%Y-%m-%d"),
                    dialog.result["end_date"].strftime("%Y-%m-%d"),
                    f"{int(dialog.result['progress'])}%",
                    dialog.result.get("manager", ""),
                    dialog.result.get("priority", ""),
                    dialog.result.get("status", ""),
                    ", ".join(dialog.result.get("resources", []))
                ),
                tags=("task",)
            )
    
    # 메뉴 기능들 (구현 예정)
    def new_project(self): pass
    def save_project(self): pass
    def manage_resources(self): pass
    def generate_report(self): pass

    def move_task_up(self):
        # 현재 활성화된 시트의 트리뷰 가져오기
        current_tab = self.notebook.select()
        current_sheet = self.notebook.tab(current_tab, "text")
        
        if current_sheet == "일정":
            tree = self.schedule_sheet.tree
        elif current_sheet == "진척":
            tree = self.progress_sheet.tree
        else:
            return
        
        selected = tree.selection()
        if not selected:
            return
        
        item = selected[0]
        prev = tree.prev(item)
        if prev:
            self._swap_items(tree, item, prev)

    def move_task_down(self):
        # 현재 활성화된 시트의 트리뷰 가져오기
        current_tab = self.notebook.select()
        current_sheet = self.notebook.tab(current_tab, "text")
        
        if current_sheet == "일정":
            tree = self.schedule_sheet.tree
        elif current_sheet == "진척":
            tree = self.progress_sheet.tree
        else:
            return
        
        selected = tree.selection()
        if not selected:
            return
        
        item = selected[0]
        next = tree.next(item)
        if next:
            self._swap_items(tree, item, next)

    def _swap_items(self, tree, item1, item2):
        """아이템 위치 교환 로직"""
        item1_values = tree.item(item1, "values")
        item2_values = tree.item(item2, "values")
        tree.item(item1, values=item2_values)
        tree.item(item2, values=item1_values)

    def show_filters(self):
        dialog = FilterDialog(self)
        self.wait_window(dialog)
        if hasattr(dialog, 'result'):
            self._apply_filters(dialog.result)

    def open_settings(self):
        dialog = SettingsDialog(self)
        self.wait_window(dialog)
        if hasattr(dialog, 'result'):
            self._apply_settings(dialog.result)

    def toggle_timeline(self):
        # 타임라인 표시/숨기기
        pass

    def _configure_tags(self):
        """트리뷰 항목의 태그 설정"""
        self.project_tree.tree.tag_configure(
            "project",
            font=('Helvetica', 11, 'bold'),
            foreground=COLORS['primary'],
            background=COLORS['background']
        )
        self.project_tree.tree.tag_configure(
            "task",
            font=('Helvetica', 10),
            background=COLORS['accent']
        )
        self.project_tree.tree.tag_configure(
            "subtask",
            font=('Helvetica', 9),
            background=COLORS['secondary']
        )

    def _expand_all_items(self, tree, parent_item=""):
        """재귀적으로 모든 트리뷰 항목 펼치기"""
        tree.item(parent_item, open=True)  # 현재 항목 펼치기
        for child in tree.get_children(parent_item):
            self._expand_all_items(tree, child)  # 재귀적으로 자식 항목들도 펼치기

    def _load_gantt_data(self, projects):
        """간트 차트에 데이터 로드"""
        all_tasks = self._flatten_tasks(projects)
        
        if all_tasks:
            # 시작일과 종료일 설정
            start_date = min(task["start_date"] for task in all_tasks)
            end_date = max(task["end_date"] for task in all_tasks)
            
            # 간트 차트 초기화 및 그리기
            self.gantt_chart.set_date_range(start_date, end_date)
            self.gantt_chart.draw(all_tasks)

if __name__ == "__main__":
    # root 윈도우 생성 및 설정
    root = ctk.CTk()
    root.withdraw()  # 메인 윈도우 숨기기
    
    # 화면 중앙에 위치시키기 위한 업데이트
    root.update_idletasks()
    
    # 로그인 다이얼로그 표시
    login = LoginDialog(root)
    
    # 로그인 창이 닫힐 때까지 대기
    root.wait_window(login)
    
    # 로그인 성공 시에만 메인 앱 실행
    if hasattr(login, 'result') and login.result:
        root.destroy()  # 숨겨진 root 창 제거
        app = GanttApp()
        app.mainloop()
    else:
        root.destroy()  # 로그인 실패 시 종료 