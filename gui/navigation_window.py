from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton
from .expense_window import ExpenseWindow
from .history_window import HistoryWindow
from .statistics_window import StatisticsWindow
from .dashboard_window import DashboardWindow

class NavigationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LineLedger")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 添加 Dashboard 按鈕
        dashboard_btn = QPushButton("總覽")
        dashboard_btn.clicked.connect(self.show_dashboard)
        layout.insertWidget(0, dashboard_btn)  # 插入到最上方
        
        # 新增記帳按鈕
        expense_btn = QPushButton("記錄支出")
        expense_btn.clicked.connect(self.show_expense)
        layout.addWidget(expense_btn)
        
        # 歷史記錄按鈕
        history_btn = QPushButton("歷史記錄")
        history_btn.clicked.connect(self.show_history)
        layout.addWidget(history_btn)
        
        # 統計分析按鈕
        stats_btn = QPushButton("統計分析")
        stats_btn.clicked.connect(self.show_statistics)
        layout.addWidget(stats_btn)
        
        self.current_window = None
    
    def show_dashboard(self):
        self.current_window = DashboardWindow(self)
        self.current_window.show()
    
    def show_expense(self):
        self.current_window = ExpenseWindow(self)
        self.current_window.show()
    
    def show_history(self):
        self.current_window = HistoryWindow(self)
        self.current_window.show()
    
    def show_statistics(self):
        self.current_window = StatisticsWindow(self)
        self.current_window.show()
