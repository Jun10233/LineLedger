from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import re
from database.db_manager import DatabaseManager
from models.transaction import Transaction
from datetime import datetime

class LedgerBot:
    def __init__(self, channel_access_token: str, channel_secret: str):
        self.line_bot_api = LineBotApi(channel_access_token)
        self.handler = WebhookHandler(channel_secret)
        self.db = DatabaseManager()

    def parse_message(self, text: str) -> Transaction:
        # 簡單的自然語言解析
        amount_pattern = r'(\d+)元'
        location_pattern = r'在([\w]+)'
        
        amount = float(re.search(amount_pattern, text).group(1))
        location = re.search(location_pattern, text).group(1)
        
        return Transaction(
            amount=amount,
            category="支出",  # 預設類別
            note=text,
            date=datetime.now(),
            location=location
        )

    @handler.add(MessageEvent, message=TextMessage)
    def handle_message(self, event):
        try:
            transaction = self.parse_message(event.message.text)
            self.db.add_transaction(transaction)
            reply_message = f"已記錄: {transaction.amount}元 at {transaction.location}"
        except Exception as e:
            reply_message = "格式不正確，請重試"
        
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )
