import psutil
import socket
import time

ESP_IP = "10.211.0.195"
ESP_PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

flows = {}

while True:
    for c in psutil.net_connections(kind='inet'):
        if not c.raddr or not c.pid:
            continue

        key = (c.laddr.ip, c.laddr.port,
               c.raddr.ip, c.raddr.port,
               c.type)

        now = time.time()

        if key not in flows:
            try:
                p = psutil.Process(c.pid)
                io = p.io_counters()
                flows[key] = {
                    "start": now,
                    "tx0": io.write_bytes,
                    "rx0": io.read_bytes,
                }
            except:
                continue

        try:
            p = psutil.Process(c.pid)
            io = p.io_counters()
            tx = io.write_bytes - flows[key]["tx0"]
            rx = io.read_bytes  - flows[key]["rx0"]
            app = p.name()
        except:
            tx = rx = 0
            app = "unknown"

        dur = int((now - flows[key]["start"]) * 1000)

        msg = (
            f"src={c.laddr.ip} sport={c.laddr.port} "
            f"dst={c.raddr.ip} dport={c.raddr.port} "
            f"proto={'TCP' if c.type==socket.SOCK_STREAM else 'UDP'} "
            f"pid={c.pid} app={app} "
            f"tx={tx} rx={rx} dur={dur}"
        )

        sock.sendto(msg.encode(), (ESP_IP, ESP_PORT))

    time.sleep(2)