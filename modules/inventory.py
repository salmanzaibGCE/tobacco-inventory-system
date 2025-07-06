from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLabel, QMessageBox,
                             QLineEdit, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from modules.database import Database

class InventoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()
        self.load_inventory()
    
    def init_ui(self):
        self.setWindowTitle("Inventory Management")
        self.setFixedSize(900, 650)  # Slightly larger for better view
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: Arial, sans-serif;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                gridline-color: #ecf0f1;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("📋 Current Inventory")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        
        # Search and controls bar
        controls_layout = QHBoxLayout()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search products...")
        self.search_box.textChanged.connect(self.filter_inventory)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_inventory)
        
        export_btn = QPushButton("📊 Export")
        export_btn.clicked.connect(self.export_inventory)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        
        controls_layout.addWidget(self.search_box)
        controls_layout.addWidget(refresh_btn)
        controls_layout.addWidget(export_btn)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Product Name", "Stock Quantity", "Unit Price", "Total Value", "Status"])
        
        # Make table read-only
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Product name stretches
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Stock quantity
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Unit price
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Total value
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Status
        
        # Summary label
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            color: #2c3e50;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
        """)
        
        layout.addWidget(title)
        layout.addLayout(controls_layout)
        layout.addWidget(self.table)
        layout.addWidget(self.summary_label)
        
        self.setLayout(layout)
    
    def load_inventory(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, stock_quantity, unit_price, 
                       (stock_quantity * unit_price) as total_value
                FROM products 
                ORDER BY name
            """)
            products = cursor.fetchall()
            conn.close()
            
            self.table.setRowCount(len(products))
            
            total_products = len(products)
            total_value = 0
            out_of_stock = 0
            low_stock = 0
            
            for row, (name, stock, price, total_value_item) in enumerate(products):
                # Product name
                self.table.setItem(row, 0, QTableWidgetItem(name))
                
                # Stock quantity
                stock_item = QTableWidgetItem(str(stock))
                stock_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 1, stock_item)
                
                # Unit price
                price_item = QTableWidgetItem(f"Rs.{price:.2f}")
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, 2, price_item)
                
                # Total value
                value_item = QTableWidgetItem(f"Rs.{total_value_item:.2f}")
                value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, 3, value_item)
                
                # Status based on stock level
                if stock == 0:
                    status = "Out of Stock"
                    color = QColor("#e74c3c")  # Red
                    out_of_stock += 1
                elif stock < 10:
                    status = "Low Stock"
                    color = QColor("#f39c12")  # Orange
                    low_stock += 1
                else:
                    status = "In Stock"
                    color = QColor("#27ae60")  # Green
                
                status_item = QTableWidgetItem(status)
                status_item.setTextAlignment(Qt.AlignCenter)
                status_item.setForeground(QColor("white"))
                status_item.setBackground(color)
                self.table.setItem(row, 4, status_item)
                
                total_value += total_value_item
            
            # Update summary
            self.update_summary(total_products, total_value, out_of_stock, low_stock)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load inventory: {str(e)}")
    
    def update_summary(self, total_products, total_value, out_of_stock, low_stock):
        """Update the summary label with inventory statistics"""
        in_stock = total_products - out_of_stock - low_stock
        
        summary_text = f"""
        📊 Summary: {total_products} Products | Total Value: Rs.{total_value:.2f} | 
        ✅ In Stock: {in_stock} | ⚠️ Low Stock: {low_stock} | ❌ Out of Stock: {out_of_stock}
        """.strip()
        
        self.summary_label.setText(summary_text)
    
    def filter_inventory(self):
        """Filter inventory based on search text"""
        search_text = self.search_box.text().lower()
        visible_rows = 0
        
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)  # Product name column
            if item:
                should_show = search_text in item.text().lower()
                self.table.setRowHidden(row, not should_show)
                if should_show:
                    visible_rows += 1
        
        # Update search status
        if search_text:
            self.setWindowTitle(f"Inventory Management - {visible_rows} products found")
        else:
            self.setWindowTitle("Inventory Management")
    
    def export_inventory(self):
        """Export inventory to CSV (placeholder for now)"""
        try:
            import csv
            from PyQt5.QtWidgets import QFileDialog
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Inventory", "inventory.csv", "CSV Files (*.csv)"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    
                    # Write header
                    headers = []
                    for col in range(self.table.columnCount()):
                        headers.append(self.table.horizontalHeaderItem(col).text())
                    writer.writerow(headers)
                    
                    # Write data
                    for row in range(self.table.rowCount()):
                        if not self.table.isRowHidden(row):
                            row_data = []
                            for col in range(self.table.columnCount()):
                                item = self.table.item(row, col)
                                row_data.append(item.text() if item else "")
                            writer.writerow(row_data)
                
                QMessageBox.information(self, "Success", f"Inventory exported to {filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export inventory: {str(e)}")