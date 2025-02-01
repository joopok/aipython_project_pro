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

class GanttApp(ctk.CTk):
    def __init__(self):
        super().__init__()
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
        
        # style 객체 생성
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._configure_treeview_style(self.style)
        
        self.menu_bar = MenuBar(self.main_container, self)
        self.project_tree = ProjectTreeView(self.main_container, self.style)
        self.gantt_chart = self._setup_gantt_chart()
        
        self._setup_layout()
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
        self.bind("<Configure>", self.on_window_resize)
        self.project_tree.tree.bind("<Button-3>", self.show_context_menu)
    
    def _load_data(self):
        """데이터 로드"""
        projects = generate_dummy_data()
        self._load_tree_data(projects)
        self._load_gantt_data(projects)
        
        # 모든 항목 펼치기
        self._expand_all_items("")
    
    def _load_tree_data(self, projects, parent=""):
        """트리뷰에 데이터 로드"""
        for project in projects:
            item_id = self.project_tree.tree.insert(
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
                self._load_tree_data(project["children"], item_id)
            
            # 점선 스타일 적용
            if parent:
                self.project_tree.tree.item(item_id, tags=("Dashed",))
    
    def _setup_gantt_chart(self):
        """간트 차트 영역 생성"""
        gantt_chart = GanttChart(self.main_container)
        return gantt_chart
    
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
        self.project_tree.tree.delete(*self.project_tree.tree.get_children())
        self.gantt_chart.canvas.delete("all")
        
        # 데이터 다시 로드
        self._load_data()
        
        # 화면 크기에 맞게 조정
        self.update_idletasks()  # 화면 업데이트 대기
        
        # 현재 창 크기 가져오기
        current_width = self.winfo_width()
        current_height = self.winfo_height()
        
        # 프로젝트 목록과 차트 영역 크기 조정
        project_tree_width = int(current_width * 0.3)
        gantt_chart_width = current_width - project_tree_width
        
        # 프로젝트 트리 크기 조정
        self.project_tree.frame.configure(width=project_tree_width)
        self.project_tree.tree.column("#0", width=int(project_tree_width * 0.4))
        
        # 각 컬럼 너비 조정
        remaining_width = project_tree_width * 0.6
        for col_name, _ in TREE_COLUMNS:
            col_width = int(remaining_width / len(TREE_COLUMNS))
            self.project_tree.tree.column(col_name, width=col_width)
        
        # 간트 차트 크기 조정
        self.gantt_chart.frame.configure(
            width=gantt_chart_width,
            height=current_height - self.menu_bar.frame.winfo_height()
        )
        
        # 직접 크기 조정 수행
        self._resize_components()
    
    def _resize_components(self):
        """프로젝트 목록과 차트 영역의 크기 조정"""
        total_width = self.winfo_width()
        total_height = self.winfo_height()
        project_tree_width = int(total_width * 0.3)
        gantt_chart_width = total_width - project_tree_width
        
        # 프로젝트 목록의 너비 조정
        self.project_tree.frame.configure(width=project_tree_width)
        self.project_tree.tree.column("#0", width=int(project_tree_width * 0.4))
        self.project_tree.tree.column("시작일", width=int(project_tree_width * 0.2))
        self.project_tree.tree.column("종료일", width=int(project_tree_width * 0.2))
        self.project_tree.tree.column("진행률", width=int(project_tree_width * 0.2))
        
        # 차트 영역의 너비 및 높이 조정
        self.gantt_chart.frame.configure(
            width=gantt_chart_width,
            height=total_height - self.menu_bar.frame.winfo_height()
        )
    
    def show_context_menu(self, event):
        """우클릭 메뉴 표시"""
        item = self.project_tree.tree.identify_row(event.y)
        if item:
            self.project_tree.tree.selection_set(item)
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
                
                # 데이터 작성
                self._export_items(writer)
            
            messagebox.showinfo("알림", "CSV 파일로 내보내기가 완료되었습니다.")
    
    def _export_items(self, writer, parent=""):
        """재귀적으로 모든 항목 내보내기"""
        for item in self.project_tree.tree.get_children(parent):
            values = self.project_tree.tree.item(item)['values']
            writer.writerow([
                item,  # 작업ID
                self.project_tree.tree.item(item)['text'],  # 작업명
                *values  # 나머지 값들
            ])
            self._export_items(writer, item)
    
    def add_task(self):
        """작업 추가"""
        dialog = TaskDialog(self)
        self.wait_window(dialog)
        if hasattr(dialog, 'result') and dialog.result:
            self.project_tree.tree.insert(
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
        selected = self.project_tree.tree.selection()
        if not selected:
            messagebox.showwarning("경고", "수정할 작업을 선택해주세요.")
            return
            
        item = selected[0]
        current_values = self.project_tree.tree.item(item)
        
        dialog = TaskDialog(
            self,
            name=current_values['text'],
            values=current_values['values']
        )
        self.wait_window(dialog)
        
        if hasattr(dialog, 'result') and dialog.result:
            self.project_tree.tree.item(
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
        selected = self.project_tree.tree.selection()
        if not selected:
            messagebox.showwarning("경고", "삭제할 작업을 선택해주세요.")
            return
            
        if messagebox.askyesno("확인", "선택한 작업을 삭제하시겠습니까?"):
            for item in selected:
                self.project_tree.tree.delete(item)
    
    def add_subtask(self):
        """하위 작업 추가"""
        selected = self.project_tree.tree.selection()
        if not selected:
            messagebox.showwarning("경고", "상위 작업을 선택해주세요.")
            return
        
        parent_item = selected[0]
        dialog = TaskDialog(self)
        self.wait_window(dialog)
        
        if hasattr(dialog, 'result') and dialog.result:
            self.project_tree.tree.insert(
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
        selected = self.project_tree.tree.selection()
        if not selected:
            return
        
        item = selected[0]
        prev = self.project_tree.tree.prev(item)
        if prev:
            self._swap_items(item, prev)

    def move_task_down(self):
        selected = self.project_tree.tree.selection()
        if not selected:
            return
        
        item = selected[0]
        next = self.project_tree.tree.next(item)
        if next:
            self._swap_items(item, next)

    def _swap_items(self, item1, item2):
        # 아이템 위치 교환 로직
        pass

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

    def _load_gantt_data(self, projects):
        """간트 차트에 데이터 로드"""
        # 모든 작업을 평면화된 리스트로 변환
        all_tasks = self._flatten_tasks(projects)
        
        if all_tasks:
            # 시작일과 종료일 설정
            start_date = min(task["start_date"] for task in all_tasks)
            end_date = max(task["end_date"] for task in all_tasks)
            
            # 간트 차트 초기화 및 그리기
            self.gantt_chart.set_date_range(start_date, end_date)
            self.gantt_chart.draw(all_tasks)

    def _flatten_tasks(self, projects):
        """프로젝트의 모든 작업을 평면화된 리스트로 변환"""
        tasks = []
        for project in projects:
            tasks.append({
                "name": project["name"],
                "start_date": project["start_date"],
                "end_date": project["end_date"],
                "progress": project["progress"]
            })
            if "children" in project:
                tasks.extend(self._flatten_tasks(project["children"]))
        return tasks

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

    def _expand_all_items(self, parent_item):
        """재귀적으로 모든 트리뷰 항목 펼치기"""
        self.project_tree.tree.item(parent_item, open=True)  # 현재 항목 펼치기
        for child in self.project_tree.tree.get_children(parent_item):
            self._expand_all_items(child)  # 재귀적으로 자식 항목들도 펼치기

if __name__ == "__main__":
    app = GanttApp()
    app.mainloop() 