import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from modules.login import LoginWindow
from modules.database import Database

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    # Initialize database
    db = Database()
    db.init_database()
    
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()