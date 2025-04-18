from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QFormLayout, QMessageBox,
                           QDialog, QComboBox, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import QUrl
from database.db_manager import DatabaseManager
import os
from datetime import datetime
import folium
from .map_selector import MapSelector
from .history_window import HistoryWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LineLedger")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize database
        self.db_manager = DatabaseManager()
        
        # Initialize address
        self.address = ""
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add transaction form
        form_layout = QFormLayout()
        
        # 類別選單
        self.category_input = QComboBox()
        self.category_input.addItems([
            "食物",
            "交通",
            "娛樂",
            "購物",
            "醫療",
            "住宿",
            "其他"
        ])
        
        self.amount_input = QLineEdit()
        self.note_input = QLineEdit()
        self.location_input = QLineEdit()
        self.location_input.setReadOnly(True)
        
        form_layout.addRow("金額:", self.amount_input)
        form_layout.addRow("類別:", self.category_input)
        form_layout.addRow("備註:", self.note_input)
        form_layout.addRow("地點:", self.location_input)
        
        # Add location picker button
        self.lat = 25.033
        self.lng = 121.565
        pick_location_btn = QPushButton("選擇位置")
        pick_location_btn.clicked.connect(self.show_map_selector)
        form_layout.addRow("位置:", pick_location_btn)
        
        submit_btn = QPushButton("記錄")
        submit_btn.clicked.connect(self.save_transaction)
        form_layout.addRow(submit_btn)
        
        layout.addLayout(form_layout)
        
        # Transaction list
        self.transaction_label = QLabel()
        layout.addWidget(self.transaction_label)
        
        # Map view using QLabel
        self.map_label = QLabel()
        self.map_label.setOpenExternalLinks(True)
        layout.addWidget(self.map_label)
        
        # 新增歷史記錄按鈕
        history_btn = QPushButton("查看歷史記錄")
        history_btn.clicked.connect(self.show_history)
        layout.addWidget(history_btn)
        
        # 添加歷史記錄表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["日期", "金額", "類別", "備註", "地點"])
        layout.addWidget(self.history_table)
        
        self._init_map()
        self._setup_realtime_updates()
        self.load_transactions()
    
    def show_map_selector(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("選擇位置")
        dialog.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        map_selector = MapSelector()
        layout.addWidget(map_selector)
        dialog.setLayout(layout)
        
        def on_location_selected(lat, lng, address):
            self.lat = lat
            self.lng = lng
            self.address = address
            self.location_input.setText(address)
            dialog.accept()
        
        map_selector.location_selected.connect(on_location_selected)
        dialog.exec_()

    def save_transaction(self):
        try:
            # 檢查金額是否為空
            if not self.amount_input.text().strip():
                QMessageBox.warning(self, "錯誤", "請輸入金額")
                return

            # 轉換金額為數值
            amount = float(self.amount_input.text().replace(',', ''))
            category = self.category_input.currentText()
            note = self.note_input.text()
            location = self.location_input.text()

            # 驗證其他必填欄位
            if not location:
                QMessageBox.warning(self, "錯誤", "請選擇位置")
                return

            transaction = {
                'amount': amount,
                'category': category,
                'note': note,
                'location': location,
                'date': datetime.now(),
                'latitude': getattr(self, 'lat', 0),
                'longitude': getattr(self, 'lng', 0)
            }
            
            print(f"Saving transaction: {transaction}")  # 除錯用
            self.db_manager.add_transaction(transaction)
            
            # 清空輸入欄位
            self.amount_input.clear()
            self.note_input.clear()
            self.location_input.clear()
            
            # 重新載入交易記錄
            self.load_transactions()
            
            QMessageBox.information(self, "成功", "交易已記錄")
            
        except ValueError as e:
            print(f"Value Error: {str(e)}")  # 除錯用
            QMessageBox.warning(self, "錯誤", "金額格式不正確，請確認是否為有效數字")
        except Exception as e:
            print(f"Error: {str(e)}")  # 除錯用
            QMessageBox.warning(self, "錯誤", f"儲存失敗: {str(e)}")
    
    def _init_map(self):
        html_content = """
        <html>
        <body>
            <h2>交易紀錄</h2>
            <table border="1">
                <tr>
                    <th>金額</th>
                    <th>地點</th>
                    <th>備註</th>
                </tr>
            </table>
        </body>
        </html>
        """
        with open("transactions.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        html_path = os.path.abspath("transactions.html")
        self.map_label.setText(f'<a href="file://{html_path}">查看交易紀錄</a>')
    
    def _setup_realtime_updates(self):
        def on_snapshot(doc_snapshot, changes, read_time):
            self._update_map_markers()
            
        self.db_manager.listen_transactions(on_snapshot)
    
    def _update_map_markers(self):
        transactions = self.db_manager.get_transactions()
        m = folium.Map(location=[25.033, 121.565], zoom_start=13)
        
        for trans in transactions:
            if 'latitude' in trans and 'longitude' in trans:
                folium.Marker(
                    [trans['latitude'], trans['longitude']],
                    popup=f"{trans['amount']}元 - {trans['note']}"
                ).add_to(m)
        
        html_path = os.path.abspath("transactions_map.html")
        m.save(html_path)
        self.map_label.setText(f'<a href="file://{html_path}">查看消費地圖</a>')
    
    def show_history(self):
        self.history_window = HistoryWindow(self)
        self.history_window.show()
    
    def load_transactions(self):
        transactions = self.db_manager.get_transactions()
        self.history_table.setRowCount(len(transactions))
        
        for i, trans in enumerate(transactions):
            self.history_table.setItem(i, 0, QTableWidgetItem(trans['date'].strftime('%Y-%m-%d %H:%M')))
            self.history_table.setItem(i, 1, QTableWidgetItem(f"{trans['amount']}"))
            self.history_table.setItem(i, 2, QTableWidgetItem(trans['category']))
            self.history_table.setItem(i, 3, QTableWidgetItem(trans['note']))
            self.history_table.setItem(i, 4, QTableWidgetItem(trans['location']))
