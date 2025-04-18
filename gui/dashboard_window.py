from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from database.db_manager import DatabaseManager
import folium
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

class DashboardWindow(QWidget):  # 改為 QWidget
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        
        # 創建主布局
        main_layout = QVBoxLayout(self)
        
        # 上方統計區
        stats_layout = QHBoxLayout()
        self.total_expense = QLabel("本月總支出: $0")
        self.total_expense.setStyleSheet("font-size: 18px; font-weight: bold;")
        stats_layout.addWidget(self.total_expense)
        main_layout.addLayout(stats_layout)
        
        # 中間圖表和地圖區
        charts_layout = QHBoxLayout()
        
        # 圓餅圖
        self.pie_view = QWebEngineView()
        charts_layout.addWidget(self.pie_view)
        
        # 地圖
        self.map_view = QWebEngineView()
        charts_layout.addWidget(self.map_view)
        
        main_layout.addLayout(charts_layout)
        
        # 最近消費記錄
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(4)
        self.recent_table.setHorizontalHeaderLabels(["日期", "金額", "類別", "地點"])
        main_layout.addWidget(self.recent_table)
        
        self.load_dashboard_data()
    
    def load_dashboard_data(self):
        transactions = self.db_manager.get_transactions()
        now = datetime.now()
        
        # 過濾本月資料
        monthly_trans = [t for t in transactions 
                        if t['date'].month == now.month and 
                        t['date'].year == now.year]
        
        # 更新總支出
        total = sum(t['amount'] for t in monthly_trans)
        self.total_expense.setText(f"本月總支出: ${total:,.2f}")
        
        # 更新圓餅圖
        self.update_pie_chart(monthly_trans)
        
        # 更新地圖
        self.update_map(transactions)
        
        # 更新最近消費記錄
        self.update_recent_transactions(transactions[:5])
    
    def update_pie_chart(self, transactions):
        # 計算各類別總額
        category_sums = {}
        for t in transactions:
            cat = t['category']
            category_sums[cat] = category_sums.get(cat, 0) + t['amount']
        
        # 建立圓餅圖
        fig = go.Figure(data=[go.Pie(
            labels=list(category_sums.keys()),
            values=list(category_sums.values())
        )])
        
        # 儲存為臨時HTML
        temp_path = os.path.join(os.path.dirname(__file__), 'temp_pie.html')
        fig.write_html(temp_path)
        self.pie_view.setUrl(QUrl.fromLocalFile(temp_path))
    
    def update_map(self, transactions):
        m = folium.Map(location=[25.033, 121.565], zoom_start=13)
        
        # 添加所有消費地點
        for t in transactions:
            if t.get('latitude') and t.get('longitude'):
                folium.Marker(
                    [t['latitude'], t['longitude']],
                    popup=f"{t['amount']}元 - {t['category']}"
                ).add_to(m)
        
        # 儲存地圖
        temp_path = os.path.join(os.path.dirname(__file__), 'temp_map.html')
        m.save(temp_path)
        self.map_view.setUrl(QUrl.fromLocalFile(temp_path))
    
    def update_recent_transactions(self, transactions):
        self.recent_table.setRowCount(len(transactions))
        for i, trans in enumerate(transactions):
            self.recent_table.setItem(i, 0, QTableWidgetItem(
                trans['date'].strftime('%Y-%m-%d %H:%M')))
            self.recent_table.setItem(i, 1, QTableWidgetItem(
                f"${trans['amount']:,.2f}"))
            self.recent_table.setItem(i, 2, QTableWidgetItem(
                trans['category']))
            self.recent_table.setItem(i, 3, QTableWidgetItem(
                trans['location']))
