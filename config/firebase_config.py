import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

def initialize_firebase():
    # 檢查是否已經初始化
    if not len(firebase_admin._apps):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cred_path = os.path.join(current_dir, "serviceAccountKey.json")
        
        if not os.path.exists(cred_path):
            raise FileNotFoundError("Firebase 憑證檔案不存在，請確認 serviceAccountKey.json 位置")
        
        try:
            # 初始化 Firebase
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("Firebase 正式環境連接成功！")
        except Exception as e:
            print(f"Firebase 連接錯誤: {str(e)}")
            raise
            
    return firestore.client()
