import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from constants import COLORS, TREE_COLUMNS, MENU_BUTTONS

class ProjectTreeView:
    def __init__(self, parent, style):
        self.frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS['background'],
            corner_radius=10
        )
        
        self.tree = self._create_tree(style)
        self._setup_scrollbar()
        self._configure_columns()
        self._configure_treeview_style(style)
        self._configure_tags()
    
    def _create_tree(self, style):
        tree = ttk.Treeview(
            self.frame,
            selectmode="browse",
            style="Treeview"
        )
        return tree
    
    def _setup_scrollbar(self):
        scrollbar = ttk.Scrollbar(
            self.frame,
            orient="vertical",
            command=self.tree.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
    
    def _configure_columns(self):
        self.tree["columns"] = [col[0] for col in TREE_COLUMNS]
        self.tree.column("#0", width=200, minwidth=150)
        
        # 헤더 스타일 설정
        style = ttk.Style()
        style.configure(
            "Treeview.Heading",
            font=('Noto Sans KR', 10, 'bold'),  # 헤더 폰트 크기 10으로 설정
            background=COLORS['primary'],
            foreground='white'
        )
        
        for col_name, width in TREE_COLUMNS:
            self.tree.column(col_name, width=width, minwidth=width)
            self.tree.heading(col_name, text=col_name)
    
    def _configure_treeview_style(self, style):
        style.configure(
            "Treeview",
            background=COLORS['background'],
            fieldbackground=COLORS['background'],
            foreground=COLORS['text'],
            rowheight=30,
            font=('Noto Sans KR', 10),  # 폰트 크기 10으로 설정
            borderwidth=0,
            relief="flat"
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS['primary'],
            foreground='white',
            relief="flat",
            font=('Noto Sans KR', 10, 'bold')  # 폰트 크기 10으로 설정
        )
        style.map(
            "Treeview",
            background=[('selected', COLORS['accent'])],
            foreground=[('selected', 'white')]
        )
        style.layout("Treeview", [
            ("Treeview.treearea", {"sticky": "nswe"})
        ])
        style.configure("Treeview", borderwidth=0, relief="flat")
        
        # 점선 스타일 설정
        style.configure("Treeview.Dashed",
            background=COLORS['background'],
            borderwidth=1,
            relief="solid",
        )
    
    def _configure_tags(self):
        self.tree.tag_configure(
            "project",
            font=('Noto Sans KR', 10, 'bold'),
            foreground=COLORS['primary']
        )
        self.tree.tag_configure(
            "task",
            font=('Noto Sans KR', 10)
        )
        self.tree.tag_configure(
            "delayed",
            foreground=COLORS['error']
        )
        self.tree.tag_configure(
            "completed",
            foreground=COLORS['success']
        )
        self.tree.tag_configure(
            "milestone",
            font=('Noto Sans KR', 10, 'bold'),
            foreground=COLORS['warning']
        )
        self.tree.tag_configure(
            "subtask",
            font=('Noto Sans KR', 10)
        )

class MenuBar:
    def __init__(self, parent, command_handler):
        self.frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS['background'],
            corner_radius=10
        )
        
        self._create_buttons(command_handler)
    
    def _create_buttons(self, command_handler):
        for i, (text, icon, command_name) in enumerate(MENU_BUTTONS):
            self.frame.grid_columnconfigure(i, weight=1)
            btn = ctk.CTkButton(
                self.frame,
                text=f"{icon} {text}",
                command=getattr(command_handler, command_name),
                font=('Noto Sans KR', 12, 'bold'),
                height=35,
                width=80,
                corner_radius=8,
                fg_color=COLORS['primary'],
            )
            btn.grid(
                row=0,
                column=i,
                padx=5,
                pady=5,
                sticky="ew"
            ) 