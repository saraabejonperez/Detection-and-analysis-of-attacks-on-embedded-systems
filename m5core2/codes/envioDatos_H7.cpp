#include <WiFi.h>
#include <ArduinoJson.h>

/* ─────────────────────────────────────────────────── */
/* ========= CÓDIGO PARA ARDUINO PORTENTA H7 ========= */
/* ─────────────────────────────────────────────────── */

/* ========= CONFIG WIFI ========= */
const char* ssid     = "MotoG(4)9983";
const char* password = "162a63f763c0";

/* ========= DESTINO (M5Stack) ========= */
const char* serverIP = "10.211.0.195";
const int   serverPort = 80;

/* ========= PARÁMETROS TRÁFICO ========= */
const int TOTAL_PKTS = 80;
const float MALICIOUS_RATE = 0.6;
const int INTERVAL_MS = 150;

WiFiClient client;

/* ========= SETUP ========= */
void setup() {
  Serial.begin(115200);
  delay(1000);

  WiFi.begin(ssid, password);
  Serial.print("Conectando WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n📶 WiFi conectado");
  randomSeed(millis());
}

/* ========= ASIGNAR FLAGS ========= */
String randomFlags(bool malicious) {
  if (malicious) return "SYN";
  const char* flags[] = {"ACK", "PSH,ACK", "SYN,ACK", "FIN,ACK", "RST"};
  return flags[random(0, 5)];
}

/* ========= LOOP ========= */
void loop() {
  for (int i = 0; i < TOTAL_PKTS; i++) {

    bool malicious = (random(0, 100) < MALICIOUS_RATE * 100);

    StaticJsonDocument<256> pkt;
    pkt["timestamp"]   = millis();
    pkt["protocol"]    = "TCP";
    pkt["flags"]       = randomFlags(malicious);
    pkt["length"]      = random(800, 1500);
    pkt["payload_len"] = random(300, 1000);
    pkt["src_ip"]      = malicious ? "192.168.1.120" : "192.168.1.50";
    pkt["dst_ip"]      = serverIP;
    pkt["src_port"]    = random(1024, 65535);
    pkt["dst_port"]    = (random(0, 100) < 20)
                           ? (random(0, 2) ? 23 : 2323)
                           : random(1024, 65535);

    String body;
    serializeJson(pkt, body);

    if (client.connect(serverIP, serverPort)) {
      client.println("POST / HTTP/1.1");
      client.println("Host: M5Stack");
      client.println("Content-Type: application/json");
      client.print("Content-Length: ");
      client.println(body.length());
      client.println();
      client.print(body);
      client.stop();

      char buffer[64];
      snprintf(buffer, sizeof(buffer),
              "#%02d [%s] %s\n",
              i + 1,
              malicious ? "MAL" : "OK",
              pkt["flags"].as<const char*>());

      Serial.println(buffer);
    }

    delay(INTERVAL_MS);
  }

  while (true);
}