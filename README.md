# ⚙️ Modbus Hub  
### Simulador completo de Modbus TCP con interfaz gráfica (Maestro y Esclavo)

> **Tecnologías:** Python 3.10+, **PySide6** (Qt for Python), **pymodbusTCP**, **uv** (gestor de entornos y paquetes)  
> **Alcance:** Solo **Modbus TCP** (sin RTU en esta versión).  

📘 [**Documentación Web (GitHub Pages)**](https://jcespitia.github.io/modbus-hub/)  
⬇️ [**Descargar última versión**](https://github.com/jcespitia/modbus-hub/releases/latest)

---

## 🧠 Descripción general

**Modbus Hub** es un simulador didáctico y práctico de **Modbus TCP**. Incluye dos aplicaciones gráficas independientes desarrolladas con **PySide6**:

- 🟦 **Modbus Master (Cliente)** — se conecta a un servidor Modbus TCP y **lee** y **escribe** registros en tiempo real.  
- 🟩 **Modbus Slave (Servidor)** — simula un dispositivo Modbus TCP con registros editables y actualizaciones en vivo.

Está diseñado para **pruebas, desarrollo, QA, educación** y demostraciones rápidas. Cumple con las limitaciones del protocolo (por ejemplo, **125 registros por solicitud**) y ofrece una interfaz limpia y responsiva con **indicadores LED** y un **registro de mensajes**.

---

## 🧩 Características

### Master (Cliente)
- ✅ Cliente **Modbus TCP** basado en `pymodbusTCP.client.ModbusClient`.
- 🔁 Lecturas periódicas (por defecto cada **2 s**) de registros holding.
- ✍️ Soporte para **escritura de un solo registro**.
- 🎛️ Parámetros configurables: **Dirección IP**, **Puerto**, **Unit ID**, **Dirección inicial**, **Cantidad** (ventana de lectura).
- 🧮 Interfaz sensible a rangos: máximo **125** registros por lectura; direcciones **0–65535**.
- 🧱 Diseño de cuadrícula dinámica: **10 filas** por bloque, 2 columnas (`Address`/`Value`), expandible horizontalmente.
- 🟢/🔴 **LED** indicador de conexión + **registro de mensajes** con marcas de tiempo.
- 🛡️ **Validaciones y ventanas emergentes** para errores (IP/puerto/unidad/rango/valor).

### Slave (Servidor)
- ✅ Servidor **Modbus TCP** basado en `pymodbusTCP.server.ModbusServer` (hilo no bloqueante).
- 🌐 **Configuración de IP** (por ejemplo, `0.0.0.0` para todas las interfaces) y **Puerto** personalizable.
- 🧮 Simula **65,536 registros holding** (espacio completo de direcciones) accesibles mediante vistas por ventana (≤ **125** simultáneos).
- ✍️ Tabla editable en la interfaz con **bloqueo temporal al editar**.
- 🔁 Actualización periódica de la UI (**1 s**) sincronizada con las escrituras del Maestro.
- 🟢/🔴 **LED** de estado del servidor + **registro de mensajes** con hora.
- 🛡️ **Validaciones y ventanas emergentes** para IP/puerto/rango/valor.

> El esclavo mantiene un objeto compartido **DataBank** pasado al `ModbusServer`, garantizando la sincronización entre los cambios en la GUI y las solicitudes del cliente.

---

## 🧱 Estructura del proyecto

```
modbus-hub/
│
├── master/
│   ├── master_app.py        # Interfaz del Maestro Modbus (solo TCP, validaciones, LED, log)
│   └── modbus_master.py     # Cliente TCP (lectura/escritura/conexión/desconexión)
│
├── slave/
│   ├── slave_app.py         # Interfaz del Esclavo Modbus (IP+puerto, tabla editable, LED, log)
│   └── modbus_slave.py      # Servidor TCP + gestión del DataBank (65,536 registros)
│
├── shared/
│   └── utils.py             # Funciones compartidas (logs, utilidades, etc.)
│
└── README.md                # Este archivo
```

---

## ⚙️ Instalación (con **uv**)

Este proyecto usa [**uv**](https://github.com/astral-sh/uv) para crear entornos reproducibles de forma rápida.  
También puedes usar un entorno virtual estándar con `python -m venv`, pero **uv** es recomendado.

### 1️⃣ Instalar `uv`
```bash
# Opción A: vía pip
pip install uv

# Opción B: instalador oficial
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2️⃣ Crear entorno virtual e instalar dependencias
Desde la raíz del proyecto (`modbus-hub/`):
```bash
uv sync
```

Activar el entorno (si no usas `uv run`):
- **Windows**
  ```bash
  .venv\Scripts\activate
  ```
- **Linux/macOS**
  ```bash
  source .venv/bin/activate
  ```

> **Dependencias:** `PySide6`, `pymodbusTCP`.  
> **Sin** `minimalmodbus` en esta versión.

---

## ▶️ Ejecución

### 🟩 Iniciar el Esclavo (Servidor)
```bash
uv run python slave/slave_app.py
```
- Elige la **IP** (ej. `0.0.0.0`) y el **Puerto** (ej. `502` o `1502` sin permisos de admin/root).
- Haz clic en **Start Server** → el LED se enciende 🟢 y el log muestra el punto de enlace.

### 🟦 Iniciar el Maestro (Cliente)
```bash
uv run python master/master_app.py
```
- Ingresa la **IP** y **Puerto** del esclavo, luego haz clic en **Connect**.
- El LED se enciende 🟢 y las lecturas se realizan cada 2 segundos.

> Si tu entorno ya está activo, puedes usar simplemente `python` en lugar de `uv run python`.

---

## 💡 Flujo de uso típico

1. Ejecuta **SlaveApp** → `0.0.0.0:502` → **Start Server**.  
2. Ejecuta **MasterApp** → conéctate a `127.0.0.1:502`.  
3. Define el rango de registros (**Start/Quantity**, ≤125).  
4. Edita valores en el Esclavo o escribe desde el Maestro: los cambios se reflejan en ambos.  
5. Puedes detener/reiniciar el servidor; la cuadrícula se ajusta automáticamente.

---

## 🧮 Modelo y límites de registros

- Espacio de direcciones: **0–65535**  
- Límite por solicitud: **≤ 125 registros**  
- Lectura (Maestro): `read_holding_registers(start, count)`  
- Escritura (Maestro): `write_single_register(address, value)`  
- El Esclavo usa una única instancia de **DataBank** compartida con el servidor, evitando inconsistencias.

---

## 🧰 Validación y experiencia de usuario

Ambas aplicaciones incluyen validaciones estrictas con **QMessageBox** para mostrar errores:

| Campo | Regla o Rango |
|---|---|
| Dirección IP | Formato IPv4 válido (`192.168.0.10`, `0.0.0.0`) |
| Puerto | `1–65535` |
| Unit ID (Maestro) | `1–247` |
| Dirección inicial | `0–65535` |
| Cantidad | `1–125` (se ajusta automáticamente) |
| Valor del registro | `0–65535` |

**Seguridad al editar (Esclavo):** la actualización automática se pausa durante la edición de celdas, evitando que el texto ingresado desaparezca.

---

## 🖥️ Diseño de la interfaz (GUI)

- **Indicador LED** + estado textual (“Conectado/Desconectado”, “Ejecutando/Detenido”).  
- **Cuadrícula dinámica**: 10 filas por bloque, columnas `Address` y `Value`.  
- **Registro de mensajes** (`QTextEdit`) con hora y desplazamiento automático.  
- **Campos de formulario** con validación integrada.

---

## 🌐 Enlaces útiles

- 🌍 **Documentación web:** [https://jcespitia.github.io/modbus-hub/](https://jcespitia.github.io/modbus-hub/)
- 📦 **Releases / Ejecutables:** [https://github.com/jcespitia/modbus-hub/releases](https://github.com/jcespitia/modbus-hub/releases)
- 🧩 **Código fuente:** [https://github.com/jcespitia/modbus-hub](https://github.com/jcespitia/modbus-hub)

---

## 🗺️ Roadmap / Ideas futuras

- Selector de tipo de registros: **Holding / Input / Coils / Discrete Inputs**.  
- Persistencia: guardar/cargar estado (JSON / CSV).  
- LED de actividad para lecturas/escrituras activas.  
- Detección automática de IP local.  
- Exportar logs a archivo.  
- Modo **RTU** opcional (con `minimalmodbus`).  
- Temas visuales (claro/oscuro, estilo SCADA).

---

## 📄 Licencia

**Licencia MIT** — uso libre para educación, pruebas o proyectos comerciales con atribución.  
Desarrollado por **Camilo Espitia** 💻  
