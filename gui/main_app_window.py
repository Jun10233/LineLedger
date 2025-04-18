from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                           QPushButton, QStackedWidget, QLabel)
from PyQt5.QtCore import Qt
from .dashboard_window import DashboardWindow
from .expense_window import ExpenseWindow
from .history_window import HistoryWindow
from .statistics_window import StatisticsWindow

class MainAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LineLedger")
        self.setGeometry(100, 100, 1200, 800)
        
        # 建立中央視窗
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 側邊欄
        sidebar = QWidget()
        sidebar.setMaximumWidth(200)
        sidebar.setMinimumWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Logo/標題
        logo = QLabel("LineLedger")
        logo.setStyleSheet("font-size: 20px; font-weight: bold; padding: 20px;")
        sidebar_layout.addWidget(logo)
        
        # 導航按鈕
        nav_buttons = [
            ("總覽", self.show_dashboard),
            ("記帳", self.show_expense),
            ("歷史記錄", self.show_history),
            ("統計分析", self.show_statistics)
        ]
        
        for text, callback in nav_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("text-align: left; padding: 10px;")
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)
        
        # 頁面堆疊
        self.stack = QStackedWidget()
        self.dashboard = DashboardWindow()
        self.expense = ExpenseWindow()
        self.expense.transaction_added.connect(self.update_all_pages)
        self.history = HistoryWindow()
        self.statistics = StatisticsWindow()
        
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.expense)
        self.stack.addWidget(self.history)
        self.stack.addWidget(self.statistics)
        
        main_layout.addWidget(self.stack)
        
        # 預設顯示總覽頁面
        self.show_dashboard()
    
    def show_dashboard(self):
        self.stack.setCurrentWidget(self.dashboard)
    
    def show_expense(self):
        self.stack.setCurrentWidget(self.expense)
    
    def show_history(self):
        self.stack.setCurrentWidget(self.history)
    
    def show_statistics(self):
        self.stack.setCurrentWidget(self.statistics)
    
    def update_all_pages(self):
        # 更新所有頁面的數據
        self.dashboard.load_dashboard_data()
        self.history.load_transactions()
        self.statistics.update_statistics()
