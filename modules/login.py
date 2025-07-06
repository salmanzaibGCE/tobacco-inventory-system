from PyQt5.QtWidgets import (QWidget, QLineEdit, QPushButton, QVBoxLayout, 
                             QLabel, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from modules.dashboard import DashboardWindow
from modules.database import Database

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Tobacco Inventory - Login")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                color: #333;
                font-size: 16px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("🚬 Tobacco Inventory System")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        
        # Input fields
        self.username = QLineEdit()
        self.username.setPlaceholderText("👤 Username")
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("🔒 Password")
        self.password.setEchoMode(QLineEdit.Password)
        
        # Login button
        self.login_btn = QPushButton("🔓 Login")
        self.login_btn.clicked.connect(self.check_login)
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.login_btn)
        
        self.setLayout(layout)
        
        # Set focus to username field
        self.username.setFocus()
        
        # Enter key support
        self.username.returnPressed.connect(self.password.setFocus)
        self.password.returnPressed.connect(self.check_login)
    
    def check_login(self):
        username = self.username.text().strip()
        password = self.password.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                      (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            self.hide()
            self.dashboard = DashboardWindow(user)
            self.dashboard.show()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")
            self.password.clear()
            self.username.setFocus()