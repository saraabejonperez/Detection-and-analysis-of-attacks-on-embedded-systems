import psutil
import socket
import time

ESP32_IP = "10.211.0.195"#"10.18.127.195"
ESP32_PORT = 9999

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

seen = set()

while True:
    for c in psutil.net_connections(kind='tcp'):
        if c.raddr and c.laddr:
            flow = (
                c.laddr.ip,
                c.laddr.port,
                c.raddr.ip,
                c.raddr.port
            )

            if flow not in seen:
                seen.add(flow)
                msg = f"{flow[0]} {flow[1]} {flow[2]} {flow[3]} TCP 0"
                udp.sendto(msg.encode(), (ESP32_IP, ESP32_PORT))

    time.sleep(1)