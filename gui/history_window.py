from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, 
                           QTableWidgetItem, QPushButton, QHBoxLayout, 
                           QMessageBox)
from database.db_manager import DatabaseManager
from datetime import datetime
from .statistics_window import StatisticsWindow

class HistoryWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        
        # 創建主布局
        main_layout = QVBoxLayout(self)
        
        # 工具列
        toolbar = QHBoxLayout()
        refresh_btn = QPushButton("重新整理")
        refresh_btn.clicked.connect(self.load_transactions)
        
        stats_btn = QPushButton("查看統計")
        stats_btn.clicked.connect(self.show_statistics)
        
        toolbar.addWidget(refresh_btn)
        toolbar.addWidget(stats_btn)
        main_layout.addLayout(toolbar)
        
        # 交易記錄表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # 增加一列用於放置刪除按鈕
        self.table.setHorizontalHeaderLabels(["日期", "品項", "金額", "類別", "地點", "操作"])
        main_layout.addWidget(self.table)
        
        self.load_transactions()
    
    def load_transactions(self):
        transactions = self.db_manager.get_transactions()
        self.table.setRowCount(len(transactions))
        
        for i, trans in enumerate(transactions):
            # 處理日期顯示
            date_str = trans['date'].strftime('%Y-%m-%d %H:%M') if isinstance(trans['date'], datetime) else str(trans['date'])
            self.table.setItem(i, 0, QTableWidgetItem(date_str))
            self.table.setItem(i, 1, QTableWidgetItem(trans.get('item', '')))
            self.table.setItem(i, 2, QTableWidgetItem(f"{trans['amount']:,.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem(trans['category']))
            self.table.setItem(i, 4, QTableWidgetItem(trans['location']))
            
            # 添加刪除按鈕
            delete_btn = QPushButton("刪除")
            delete_btn.clicked.connect(lambda checked, row=i, id=trans.get('id'): self.delete_transaction(row, id))
            self.table.setCellWidget(i, 5, delete_btn)
    
    def delete_transaction(self, row, transaction_id):
        reply = QMessageBox.question(self, '確認刪除', 
                                   '確定要刪除這筆記錄嗎？',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.db_manager.delete_transaction(transaction_id):
                self.table.removeRow(row)
                QMessageBox.information(self, "成功", "記錄已刪除")
            else:
                QMessageBox.warning(self, "錯誤", "刪除失敗")
    
    def show_statistics(self):
        self.stats_window = StatisticsWindow(self)
        self.stats_window.show()
