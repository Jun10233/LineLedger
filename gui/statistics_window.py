from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QComboBox, QPushButton, QScrollArea)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
from database.db_manager import DatabaseManager

class StatisticsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 控制面板
        control_panel = QHBoxLayout()
        
        # 時間範圍選擇
        self.period_combo = QComboBox()
        self.period_combo.addItems(["本月", "上月", "近三個月", "近半年", "今年"])
        self.period_combo.currentTextChanged.connect(self.update_statistics)
        control_panel.addWidget(QLabel("時間範圍:"))
        control_panel.addWidget(self.period_combo)
        
        # 更新按鈕
        refresh_btn = QPushButton("更新統計")
        refresh_btn.clicked.connect(self.update_statistics)
        control_panel.addWidget(refresh_btn)
        
        main_layout.addLayout(control_panel)
        
        # 統計摘要區
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("font-size: 14px;")
        main_layout.addWidget(self.summary_label)
        
        # 圖表區域
        charts_layout = QHBoxLayout()
        
        # 消費趨勢圖
        self.trend_view = QWebEngineView()
        charts_layout.addWidget(self.trend_view)
        
        # 類別分析圖
        self.category_view = QWebEngineView()
        charts_layout.addWidget(self.category_view)
        
        main_layout.addLayout(charts_layout)
        
        self.update_statistics()
    
    def update_statistics(self):
        transactions = self.db_manager.get_transactions()
        period = self.period_combo.currentText()
        
        # 過濾資料
        filtered_trans = self.filter_transactions(transactions, period)
        
        if not filtered_trans:
            self.summary_label.setText("所選期間沒有交易記錄")
            return
        
        # 計算統計數據
        total = sum(t['amount'] for t in filtered_trans)
        avg = total / len(filtered_trans)
        max_trans = max(filtered_trans, key=lambda x: x['amount'])
        
        # 更新統計摘要
        summary = f"""
        統計期間: {period}
        總支出: ${total:,.2f}
        平均每筆: ${avg:,.2f}
        交易筆數: {len(filtered_trans)}
        最大支出: ${max_trans['amount']:,.2f} ({max_trans['item']})
        """
        self.summary_label.setText(summary)
        
        # 更新趨勢圖
        self.update_trend_chart(filtered_trans)
        
        # 更新類別分析圖
        self.update_category_chart(filtered_trans)
    
    def filter_transactions(self, transactions, period):
        now = datetime.now()
        if period == "本月":
            return [t for t in transactions if t['date'].month == now.month and t['date'].year == now.year]
        elif period == "上月":
            last_month = now.replace(day=1) - timedelta(days=1)
            return [t for t in transactions if t['date'].month == last_month.month and t['date'].year == last_month.year]
        elif period == "近三個月":
            three_months_ago = now - timedelta(days=90)
            return [t for t in transactions if t['date'] >= three_months_ago]
        elif period == "近半年":
            six_months_ago = now - timedelta(days=180)
            return [t for t in transactions if t['date'] >= six_months_ago]
        else:  # 今年
            return [t for t in transactions if t['date'].year == now.year]
    
    def update_trend_chart(self, transactions):
        df = pd.DataFrame(transactions)
        df['date'] = pd.to_datetime(df['date'])
        daily_amounts = df.groupby('date')['amount'].sum()
        
        fig = make_subplots(rows=2, cols=1)
        
        # 每日消費趨勢
        fig.add_trace(
            go.Scatter(x=daily_amounts.index, y=daily_amounts.values, name="每日消費"),
            row=1, col=1
        )
        
        # 類別趨勢
        category_trend = df.pivot_table(
            index='date',
            columns='category',
            values='amount',
            aggfunc='sum'
        ).fillna(0)
        
        for category in category_trend.columns:
            fig.add_trace(
                go.Scatter(
                    x=category_trend.index,
                    y=category_trend[category],
                    name=category,
                    stackgroup='category'
                ),
                row=2, col=1
            )
        
        fig.update_layout(height=600, title="消費趨勢分析")
        
        # 保存並顯示圖表
        trend_path = os.path.join(os.path.dirname(__file__), 'trend_chart.html')
        fig.write_html(trend_path)
        self.trend_view.setUrl(QUrl.fromLocalFile(trend_path))
    
    def update_category_chart(self, transactions):
        df = pd.DataFrame(transactions)
        category_sums = df.groupby('category')['amount'].agg(['sum', 'count'])
        
        fig = make_subplots(rows=1, cols=2, specs=[[{'type':'pie'}, {'type':'pie'}]])
        
        # 金額占比
        fig.add_trace(
            go.Pie(
                labels=category_sums.index,
                values=category_sums['sum'],
                name="金額占比"
            ),
            row=1, col=1
        )
        
        # 筆數占比
        fig.add_trace(
            go.Pie(
                labels=category_sums.index,
                values=category_sums['count'],
                name="筆數占比"
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            height=400,
            title="類別分析（左：金額占比，右：筆數占比）"
        )
        
        # 保存並顯示圖表
        category_path = os.path.join(os.path.dirname(__file__), 'category_chart.html')
        fig.write_html(category_path)
        self.category_view.setUrl(QUrl.fromLocalFile(category_path))
