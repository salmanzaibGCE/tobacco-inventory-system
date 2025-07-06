from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGridLayout, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from modules.purchase import PurchaseWindow
from modules.sale import SaleWindow
from modules.inventory import InventoryWindow
from modules.reports import ReportsWindow

class DashboardWindow(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Tobacco Inventory - Dashboard")
        self.setFixedSize(800, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: Arial, sans-serif;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 15px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                min-height: 80px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel(f"Welcome, {self.user_data[1]}! 👋")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 20, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        
        # Menu buttons
        menu_frame = QFrame()
        menu_layout = QGridLayout(menu_frame)
        menu_layout.setSpacing(20)
        
        # Create buttons
        buttons = [
            ("📦 Purchase Entry", self.open_purchase, "#e74c3c"),
            ("💰 Sale Entry", self.open_sale, "#27ae60"),
            ("📋 Inventory", self.open_inventory, "#9b59b6"),
            ("📊 Reports", self.open_reports, "#f39c12"),
        ]
        
        for i, (text, handler, color) in enumerate(buttons):
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    padding: 20px;
                    border: none;
                    border-radius: 10px;
                    font-size: 16px;
                    font-weight: bold;
                    min-height: 100px;
                    min-width: 180px;
                }}
                QPushButton:hover {{
                    background-color: {color}dd;
                }}
            """)
            row, col = i // 2, i % 2
            menu_layout.addWidget(btn, row, col)
        
        main_layout.addWidget(header)
        main_layout.addWidget(menu_frame)
        
        self.setLayout(main_layout)
    
    def open_purchase(self):
        self.pur_win = PurchaseWindow()
        self.pur_win.show()
    
    def open_sale(self):
        self.sale_win = SaleWindow()
        self.sale_win.show()
    
    def open_inventory(self):
        self.inv_win = InventoryWindow()
        self.inv_win.show()
    
    def open_reports(self):
        self.rep_win = ReportsWindow()
        self.rep_win.show()
