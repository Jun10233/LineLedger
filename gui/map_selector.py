from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                             QLineEdit, QListWidget, QListWidgetItem)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot, QUrl, Qt
from services.geocoding import GeocodingService
import folium
import os

class Bridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.map_selector = parent

    @pyqtSlot(float, float)
    def locationClicked(self, lat, lng):
        if self.map_selector:
            self.map_selector.handle_location_click(lat, lng)

class MapSelector(QWidget):
    location_selected = pyqtSignal(float, float, str)

    def __init__(self):
        super().__init__()
        self.geocoding = GeocodingService()
        self.selected_lat = None
        self.selected_lng = None
        self.selected_address = ""
        
        # 主布局
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 搜尋區域
        search_layout = QVBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("輸入地址或地標...")
        self.search_input.returnPressed.connect(self.search_location)
        search_layout.addWidget(self.search_input)
        
        # 搜尋按鈕
        search_btn = QPushButton("搜尋")
        search_btn.clicked.connect(self.search_location)
        search_layout.addWidget(search_btn)
        
        # 搜尋結果列表
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.select_search_result)
        search_layout.addWidget(self.results_list)
        
        layout.addLayout(search_layout)

        # 地址顯示
        self.address_label = QLabel("請在地圖上選擇位置")
        layout.addWidget(self.address_label)

        # 地圖視圖
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # 確認按鈕
        self.confirm_btn = QPushButton("確認位置")
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.clicked.connect(self.confirm_location)
        layout.addWidget(self.confirm_btn)

        # 設置 WebChannel
        self.bridge = Bridge(self)
        self.channel = QWebChannel()
        self.channel.registerObject('bridge', self.bridge)
        self.web_view.page().setWebChannel(self.channel)

        self.init_map()

    def init_map(self):
        m = folium.Map(location=[25.033, 121.565], zoom_start=15)
        html_path = os.path.abspath("select_location.html")
        m.save(html_path)

        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # 修改 JavaScript 初始化
        html = html.replace('</head>',
            '''
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            </head>
            ''')
        
        html = html.replace('</body>',
            '''
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                // 等待地圖初始化完成
                setTimeout(function() {
                    var mapElement = document.querySelector("#map");
                    if (mapElement && mapElement._leaflet_map) {
                        var map = mapElement._leaflet_map;
                        var currentMarker = null;
                        
                        new QWebChannel(qt.webChannelTransport, function(channel) {
                            window.bridge = channel.objects.bridge;
                            
                            map.on('click', function(e) {
                                if (currentMarker) {
                                    map.removeLayer(currentMarker);
                                }
                                currentMarker = L.marker(e.latlng).addTo(map);
                                window.bridge.locationClicked(e.latlng.lat, e.latlng.lng);
                            });
                        });
                    }
                }, 1000); // 給予地圖載入時間
            });
            </script>
            </body>
            ''')

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)

        self.web_view.setUrl(QUrl.fromLocalFile(html_path))

    def search_location(self):
        query = self.search_input.text()
        if query:
            self.results_list.clear()
            results = self.geocoding.search_location(query)
            for result in results:
                item = QListWidgetItem(result['display_name'])  # 修正這裡
                item.setData(Qt.UserRole, (float(result['lat']), float(result['lon'])))
                self.results_list.addItem(item)
    
    def select_search_result(self, item):
        lat, lng = item.data(Qt.UserRole)
        self.web_view.page().runJavaScript(
            f"map.setView([{lat}, {lng}], 15); "
            f"if(currentMarker) map.removeLayer(currentMarker); "
            f"currentMarker = L.marker([{lat}, {lng}]).addTo(map);"
        )
        self.handle_location_click(lat, lng)

    def handle_location_click(self, lat, lng):
        self.selected_lat = lat
        self.selected_lng = lng
        address = self.geocoding.get_address(lat, lng)
        self.selected_address = address
        self.address_label.setText(f"選擇的位置: {address}")
        self.confirm_btn.setEnabled(True)

    def confirm_location(self):
        if self.selected_lat and self.selected_lng:
            self.location_selected.emit(
                self.selected_lat,
                self.selected_lng,
                self.selected_address
            )
