from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLabel, QMessageBox,
                             QDateEdit, QComboBox, QHeaderView, QTextEdit)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont
from modules.database import Database
import sqlite3
import os

class ReportsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Reports & Analytics")
        self.setFixedSize(1000, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: Arial, sans-serif;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                gridline-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
                font-family: monospace;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("📊 Reports & Analytics")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        self.report_type = QComboBox()
        self.report_type.addItems(["Sales Report", "Purchase Report", "Stock Report", "Summary Report"])
        
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addDays(-30))
        self.from_date.setCalendarPopup(True)
        
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setCalendarPopup(True)
        
        generate_btn = QPushButton("📈 Generate Report")
        generate_btn.clicked.connect(self.generate_report)
        
        export_btn = QPushButton("📄 Export PDF")
        export_btn.clicked.connect(self.export_pdf)
        
        filter_layout.addWidget(QLabel("Report Type:"))
        filter_layout.addWidget(self.report_type)
        filter_layout.addWidget(QLabel("From:"))
        filter_layout.addWidget(self.from_date)
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.to_date)
        filter_layout.addWidget(generate_btn)
        filter_layout.addWidget(export_btn)
        
        # Summary section
        self.summary_text = QTextEdit()
        self.summary_text.setMaximumHeight(150)
        self.summary_text.setReadOnly(True)
        
        # Table for detailed data
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(title)
        layout.addLayout(filter_layout)
        layout.addWidget(QLabel("Summary:"))
        layout.addWidget(self.summary_text)
        layout.addWidget(QLabel("Detailed Data:"))
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
        # Generate initial report
        self.generate_report()
    
    def generate_report(self):
        try:
            report_type = self.report_type.currentText()
            from_date = self.from_date.date().toString("yyyy-MM-dd")
            to_date = self.to_date.date().toString("yyyy-MM-dd")
            
            if report_type == "Sales Report":
                self.generate_sales_report(from_date, to_date)
            elif report_type == "Purchase Report":
                self.generate_purchase_report(from_date, to_date)
            elif report_type == "Stock Report":
                self.generate_stock_report()
            elif report_type == "Summary Report":
                self.generate_summary_report(from_date, to_date)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
            print(f"Debug - Report generation error: {e}")
    
    def generate_sales_report(self, from_date, to_date):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Check if sales table exists and has data
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sales'")
            if not cursor.fetchone():
                # Create empty report if table doesn't exist
                self.create_empty_sales_report(from_date, to_date)
                conn.close()
                return
            
            # Get sales data
            cursor.execute("""
                SELECT s.sale_date, p.name, s.customer_name, s.quantity, 
                       s.unit_price, s.total_amount, s.payment_type
                FROM sales s
                JOIN products p ON s.product_id = p.id
                WHERE s.sale_date BETWEEN ? AND ?
                ORDER BY s.sale_date DESC
            """, (from_date, to_date))
            
            sales_data = cursor.fetchall()
            
            # Calculate summary
            cursor.execute("""
                SELECT COUNT(*), SUM(total_amount), AVG(total_amount)
                FROM sales
                WHERE sale_date BETWEEN ? AND ?
            """, (from_date, to_date))
            
            summary = cursor.fetchone()
            conn.close()
            
            # Update table
            self.table.setColumnCount(7)
            self.table.setHorizontalHeaderLabels(["Date", "Product", "Customer", "Quantity", "Unit Price", "Total", "Payment"])
            self.table.setRowCount(len(sales_data))
            
            for row, data in enumerate(sales_data):
                for col, value in enumerate(data):
                    if col in [4, 5]:  # Price columns
                        self.table.setItem(row, col, QTableWidgetItem(f"Rs.{value:.2f}"))
                    else:
                        self.table.setItem(row, col, QTableWidgetItem(str(value)))
            
            # Update summary
            total_sales = summary[0] if summary[0] else 0
            total_amount = summary[1] if summary[1] else 0
            avg_amount = summary[2] if summary[2] else 0
            
            summary_text = f"""
SALES REPORT SUMMARY ({from_date} to {to_date})
================================================
Total Sales: {total_sales}
Total Revenue: Rs.{total_amount:.2f}
Average Sale Amount: Rs.{avg_amount:.2f}
            """
            self.summary_text.setPlainText(summary_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate sales report: {str(e)}")
            print(f"Debug - Sales report error: {e}")
    
    def create_empty_sales_report(self, from_date, to_date):
        # Create empty table
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Date", "Product", "Customer", "Quantity", "Unit Price", "Total", "Payment"])
        self.table.setRowCount(0)
        
        # Empty summary
        summary_text = f"""
SALES REPORT SUMMARY ({from_date} to {to_date})
================================================
Total Sales: 0
Total Revenue: Rs.0.00
Average Sale Amount: Rs.0.00
Note: No sales data found for the selected period.
        """
        self.summary_text.setPlainText(summary_text)
    
    def generate_purchase_report(self, from_date, to_date):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Check if purchases table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='purchases'")
            if not cursor.fetchone():
                self.create_empty_purchase_report(from_date, to_date)
                conn.close()
                return
            
            # Get purchase data
            cursor.execute("""
                SELECT p.purchase_date, pr.name, p.supplier, p.quantity, 
                       p.unit_cost, p.total_cost, p.payment_type
                FROM purchases p
                JOIN products pr ON p.product_id = pr.id
                WHERE p.purchase_date BETWEEN ? AND ?
                ORDER BY p.purchase_date DESC
            """, (from_date, to_date))
            
            purchase_data = cursor.fetchall()
            
            # Calculate summary
            cursor.execute("""
                SELECT COUNT(*), SUM(total_cost), AVG(total_cost)
                FROM purchases
                WHERE purchase_date BETWEEN ? AND ?
            """, (from_date, to_date))
            
            summary = cursor.fetchone()
            conn.close()
            
            # Update table
            self.table.setColumnCount(7)
            self.table.setHorizontalHeaderLabels(["Date", "Product", "Supplier", "Quantity", "Unit Cost", "Total", "Payment"])
            self.table.setRowCount(len(purchase_data))
            
            for row, data in enumerate(purchase_data):
                for col, value in enumerate(data):
                    if col in [4, 5]:  # Price columns
                        self.table.setItem(row, col, QTableWidgetItem(f"Rs.{value:.2f}"))
                    else:
                        self.table.setItem(row, col, QTableWidgetItem(str(value)))
            
            # Update summary
            total_purchases = summary[0] if summary[0] else 0
            total_cost = summary[1] if summary[1] else 0
            avg_cost = summary[2] if summary[2] else 0
            
            summary_text = f"""
PURCHASE REPORT SUMMARY ({from_date} to {to_date})
==================================================
Total Purchases: {total_purchases}
Total Cost: Rs.{total_cost:.2f}
Average Purchase Cost: Rs.{avg_cost:.2f}
            """
            self.summary_text.setPlainText(summary_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate purchase report: {str(e)}")
            print(f"Debug - Purchase report error: {e}")
    
    def create_empty_purchase_report(self, from_date, to_date):
        # Create empty table
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Date", "Product", "Supplier", "Quantity", "Unit Cost", "Total", "Payment"])
        self.table.setRowCount(0)
        
        # Empty summary
        summary_text = f"""
PURCHASE REPORT SUMMARY ({from_date} to {to_date})
==================================================
Total Purchases: 0
Total Cost: Rs.0.00
Average Purchase Cost: Rs.0.00
Note: No purchase data found for the selected period.
        """
        self.summary_text.setPlainText(summary_text)
    
    def generate_stock_report(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Check if products table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
            if not cursor.fetchone():
                self.create_empty_stock_report()
                conn.close()
                return
            
            # Get stock data
            cursor.execute("""
                SELECT name, stock_quantity, unit_price, 
                       (stock_quantity * unit_price) as stock_value
                FROM products
                ORDER BY stock_quantity ASC
            """)
            
            stock_data = cursor.fetchall()
            
            # Calculate summary
            cursor.execute("""
                SELECT COUNT(*), SUM(stock_quantity), SUM(stock_quantity * unit_price)
                FROM products
            """)
            
            summary = cursor.fetchone()
            conn.close()
            
            # Update table
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["Product", "Stock Quantity", "Unit Price", "Stock Value"])
            self.table.setRowCount(len(stock_data))
            
            for row, data in enumerate(stock_data):
                for col, value in enumerate(data):
                    if col in [2, 3]:  # Price columns
                        self.table.setItem(row, col, QTableWidgetItem(f"Rs.{value:.2f}"))
                    else:
                        self.table.setItem(row, col, QTableWidgetItem(str(value)))
            
            # Update summary
            total_products = summary[0] if summary[0] else 0
            total_stock = summary[1] if summary[1] else 0
            total_value = summary[2] if summary[2] else 0
            
            summary_text = f"""
STOCK REPORT SUMMARY
====================
Total Products: {total_products}
Total Stock Units: {total_stock}
Total Stock Value: Rs.{total_value:.2f}
            """
            self.summary_text.setPlainText(summary_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate stock report: {str(e)}")
            print(f"Debug - Stock report error: {e}")
    
    def create_empty_stock_report(self):
        # Create empty table
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Product", "Stock Quantity", "Unit Price", "Stock Value"])
        self.table.setRowCount(0)
        
        # Empty summary
        summary_text = f"""
STOCK REPORT SUMMARY
====================
Total Products: 0
Total Stock Units: 0
Total Stock Value: Rs.0.00
Note: No products found in inventory.
        """
        self.summary_text.setPlainText(summary_text)
    
    def generate_summary_report(self, from_date, to_date):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Check if required tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('sales', 'purchases', 'products')")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            if not existing_tables:
                self.create_empty_summary_report(from_date, to_date)
                conn.close()
                return
            
            # Initialize default values
            total_sales = sales_revenue = total_purchases = purchase_cost = 0
            total_products = total_stock = 0
            
            # Get sales data if table exists
            if 'sales' in existing_tables:
                cursor.execute("""
                    SELECT COUNT(*), COALESCE(SUM(total_amount), 0)
                    FROM sales WHERE sale_date BETWEEN ? AND ?
                """, (from_date, to_date))
                result = cursor.fetchone()
                total_sales, sales_revenue = result if result else (0, 0)
            
            # Get purchase data if table exists
            if 'purchases' in existing_tables:
                cursor.execute("""
                    SELECT COUNT(*), COALESCE(SUM(total_cost), 0)
                    FROM purchases WHERE purchase_date BETWEEN ? AND ?
                """, (from_date, to_date))
                result = cursor.fetchone()
                total_purchases, purchase_cost = result if result else (0, 0)
            
            # Get product data if table exists
            if 'products' in existing_tables:
                cursor.execute("""
                    SELECT COUNT(*), COALESCE(SUM(stock_quantity), 0)
                    FROM products
                """)
                result = cursor.fetchone()
                total_products, total_stock = result if result else (0, 0)
            
            # Get top selling products if both sales and products tables exist
            top_products = []
            if 'sales' in existing_tables and 'products' in existing_tables:
                cursor.execute("""
                    SELECT p.name, SUM(s.quantity) as total_sold, SUM(s.total_amount) as revenue
                    FROM sales s
                    JOIN products p ON s.product_id = p.id
                    WHERE s.sale_date BETWEEN ? AND ?
                    GROUP BY p.name
                    ORDER BY total_sold DESC
                    LIMIT 5
                """, (from_date, to_date))
                top_products = cursor.fetchall()
            
            conn.close()
            
            # Update table with top products
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["Product", "Units Sold", "Revenue"])
            self.table.setRowCount(len(top_products))
            
            for row, (name, sold, revenue) in enumerate(top_products):
                self.table.setItem(row, 0, QTableWidgetItem(name))
                self.table.setItem(row, 1, QTableWidgetItem(str(sold)))
                self.table.setItem(row, 2, QTableWidgetItem(f"Rs.{revenue:.2f}"))
            
            # Update summary
            profit = sales_revenue - purchase_cost
            profit_margin = (profit/sales_revenue*100) if sales_revenue > 0 else 0
            
            summary_text = f"""
BUSINESS SUMMARY REPORT ({from_date} to {to_date})
==================================================
SALES:
  Total Sales: {total_sales}
  Sales Revenue: Rs.{sales_revenue:.2f}

PURCHASES:
  Total Purchases: {total_purchases}
  Purchase Cost: Rs.{purchase_cost:.2f}

PROFIT/LOSS:
  Gross Profit: Rs.{profit:.2f}
  Profit Margin: {profit_margin:.1f}%

INVENTORY:
  Total Products: {total_products}
  Total Stock: {total_stock} units

TOP SELLING PRODUCTS (shown in table below)
            """
            self.summary_text.setPlainText(summary_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate summary report: {str(e)}")
            print(f"Debug - Summary report error: {e}")
    
    def create_empty_summary_report(self, from_date, to_date):
        # Create empty table
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Product", "Units Sold", "Revenue"])
        self.table.setRowCount(0)
        
        # Empty summary
        summary_text = f"""
BUSINESS SUMMARY REPORT ({from_date} to {to_date})
==================================================
SALES:
  Total Sales: 0
  Sales Revenue: Rs.0.00

PURCHASES:
  Total Purchases: 0
  Purchase Cost: Rs.0.00

PROFIT/LOSS:
  Gross Profit: Rs.0.00
  Profit Margin: 0.0%

INVENTORY:
  Total Products: 0
  Total Stock: 0 units

Note: No data found for the selected period.
        """
        self.summary_text.setPlainText(summary_text)
    
    def export_pdf(self):
        try:
            from fpdf import FPDF
            
            # Create PDF with UTF-8 support
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Add title
            pdf.cell(200, 10, txt=f"{self.report_type.currentText()}", ln=1, align='C')
            pdf.ln(10)
            
            # Add summary - replace currency symbols with "Rs."
            summary_text = self.summary_text.toPlainText()
            summary_lines = summary_text.split('\n')
            
            for line in summary_lines:
                # Replace any currency symbols with Rs.
                clean_line = line.replace('₹', 'Rs.').replace('$', 'Rs.')
                # Ensure the line is not too long
                if len(clean_line) > 80:
                    clean_line = clean_line[:80] + "..."
                try:
                    pdf.cell(200, 8, txt=clean_line, ln=1)
                except UnicodeEncodeError:
                    # If there are still encoding issues, replace problematic characters
                    clean_line = clean_line.encode('ascii', 'ignore').decode('ascii')
                    pdf.cell(200, 8, txt=clean_line, ln=1)
            
            # Create filename
            report_type_clean = self.report_type.currentText().replace(' ', '_').lower()
            date_str = QDate.currentDate().toString('yyyy_MM_dd')
            filename = f"{report_type_clean}_{date_str}.pdf"
            
            # Save PDF
            pdf.output(filename)
            
            # Get absolute path
            abs_path = os.path.abspath(filename)
            QMessageBox.information(self, "Success", f"Report exported successfully!\nSaved as: {abs_path}")
            
        except ImportError:
            QMessageBox.warning(self, "Error", "PDF export requires fpdf2 library.\nInstall with: pip install fpdf2")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export PDF: {str(e)}")
            print(f"Debug - PDF export error: {e}")