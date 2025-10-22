# ⚙️ Modbus Hub

<p align="center">
  <img src="assets/icons/master/icon_master.png" alt="Master Logo" width="120" style="margin-right: 20px;"/>
  <img src="assets/icons/slave/icon_slave.png" alt="Slave Logo" width="120"/>
</p>

<h3 align="center">
  <span id="typewriter"></span>
</h3>

---

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-00ff99?style=for-the-badge&logo=python"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-00ff99?style=for-the-badge"/>
</p>

---

## 🧠 Overview

**Modbus Hub** is a professional and educational **Modbus TCP simulator**,  
featuring two standalone GUI applications built with **PySide6 (Qt for Python)** and **pymodbusTCP**.

- 🟦 **MasterApp (Client)** – connects to a Modbus TCP server, reads/writes registers in real time.
- 🟩 **SlaveApp (Server)** – simulates a Modbus TCP device with editable holding registers.

---

## 🧩 Key Features

| Component                  | Features                                                                                                            |
|----------------------------|---------------------------------------------------------------------------------------------------------------------|
| 🟦 **MasterApp**           | Connect to Modbus TCP servers, read/write holding registers, define ranges, live refresh, connection LED, log panel |
| 🟩 **SlaveApp**            | Simulated Modbus TCP server, editable registers, IP/Port configuration, live sync, server status LED, message log   |
| 🧱 **Shared Architecture** | Modular structure, full input validation, friendly GUI built with PySide6                                           |
| 🧮 **Protocol Compliance** | Supports 65,536 registers, 125 registers per Modbus frame (standard limit)                                          |

---

## ⚙️ Installation

```bash
pip install pyside6 pymodbusTCP
git clone https://github.com/jcespitia/modbus-hub.git
cd modbus-hub
```

---

## ▶️ Usage

```bash
python slave/slave_app.py
python master/master_app.py
```

---

## 📊 Register Model

| Parameter             | Range / Limit                        |
|-----------------------|--------------------------------------|
| Address Space         | 0 – 65535                            |
| Registers per request | ≤ 125                                |
| Function Codes        | 03 (Read Holding), 06 (Write Single) |
| Data Type             | Unsigned 16-bit integer              |

---

## 💾 Downloads

| Platform   | File                                                                        | Description           |
|------------|-----------------------------------------------------------------------------|-----------------------|
| 🪟 Windows | [modbus-hub-win64.exe](https://github.com/jcespitia/modbus-hub/releases)    | Standalone executable |
| 🐧 Linux   | [modbus-hub-linux.tar.gz](https://github.com/jcespitia/modbus-hub/releases) | Binary build          |
| 💻 Source  | [GitHub Repository](https://github.com/jcespitia/modbus-hub)                | Full source code      |

---

## 🧠 Developer Notes

- Modular, documented, and educational design.
- GUI is non-blocking — uses `QTimer`.
- Master and Slave can run on same or separate machines.
- Ideal for **testing and integration development**.

---

## 📈 Roadmap

- [ ] Register type selector
- [ ] Data persistence
- [ ] Export logs to `.txt`
- [ ] Activity LED (blinking)
- [ ] Auto-detect local IP
- [ ] Dark/Light theme toggle

---

## 📜 License

MIT License — free for educational and commercial use with attribution.

---

## 📬 Contact

👨‍💻 **Author:** Camilo Espitia  
🌐 [GitHub](https://github.com/jcespitia)

---

<pre><code>
[ OK ] Documentation loaded successfully – Modbus Hub v1.0.0
</code></pre>

---

<!-- 🧠 Hacker Theme Custom CSS -->
<style>
body {
  background-color: #0d0d0d;
  color: #00ff99;
  font-family: 'Courier New', monospace;
}
a { color: #00ff99; text-decoration: none; }
a:hover { text-decoration: underline; }
code, pre {
  background-color: #111;
  color: #00ff99;
  padding: 6px 10px;
  border-radius: 8px;
  display: block;
}
table {
  border: 1px solid #00ff99;
  border-collapse: collapse;
  width: 100%;
}
th, td {
  border: 1px solid #00ff99;
  padding: 6px 10px;
}
img {
  filter: drop-shadow(0 0 10px #00ff99);
}
</style>

<script>
const text = "💀 Modbus Hub – Modbus TCP Simulator (Master & Slave)";
let i = 0;
function typing() {
  if (i < text.length) {
    document.getElementById("typewriter").innerHTML += text.charAt(i);
    i++;
    setTimeout(typing, 80);
  }
}
typing();
</script>