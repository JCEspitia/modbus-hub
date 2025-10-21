from pyModbusTCP.client import ModbusClient
from shared.utils import log


class ModbusMasterClient:
    """Cliente Modbus TCP (solo TCP, sin soporte RTU)."""

    def __init__(self, host="127.0.0.1", port=502, unit_id=1):
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.client = None

    def connect(self):
        """Conecta al servidor Modbus TCP."""
        try:
            self.client = ModbusClient(host=self.host, port=self.port, unit_id=self.unit_id, auto_open=True)
            log(f"Connecting via TCP to {self.host}:{self.port}")
            return self.client.open()
        except Exception as e:
            log(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Desconecta del servidor."""
        if self.client:
            try:
                self.client.close()
                log("Disconnected from Modbus server.")
            except Exception as e:
                log(f"Error during disconnect: {e}")

    def read_registers(self, start_addr=0, count=10):
        """Lee registros holding (máximo 125)."""
        try:
            if count > 125:
                count = 125
            values = self.client.read_holding_registers(start_addr, count)
            if values:
                log(f"Read successful: {values}")
                return values
            else:
                log("Read returned no data.")
        except Exception as e:
            log(f"Read error: {e}")
        return None

    def write_register(self, address, value):
        """Escribe un valor en un holding register."""
        try:
            ok = self.client.write_single_register(address, value)
            if ok:
                log(f"Write successful: Address={address}, Value={value}")
                return True
            else:
                log(f"Write failed at address {address}")
        except Exception as e:
            log(f"Write error: {e}")
        return False
