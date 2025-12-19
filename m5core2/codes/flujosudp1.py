import psutil
import socket
import time

ESP_IP = "10.18.127.195"
ESP_PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

flows = {}

while True:
    for c in psutil.net_connections(kind='inet'):
        if not c.raddr or not c.pid:
            continue

        key = (c.laddr.ip, c.laddr.port, c.raddr.ip, c.raddr.port, c.type)

        now = time.time()

        if key not in flows:
            flows[key] = {
                "start": now,
                "tx": 0,
                "rx": 0,
                "pid": c.pid
            }

        # Protección por si desaparecen procesos antes de hacer la llamada a la función psutil.Process(pid)
        try:
            proc = psutil.Process(c.pid)
            name = proc.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            app = "unknown"

        dur = int((now - flows[key]["start"]) * 1000)

        msg = (
            f"src={c.laddr.ip} sport={c.laddr.port} "
            f"dst={c.raddr.ip} dport={c.raddr.port} "
            f"proto={'TCP' if c.type==socket.SOCK_STREAM else 'UDP'} "
            f"state={c.status} pid={c.pid} app={name} "
            f"tx={flows[key]['tx']} rx={flows[key]['rx']} dur={dur}"
        )

        sock.sendto(msg.encode(), (ESP_IP, ESP_PORT))

    time.sleep(2)