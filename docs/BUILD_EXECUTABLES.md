# 🧱 Modbus Hub — Generación de Ejecutables

Este documento explica el proceso para generar los ejecutables (`.exe` y binarios Linux) del proyecto **Modbus Hub**  
utilizando el script automatizado `build_executables.sh`.

---

## 📦 Requisitos previos

### 🔹 En Linux

Asegúrate de tener instaladas las siguientes herramientas:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip wine64 wget zip
```

Verifica que Wine esté funcionando correctamente:

```bash
wine --version
```

🧠 El script usa Wine para compilar los ejecutables de Windows directamente desde Linux, sin necesidad de una máquina
Windows.

---

## ⚙️ Estructura del proyecto

La estructura mínima del proyecto debe ser:

```
modbus-hub/
├── assets/
│   ├── icon.png
│   ├── icon.ico
│   └── ...
├── master/
│   └── master_app.py
├── slave/
│   └── slave_app.py
├── build_executables.sh
└── ...
```

Asegúrate de que `icon.png` y `icon.ico` existan en la carpeta `assets/`.

---

## 🚀 Uso del script

El script `build_executables.sh` genera binarios para Linux y/o Windows, con soporte para versiones.

### 🔧 Comandos básicos

- Generar ambos (Linux + Windows):

```bash
./build_executables.sh
```

Crea:

```
dist/linux/ModbusHubMaster_vDEV
dist/linux/ModbusHubSlave_vDEV
dist/windows/ModbusHubMaster_vDEV.exe
dist/windows/ModbusHubSlave_vDEV.exe
```

- Especificar una versión:

```bash
./build_executables.sh --version 0.1.0
```

Crea los ejecutables con la versión en el nombre y genera los paquetes comprimidos:

```
dist/ModbusHub_Linux_Binaries_v0.1.0.zip
dist/ModbusHub_Windows_Binaries_v0.1.0.zip
```

- Solo Linux:

```bash
./build_executables.sh --linux-only --version 1.0.0
```

- Solo Windows:

```bash
./build_executables.sh --windows-only --version 1.0.0
```

---

## 🧰 Qué hace el script

- Limpia los builds anteriores (`build/` y `dist/`).
- Crea las carpetas necesarias.
- Compila las apps Linux con PyInstaller.
- Si Wine está disponible:
    - Instala (una sola vez) Python 3.11 para Windows dentro de Wine.
    - Instala las dependencias (pyinstaller, pyside6, pymodbusTCP).
    - Compila las apps Windows (`.exe`).
- Empaqueta los resultados en `.zip`:

```
dist/ModbusHub_Linux_Binaries_<versión>.zip
dist/ModbusHub_Windows_Binaries_<versión>.zip
```

---

## 💡 Notas técnicas

- Los binarios de Linux se crean usando PyInstaller nativo.
- Los `.exe` se crean bajo Wine, ejecutando el Python de Windows.
- El script convierte las rutas automáticamente para que funcione en cualquier PC o entorno.
- Se incluyen los plugins de Qt (PySide6) para evitar el error de “Qt platform plugin not found”.

---

## 🧩 Ejemplo completo

1️⃣ Clonar el repositorio:

```bash
git clone https://github.com/tuusuario/modbus-hub.git
cd modbus-hub
```

2️⃣ Dar permisos de ejecución al script:

```bash
chmod +x build_executables.sh
```

3️⃣ Ejecutar con una versión específica:

```bash
./build_executables.sh --version 0.2.0
```

Resultado esperado:

```
dist/
├── linux/
│   ├── ModbusHubMaster_v0.2.0
│   └── ModbusHubSlave_v0.2.0
├── windows/
│   ├── ModbusHubMaster_v0.2.0.exe
│   └── ModbusHubSlave_v0.2.0.exe
├── ModbusHub_Linux_Binaries_v0.2.0.zip
└── ModbusHub_Windows_Binaries_v0.2.0.zip
```

---

## 🧾 Solución de problemas

- ❌ PyInstaller not found for Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pyinstaller
```

- ❌ “Qt platform plugin could not be initialized”:  
  Ya está corregido: el script incluye el plugin de Qt (`qwindows.dll`) automáticamente.

- ❌ “Unable to find assets”:  
  Asegúrate de que la carpeta `assets/` existe y contiene los íconos necesarios.

---

## 🏁 Resultado final

Después de ejecutar el script, tendrás ejecutables listos para distribución:

| Plataforma     | Archivo                                                                               | Descripción           |
|----------------|---------------------------------------------------------------------------------------|-----------------------|
| 🐧 Linux       | ModbusHubMaster_vX.Y.Z / ModbusHubSlave_vX.Y.Z                                        | Ejecutables ELF       |
| 🪟 Windows     | ModbusHubMaster_vX.Y.Z.exe / ModbusHubSlave_vX.Y.Z.exe                                | Ejecutables Windows   |
| 📦 Paquete ZIP | dist/ModbusHub_Linux_Binaries_vX.Y.Z.zip / dist/ModbusHub_Windows_Binaries_vX.Y.Z.zip | Binarios empaquetados |