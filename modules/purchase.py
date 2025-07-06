from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QMessageBox, QComboBox, 
                             QSpinBox, QDoubleSpinBox, QDateEdit, QFormLayout)
from PyQt5.QtCore import QDate
from modules.database import Database

class PurchaseWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Purchase Entry")
        self.setFixedSize(600, 550)  # Increased size
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: Arial, sans-serif;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
                min-height: 20px;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("📦 Purchase Entry")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        
        # Form layout for better organization
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        # Form fields
        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("Enter product name")
        
        self.supplier = QLineEdit()
        self.supplier.setPlaceholderText("Enter supplier name")
        
        self.quantity = QSpinBox()
        self.quantity.setRange(1, 10000)
        self.quantity.setSuffix(" units")
        self.quantity.setValue(1)
        
        self.unit_cost = QDoubleSpinBox()
        self.unit_cost.setRange(0.01, 999999.99)
        self.unit_cost.setPrefix("Rs. ")
        self.unit_cost.setDecimals(2)
        self.unit_cost.setValue(1.00)
        
        self.payment_type = QComboBox()
        self.payment_type.addItems(["Cash", "Credit", "Bank Transfer", "Cheque"])
        
        self.purchase_date = QDateEdit()
        self.purchase_date.setDate(QDate.currentDate())
        self.purchase_date.setCalendarPopup(True)
        
        # Add fields to form layout
        form_layout.addRow("Product Name:", self.product_name)
        form_layout.addRow("Supplier:", self.supplier)
        form_layout.addRow("Quantity:", self.quantity)
        form_layout.addRow("Unit Cost:", self.unit_cost)
        form_layout.addRow("Payment Type:", self.payment_type)
        form_layout.addRow("Purchase Date:", self.purchase_date)
        
        # Calculate total automatically
        self.total_cost = QLabel("Total: Rs. 0.00")
        self.total_cost.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #e74c3c;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
            margin: 10px 0;
        """)
        
        # Connect signals for auto-calculation
        self.quantity.valueChanged.connect(self.calculate_total)
        self.unit_cost.valueChanged.connect(self.calculate_total)
        
        # Calculate initial total
        self.calculate_total()
        
        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        save_btn = QPushButton("💾 Save Purchase")
        save_btn.clicked.connect(self.save_purchase)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.close)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        # Add everything to main layout
        main_layout.addWidget(title)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.total_cost)
        main_layout.addLayout(button_layout)
        main_layout.addStretch()  # Push everything to top
        
        self.setLayout(main_layout)
        
        # Set focus to first field
        self.product_name.setFocus()
    
    def calculate_total(self):
        total = self.quantity.value() * self.unit_cost.value()
        self.total_cost.setText(f"Total: Rs. {total:.2f}")
    
    def save_purchase(self):
        # Validate inputs
        if not self.product_name.text().strip():
            QMessageBox.warning(self, "Error", "Please enter product name")
            return
        
        if not self.supplier.text().strip():
            QMessageBox.warning(self, "Error", "Please enter supplier name")
            return
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Check if product exists, if not create it
            cursor.execute("SELECT id FROM products WHERE name = ?", (self.product_name.text().strip(),))
            product = cursor.fetchone()
            
            if not product:
                cursor.execute("""
                    INSERT INTO products (name, stock_quantity, unit_price) 
                    VALUES (?, ?, ?)
                """, (self.product_name.text().strip(), 0, self.unit_cost.value()))
                product_id = cursor.lastrowid
            else:
                product_id = product[0]
            
            # Insert purchase record
            total_cost = self.quantity.value() * self.unit_cost.value()
            cursor.execute("""
                INSERT INTO purchases (product_id, supplier, quantity, unit_cost, total_cost, payment_type, purchase_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (product_id, self.supplier.text().strip(), self.quantity.value(), 
                  self.unit_cost.value(), total_cost, self.payment_type.currentText(),
                  self.purchase_date.date().toString("yyyy-MM-dd")))
            
            # Update product stock
            cursor.execute("""
                UPDATE products 
                SET stock_quantity = stock_quantity + ?, unit_price = ?
                WHERE id = ?
            """, (self.quantity.value(), self.unit_cost.value(), product_id))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Success", "Purchase record saved successfully!")
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save purchase: {str(e)}")