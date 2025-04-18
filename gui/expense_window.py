from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                           QPushButton, QComboBox, QMessageBox, QDialog,
                           QListWidget, QLabel)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from database.db_manager import DatabaseManager
from datetime import datetime
from services.geocoding import GeocodingService
import os

class ExpenseWindow(QWidget):
    # 添加更新信號
    transaction_added = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.geocoding = GeocodingService()
        self.lat = None
        self.lng = None
        
        # 創建主布局
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # 品項輸入
        self.item_input = QLineEdit()
        form_layout.addRow("品項:", self.item_input)
        
        # 金額輸入
        self.amount_input = QLineEdit()
        form_layout.addRow("金額:", self.amount_input)
        
        # 類別選擇
        self.category_input = QComboBox()
        self.category_input.addItems(["餐飲", "交通", "娛樂", "購物", "醫療", "住宿", "其他"])
        form_layout.addRow("類別:", self.category_input)
        
        # 地點輸入和選擇按鈕
        self.location_input = QLineEdit()
        self.location_input.setReadOnly(True)
        pick_location_btn = QPushButton("選擇位置")
        pick_location_btn.clicked.connect(self.show_map_selector)
        form_layout.addRow("地點:", self.location_input)
        form_layout.addRow("", pick_location_btn)
        
        # 備註輸入
        self.note_input = QLineEdit()
        form_layout.addRow("備註:", self.note_input)
        
        # 儲存按鈕
        save_btn = QPushButton("儲存")
        save_btn.clicked.connect(self.save_transaction)
        form_layout.addRow("", save_btn)
        
        main_layout.addLayout(form_layout)
        
        # 添加地圖預覽
        self.map_preview = QWebEngineView()
        self.map_preview.setMinimumHeight(300)
        main_layout.addWidget(self.map_preview)
        
        # 初始化地圖
        self.update_map_preview(25.033, 121.565)  # 預設位置
    
    def update_map_preview(self, lat, lng):
        import folium
        m = folium.Map(location=[lat, lng], zoom_start=15)
        folium.Marker([lat, lng]).add_to(m)
        
        # 保存並顯示地圖
        html_path = os.path.abspath("preview_map.html")
        m.save(html_path)
        self.map_preview.setUrl(QUrl.fromLocalFile(html_path))
    
    def show_map_selector(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("搜尋地點")
        dialog.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        # 搜尋輸入
        search_input = QLineEdit()
        search_input.setPlaceholderText("輸入地址或地標...")
        layout.addWidget(search_input)
        
        # 搜尋按鈕
        search_btn = QPushButton("搜尋")
        layout.addWidget(search_btn)
        
        # 結果列表
        results_list = QListWidget()
        layout.addWidget(results_list)
        
        dialog.setLayout(layout)
        
        def search():
            query = search_input.text()
            if query:
                results = self.geocoding.search_location(query)
                results_list.clear()
                for result in results:
                    results_list.addItem(result['display_name'])
                    results_list.item(results_list.count() - 1).setData(
                        Qt.UserRole, 
                        (float(result['lat']), float(result['lon']))
                    )
        
        def select_result(item):
            lat, lng = item.data(Qt.UserRole)
            address = item.text()
            self.lat = lat
            self.lng = lng
            self.location_input.setText(address)
            self.update_map_preview(lat, lng)  # 添加這行來更新地圖
            dialog.accept()
        
        search_btn.clicked.connect(search)
        search_input.returnPressed.connect(search)
        results_list.itemClicked.connect(select_result)
        
        dialog.exec_()
    
    def save_transaction(self):
        try:
            # 取得表單數據
            item = self.item_input.text()
            amount = float(self.amount_input.text())
            category = self.category_input.currentText()
            note = self.note_input.text()
            location = self.location_input.text()
            
            # 驗證必填欄位
            if not item:
                QMessageBox.warning(self, "錯誤", "請輸入消費品項")
                return
                
            if not amount:
                QMessageBox.warning(self, "錯誤", "請輸入金額")
                return
                
            if not location:
                QMessageBox.warning(self, "錯誤", "請選擇位置")
                return
            
            # 建立交易資料
            transaction = {
                'item': item,
                'amount': amount,
                'category': category,
                'note': note,
                'location': location,
                'date': datetime.now(),
                'latitude': self.lat,
                'longitude': self.lng
            }
            
            # 儲存到資料庫
            self.db_manager.add_transaction(transaction)
            
            # 發送更新信號
            self.transaction_added.emit()
            
            # 清空表單
            self.item_input.clear()
            self.amount_input.clear()
            self.note_input.clear()
            self.location_input.clear()
            self.lat = None
            self.lng = None
            
            QMessageBox.information(self, "成功", "交易已記錄")
            
        except ValueError:
            QMessageBox.warning(self, "錯誤", "金額格式不正確，請確認是否為有效數字")
        except Exception as e:
            QMessageBox.warning(self, "錯誤", f"儲存失敗: {str(e)}")
