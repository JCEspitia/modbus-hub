import datetime

def log(message: str):
    """Registrar mensajes con timestamp en consola."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {message}")
