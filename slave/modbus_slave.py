from pyModbusTCP.server import ModbusServer, DataBank
import threading
import time
from shared.utils import log


class ModbusSlaveServer:
    """Servidor Modbus TCP con 65536 registros simulados."""

    def __init__(self, host="127.0.0.1", port=502):
        # Crear el DataBank completo (65536 registros)
        self.databank = DataBank()

        # Inicializar 65_536 registros holding en 0
        self.total_registers = 65536
        self.databank.set_holding_registers(0, [0] * self.total_registers)

        # Crear el servidor TCP con este databank
        self.server = ModbusServer(host, port, no_block=True, data_bank=self.databank)

        # Ventana activa (rango visible/modificable)
        self.start_addr = 0
        self.visible_count = 125

        self.running = False
        self._thread = None

    # ------------------------------------------------
    # Control del servidor
    # ------------------------------------------------
    def start(self):
        """Inicia el servidor en hilo separado."""
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._run_server, daemon=True)
        self._thread.start()
        log("Modbus Slave server started.")

    def stop(self):
        """Detiene el servidor."""
        self.running = False
        try:
            self.server.stop()
        except Exception as e:
            log(f"Error stopping server: {e}")
        log("Modbus Slave server stopped.")

    # ------------------------------------------------
    # Loop principal
    # ------------------------------------------------
    def _run_server(self):
        """Bucle principal: mantener la coherencia de los registros."""
        try:
            self.server.start()
            while self.running:
                # Leer ventana visible actual del DataBank (por si el Master modificó algo)
                window = self.databank.get_holding_registers(self.start_addr, self.visible_count)
                if window:
                    # Sincronizar registros activos (se podría expandir en GUI)
                    pass  # Solo lectura pasiva por ahora
                time.sleep(0.5)
        except Exception as e:
            log(f"Server error: {e}")
            self.running = False

    # ------------------------------------------------
    # Actualizar registros (desde GUI del Slave)
    # ------------------------------------------------
    def update_register(self, index, value):
        """Actualiza un registro específico (en todo el espacio de 0–65535)."""
        if 0 <= index < self.total_registers:
            self.databank.set_holding_registers(index, [value])
            log(f"Register {index} updated to {value}")

    # ------------------------------------------------
    # Leer rango
    # ------------------------------------------------
    def read_window(self, start_addr, count):
        """Obtiene un rango de valores para mostrar en GUI."""
        if count > 125:
            count = 125
        if start_addr + count > self.total_registers:
            count = self.total_registers - start_addr
        values = self.databank.get_holding_registers(start_addr, count)
        return values if values else [0] * count
