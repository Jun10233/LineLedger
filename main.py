import sys
from PyQt5.QtWidgets import QApplication
from gui.main_app_window import MainAppWindow
from config.firebase_config import initialize_firebase

def main():
    try:
        print("正在連接 Firebase...")
        initialize_firebase()
        
        app = QApplication(sys.argv)
        window = MainAppWindow()
        window.show()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"錯誤：{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
