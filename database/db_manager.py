from typing import List, Optional
from datetime import datetime
from models.transaction import Transaction
from config.firebase_config import initialize_firebase

class DatabaseManager:
    def __init__(self):
        self.db = initialize_firebase()
        self.transactions_ref = self.db.collection('transactions')

    def add_transaction(self, transaction):
        # 確保資料格式正確
        if not isinstance(transaction, dict):
            raise ValueError("交易資料必須是字典格式")
        
        required_fields = ['amount', 'category', 'location', 'date']
        for field in required_fields:
            if field not in transaction:
                raise ValueError(f"缺少必要欄位: {field}")
        
        # 轉換日期格式為 timestamp
        if isinstance(transaction['date'], datetime):
            transaction['date'] = transaction['date'].isoformat()
            
        return self.transactions_ref.add(transaction)

    def delete_transaction(self, doc_id):
        try:
            self.transactions_ref.document(doc_id).delete()
            return True
        except Exception as e:
            print(f"刪除失敗: {str(e)}")
            return False
    
    def get_transactions(self) -> List[Transaction]:
        docs = self.transactions_ref.order_by('date', direction='DESCENDING').get()
        transactions = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id  # 添加文件ID
            if 'date' in data and isinstance(data['date'], str):
                data['date'] = datetime.fromisoformat(data['date'])
            transactions.append(data)
        return transactions

    def listen_transactions(self, callback):
        """設置即時監聽"""
        return self.transactions_ref.on_snapshot(callback)
