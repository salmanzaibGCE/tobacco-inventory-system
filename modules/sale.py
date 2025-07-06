from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QMessageBox, QComboBox, 
                             QSpinBox, QDoubleSpinBox, QDateEdit, QFormLayout)
from PyQt5.QtCore import QDate
from modules.database import Database

class SaleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Sale Entry")
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
                background-color: #e74c3c;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("💰 Sale Entry")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        
        # Form layout for better organization
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        # Form fields
        self.product_combo = QComboBox()
        self.product_combo.setEditable(True)
        self.product_combo.setPlaceholderText("Select or enter product name")
        self.load_products()
        
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Enter customer name")
        
        self.quantity = QSpinBox()
        self.quantity.setRange(1, 10000)
        self.quantity.setSuffix(" units")
        self.quantity.setValue(1)
        
        self.unit_price = QDoubleSpinBox()
        self.unit_price.setRange(0.01, 999999.99)
        self.unit_price.setPrefix("Rs. ")
        self.unit_price.setDecimals(2)
        self.unit_price.setValue(1.00)
        
        self.payment_type = QComboBox()
        self.payment_type.addItems(["Cash", "Credit", "Bank Transfer", "UPI"])
        
        self.sale_date = QDateEdit()
        self.sale_date.setDate(QDate.currentDate())
        self.sale_date.setCalendarPopup(True)
        
        # Add fields to form layout
        form_layout.addRow("Product:", self.product_combo)
        form_layout.addRow("Customer Name:", self.customer_name)
        form_layout.addRow("Quantity:", self.quantity)
        form_layout.addRow("Unit Price:", self.unit_price)
        form_layout.addRow("Payment Type:", self.payment_type)
        form_layout.addRow("Sale Date:", self.sale_date)
        
        # Calculate total automatically
        self.total_amount = QLabel("Total: Rs. 0.00")
        self.total_amount.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #27ae60;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
            margin: 10px 0;
        """)
        
        # Connect signals for auto-calculation
        self.quantity.valueChanged.connect(self.calculate_total)
        self.unit_price.valueChanged.connect(self.calculate_total)
        self.product_combo.currentTextChanged.connect(self.load_product_price)
        
        # Calculate initial total
        self.calculate_total()
        
        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        save_btn = QPushButton("💾 Save Sale")
        save_btn.clicked.connect(self.save_sale)
        
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
        main_layout.addWidget(self.total_amount)
        main_layout.addLayout(button_layout)
        main_layout.addStretch()  # Push everything to top
        
        self.setLayout(main_layout)
        
        # Set focus to first field
        self.product_combo.setFocus()
    
    def load_products(self):
        """Load existing products into combo box"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM products ORDER BY name")
            products = cursor.fetchall()
            
            self.product_combo.clear()
            for product in products:
                self.product_combo.addItem(product[0])
            
            conn.close()
        except Exception as e:
            print(f"Error loading products: {e}")
    
    def load_product_price(self):
        """Load product price when product is selected"""
        product_name = self.product_combo.currentText()
        if not product_name:
            return
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT unit_price FROM products WHERE name = ?", (product_name,))
            result = cursor.fetchone()
            
            if result:
                self.unit_price.setValue(result[0])
            
            conn.close()
        except Exception as e:
            print(f"Error loading product price: {e}")
    
    def calculate_total(self):
        total = self.quantity.value() * self.unit_price.value()
        self.total_amount.setText(f"Total: Rs. {total:.2f}")
    
    def save_sale(self):
        # Validate inputs
        if not self.product_combo.currentText().strip():
            QMessageBox.warning(self, "Error", "Please select or enter product name")
            return
        
        if not self.customer_name.text().strip():
            QMessageBox.warning(self, "Error", "Please enter customer name")
            return
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Check if product exists
            product_name = self.product_combo.currentText().strip()
            cursor.execute("SELECT id, stock_quantity FROM products WHERE name = ?", (product_name,))
            product = cursor.fetchone()
            
            if not product:
                QMessageBox.warning(self, "Error", "Product not found. Please add it through Purchase Entry first.")
                return
            
            product_id, current_stock = product
            
            # Check if enough stock available
            if current_stock < self.quantity.value():
                QMessageBox.warning(self, "Error", f"Insufficient stock. Available: {current_stock} units")
                return
            
            # Insert sale record
            total_amount = self.quantity.value() * self.unit_price.value()
            cursor.execute("""
                INSERT INTO sales (product_id, customer_name, quantity, unit_price, total_amount, payment_type, sale_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (product_id, self.customer_name.text().strip(), self.quantity.value(), 
                  self.unit_price.value(), total_amount, self.payment_type.currentText(),
                  self.sale_date.date().toString("yyyy-MM-dd")))
            
            # Update product stock
            cursor.execute("""
                UPDATE products 
                SET stock_quantity = stock_quantity - ?
                WHERE id = ?
            """, (self.quantity.value(), product_id))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Success", "Sale record saved successfully!")
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save sale: {str(e)}")