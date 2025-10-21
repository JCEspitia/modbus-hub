import sys
import re
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QHBoxLayout,
    QMessageBox, QTextEdit, QFrame
)
from PySide6.QtCore import QTimer, Qt
from slave.modbus_slave import ModbusSlaveServer


class SlaveApp(QWidget):
    """Servidor Modbus TCP con IP configurable, LED de estado y panel de mensajes."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modbus Hub - Slave Server")
        self.setGeometry(300, 200, 900, 600)

        # Servidor
        self.server = None
        self.start_addr = 0
        self.quantity = 10

        # Campos de configuración
        self.ip_input = QLineEdit("0.0.0.0")
        self.port_input = QLineEdit("502")
        self.start_input = QLineEdit("0")
        self.qty_input = QLineEdit("10")

        self.start_button = QPushButton("Start Server")

        # LED indicador
        self.status_label = QLabel("Status: Stopped")
        self.status_led = QFrame()
        self.status_led.setFixedSize(16, 16)
        self.status_led.setStyleSheet("background-color: red; border-radius: 8px;")

        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.status_led)
        status_layout.addStretch()

        # Tabla
        self.table = QTableWidget()
        self.refresh_table_layout()

        # Cuadro de mensajes
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMinimumHeight(120)
        self.log_box.setStyleSheet("background-color: #111; color: #0f0; font-family: monospace;")

        # Layout de rango
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("Start:"))
        range_layout.addWidget(self.start_input)
        range_layout.addWidget(QLabel("Quantity:"))
        range_layout.addWidget(self.qty_input)

        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(QLabel("IP Address:"))
        layout.addWidget(self.ip_input)
        layout.addWidget(QLabel("Port:"))
        layout.addWidget(self.port_input)
        layout.addLayout(range_layout)
        layout.addWidget(self.start_button)
        layout.addLayout(status_layout)
        layout.addWidget(self.table)
        layout.addWidget(QLabel("Messages:"))
        layout.addWidget(self.log_box)
        self.setLayout(layout)

        # Conexiones
        self.start_button.clicked.connect(self.toggle_server)
        self.table.cellChanged.connect(self.handle_cell_change)
        self.start_input.editingFinished.connect(self.update_range)
        self.qty_input.editingFinished.connect(self.update_range)
        self.table.cellClicked.connect(self.pause_refresh)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_table)
        self.timer.start(1000)

        self._updating = False
        self._editing = False

    # ------------------------------------------------
    # Logging interno
    # ------------------------------------------------
    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.append(f"[{timestamp}] {msg}")
        self.log_box.verticalScrollBar().setValue(self.log_box.verticalScrollBar().maximum())

    # ------------------------------------------------
    # Validaciones
    # ------------------------------------------------
    def validate_ip(self, ip_text):
        """Valida formato de IP."""
        pattern = r"^(?:\d{1,3}\.){3}\d{1,3}$"
        if not re.match(pattern, ip_text.strip()):
            QMessageBox.warning(self, "Invalid IP", "Please enter a valid IP address (e.g., 192.168.0.10 or 0.0.0.0).")
            return None
        return ip_text.strip()

    # ------------------------------------------------
    # Configuración del rango
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
        """Reconstruye la tabla de registros."""
        self._updating = True
        cols_needed = ((self.quantity - 1) // 10 + 1) * 2
        self.table.setColumnCount(cols_needed)
        self.table.setRowCount(10)
        headers = []
        for i in range(0, cols_needed, 2):
            block = i // 2
            headers.extend([f"Address {block+1}", f"Value {block+1}"])
        self.table.setHorizontalHeaderLabels(headers)

        if self.server:
            values = self.server.read_window(self.start_addr, self.quantity)
        else:
            values = [0] * self.quantity

        for i in range(self.quantity):
            addr = self.start_addr + i
            col_block = (i // 10) * 2
            row = i % 10
            self.table.setItem(row, col_block, QTableWidgetItem(str(addr)))
            val_item = QTableWidgetItem(str(values[i]))
            val_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, col_block + 1, val_item)
        self._updating = False

    # ------------------------------------------------
    # LED indicador
    # ------------------------------------------------
    def set_led(self, color):
        self.status_led.setStyleSheet(f"background-color: {color}; border-radius: 8px;")

    # ------------------------------------------------
    # Control del servidor
    # ------------------------------------------------
    def toggle_server(self):
        """Inicia o detiene el servidor Modbus TCP."""
        if not self.server or not getattr(self.server, "running", False):
            ip = self.validate_ip(self.ip_input.text())
            if not ip:
                return
            try:
                port = int(self.port_input.text())
                if port < 1 or port > 65535:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Invalid Port", "Port must be between 1 and 65535.")
                return

            self.server = ModbusSlaveServer(host=ip, port=port)
            self.server.start()
            self.status_label.setText("Status: Running")
            self.set_led("green")
            self.start_button.setText("Stop Server")
            self.refresh_table_layout()
            self.log(f"Server started at {ip}:{port}.")
        else:
            self.server.stop()
            self.status_label.setText("Status: Stopped")
            self.set_led("red")
            self.start_button.setText("Start Server")
            self.refresh_table_layout()
            self.log("Server stopped.")

    # ------------------------------------------------
    # Actualización periódica
    # ------------------------------------------------
    def refresh_table(self):
        if not self.server or not getattr(self.server, "running", False) or self._editing:
            return
        self._updating = True
        values = self.server.read_window(self.start_addr, self.quantity)
        for i in range(self.quantity):
            col_block = (i // 10) * 2
            row = i % 10
            val_item = QTableWidgetItem(str(values[i]))
            val_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, col_block + 1, val_item)
        self._updating = False

    # ------------------------------------------------
    # Edición manual
    # ------------------------------------------------
    def pause_refresh(self):
        self._editing = True
        self.timer.stop()

    def handle_cell_change(self, row, column):
        if self._updating or not self.server or not getattr(self.server, "running", False):
            return
        if column % 2 == 1:
            try:
                new_value = int(self.table.item(row, column).text())
                if new_value < 0 or new_value > 65535:
                    raise ValueError
                addr = self.start_addr + (column // 2) * 10 + row
                self.server.update_register(addr, new_value)
                self.log(f"Register {addr} updated -> {new_value}")
            except ValueError:
                QMessageBox.warning(self, "Invalid Value", "Register value must be between 0–65535.")
        self._editing = False
        self.timer.start(1000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SlaveApp()
    window.show()
    sys.exit(app.exec())
