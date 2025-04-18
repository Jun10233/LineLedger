# LineLedger - 智慧記帳系統

一個結合地理位置的跨平台記帳應用程式，支援桌面端和 Line Bot 記帳。

## 功能特點

### 1. 記帳功能
- 輸入消費金額、品項和類別
- 地點選擇和自動地理編碼
- 支援備註和分類管理

### 2. 數據視覺化
- 月度消費趨勢圖表
- 分類支出分析
- 消費地點地圖顯示

### 3. 多平台支援
- PyQt5 桌面應用程式
- Line Bot 快速記帳

### 4. 雲端同步
- Firebase 即時數據同步
- 跨設備資料存取

## 安裝說明

1. 安裝必要套件：
```bash
pip install -r requirements.txt
```

2. 設定環境變數：
- 複製 `.env.example` 為 `.env`
- 填入 Firebase 和 Line Bot 相關設定

3. 啟動應用程式：
```bash
python main.py
```

## 環境需求

- Python 3.11+
- PyQt5
- Firebase Admin SDK
- Line Bot SDK

## 專案結構

```
LineLedger/
├── config/             # 設定檔
├── database/          # 資料庫操作
├── gui/               # 圖形界面
│   ├── dashboard_window.py
│   ├── expense_window.py
│   ├── history_window.py
│   └── statistics_window.py
├── line_bot/          # Line Bot 整合
├── services/          # 服務層
└── main.py           # 主程式入口
```

## 使用說明

### 桌面應用程式
1. 總覽頁面：查看每月消費統計和最近記錄
2. 記帳頁面：新增消費記錄，支援地點選擇
3. 歷史記錄：檢視和管理所有交易記錄
4. 統計分析：查看消費趨勢和分類分析

### Line Bot
發送格式：「在[地點]買了[品項]花了[金額]元」
例如：「在全聯買晚餐花了150元」

## 開發者

此專案由 [Jun] 開發維護。

## 授權條款

MIT License
