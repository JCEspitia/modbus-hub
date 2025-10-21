import sys
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QMessageBox, QTextEdit, QFrame
)
from PySide6.QtCore import QTimer, Qt
from master.modbus_master import ModbusMasterClient


class MasterApp(QWidget):
    """Cliente Modbus TCP con LED de estado y cuadro de mensajes."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modbus Hub - Master Client (TCP)")
        self.setGeometry(300, 200, 900, 600)

        self.start_addr = 0
        self.quantity = 10
        self.connected = False
        self.client = None

        # Conexión TCP
        self.ip_input = QLineEdit("127.0.0.1")
        self.port_input = QLineEdit("502")
        self.unit_input = QLineEdit("1")
        self.connect_button = QPushButton("Connect")

        # LED indicador
        self.status_label = QLabel("Status: Disconnected")
        self.status_led = QFrame()
        self.status_led.setFixedSize(16, 16)
        self.status_led.setStyleSheet("background-color: red; border-radius: 8px;")

        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.status_led)
        status_layout.addStretch()

        # Rango
        range_layout = QHBoxLayout()
        self.start_input = QLineEdit("0")
        self.qty_input = QLineEdit("10")
        range_layout.addWidget(QLabel("Start:"))
        range_layout.addWidget(self.start_input)
        range_layout.addWidget(QLabel("Quantity:"))
        range_layout.addWidget(self.qty_input)

        # Tabla
        self.table = QTableWidget()
        self.refresh_table_layout()

        # Escritura
        write_layout = QHBoxLayout()
        self.write_addr = QLineEdit()
        self.write_addr.setPlaceholderText("Address")
        self.write_value = QLineEdit()
        self.write_value.setPlaceholderText("Value")
        self.write_button = QPushButton("Write Register")
        write_layout.addWidget(self.write_addr)
        write_layout.addWidget(self.write_value)
        write_layout.addWidget(self.write_button)

        # Cuadro de mensajes
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMinimumHeight(120)
        self.log_box.setStyleSheet("background-color: #111; color: #0f0; font-family: monospace;")

        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(QLabel("IP Address:"))
        layout.addWidget(self.ip_input)
        layout.addWidget(QLabel("Port:"))
        layout.addWidget(self.port_input)
        layout.addWidget(QLabel("Unit ID:"))
        layout.addWidget(self.unit_input)
        layout.addLayout(range_layout)
        layout.addWidget(self.connect_button)
        layout.addLayout(status_layout)
        layout.addWidget(self.table)
        layout.addLayout(write_layout)
        layout.addWidget(QLabel("Messages:"))
        layout.addWidget(self.log_box)
        self.setLayout(layout)

        # Conexiones
        self.connect_button.clicked.connect(self.toggle_connection)
        self.write_button.clicked.connect(self.write_register_to_slave)
        self.start_input.editingFinished.connect(self.update_range)
        self.qty_input.editingFinished.connect(self.update_range)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_table)

    # ------------------------------------------------
    # Logging visual
    # ------------------------------------------------
    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.append(f"[{timestamp}] {msg}")
        self.log_box.verticalScrollBar().setValue(self.log_box.verticalScrollBar().maximum())

    # ------------------------------------------------
    # LED
    # ------------------------------------------------
    def set_led(self, color):
        self.status_led.setStyleSheet(f"background-color: {color}; border-radius: 8px;")

    # ------------------------------------------------
    # Rango
    # ------------------------------------------------
    def update_range(self):
        try:
            start = int(self.start_input.text())
            qty = int(self.qty_input.text())
            if start < 0 or start >= 65536 or qty < 1 or qty > 125:
                raise ValueError
            if start + qty > 65536:
                qty = 65536 - start
            self.start_addr = start
            self.quantity = qty
            self.refresh_table_layout()
            self.log(f"Range updated: start={start}, qty={qty}")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numeric values.")

    def refresh_table_layout(self):
        cols_needed = ((self.quantity - 1) // 10 + 1) * 2
        self.table.setColumnCount(cols_needed)
        self.table.setRowCount(10)
        headers = []
        for i in range(0, cols_needed, 2):
            block = i // 2
            headers.extend([f"Address {block+1}", f"Value {block+1}"])
        self.table.setHorizontalHeaderLabels(headers)
        for i in range(self.quantity):
            addr = self.start_addr + i
            col_block = (i // 10) * 2
            row = i % 10
            self.table.setItem(row, col_block, QTableWidgetItem(str(addr)))
            self.table.setItem(row, col_block + 1, QTableWidgetItem("0"))

    # ------------------------------------------------
    # Conexión
    # ------------------------------------------------
    def toggle_connection(self):
        if not self.connected:
            self.connect_to_server()
        else:
            self.disconnect_from_server()

    def connect_to_server(self):
        ip = self.ip_input.text().strip()
        try:
            port = int(self.port_input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Port", "Please enter a valid port number.")
            return
        try:
            unit = int(self.unit_input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Unit ID", "Please enter a valid number.")
            return

        self.client = ModbusMasterClient(host=ip, port=port, unit_id=unit)
        if self.client.connect():
            self.connected = True
            self.connect_button.setText("Disconnect")
            self.status_label.setText("Status: Connected")
            self.set_led("green")
            self.timer.start(2000)
            self.log(f"Connected to {ip}:{port}")
        else:
            QMessageBox.warning(self, "Connection Failed", "Could not connect to Modbus server.")
            self.set_led("red")
            self.log("Connection failed.")

    def disconnect_from_server(self):
        if self.client:
            self.client.disconnect()
        self.connected = False
        self.connect_button.setText("Connect")
        self.status_label.setText("Status: Disconnected")
        self.set_led("red")
        self.timer.stop()
        self.log("Disconnected from server.")

    # ------------------------------------------------
    # Lectura periódica
    # ------------------------------------------------
    def update_table(self):
        if not self.connected:
            return
        values = self.client.read_registers(self.start_addr, self.quantity)
        if values:
            for i, val in enumerate(values):
                col_block = (i // 10) * 2
                row = i % 10
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col_block + 1, item)
            self.log(f"Read registers {self.start_addr}–{self.start_addr + len(values) - 1}")
        else:
            self.log("Read error.")


    # ------------------------------------------------
    # Escritura
    # ------------------------------------------------
    def write_register_to_slave(self):
        if not self.connected:
            QMessageBox.warning(self, "Not Connected", "Connect first.")
            return
        try:
            addr = int(self.write_addr.text())
            val = int(self.write_value.text())
            if not (0 <= addr < 65536 and 0 <= val < 65536):
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Address/Value must be between 0–65535.")
            return
        if self.client.write_register(addr, val):
            self.log(f"Write successful: address={addr}, value={val}")
            self.update_table()
        else:
            self.log(f"Write failed at address {addr}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MasterApp()
    window.show()
    sys.exit(app.exec())
