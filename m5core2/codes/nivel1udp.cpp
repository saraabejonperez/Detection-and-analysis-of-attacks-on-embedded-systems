#include <M5Core2.h>
#include <WiFi.h>
#include <WiFiUdp.h>

/* ========= CONFIGURACIÓN WIFI ========= */
const char* WIFI_SSID = "WiFi";
const char* WIFI_PASS = "contraseña";

/* ========= CONFIGURACIÓN UDP ========= */
const int UDP_PORT = 9999;
WiFiUDP udp;

/* ========= BUFFER PANTALLA ========= */
String lines[12];
int lineIndex = 0;

/* ========= MOSTRAR FLUJO RECIBIDO ========= */
void addLine(const String& msg) {
  lines[lineIndex] = msg;
  lineIndex = (lineIndex + 1) % 12;

  M5.Lcd.fillScreen(BLACK);
  M5.Lcd.setCursor(0, 0);
  M5.Lcd.setTextColor(GREEN);
  M5.Lcd.setTextSize(2);

  for (int i = 0; i < 12; i++) {
    int idx = (lineIndex + i) % 12;
    M5.Lcd.println(lines[idx]);
  }
}

/* ========= SETUP ========= */
void setup() {
  M5.begin();
  M5.Lcd.fillScreen(BLACK);
  M5.Lcd.setTextSize(2);
  M5.Lcd.setTextColor(GREEN);

  addLine("M5Stack UDP Flow");
  addLine("Conectando WiFi...");

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  addLine("WiFi OK");
  addLine("IP: " + WiFi.localIP().toString());

  udp.begin(UDP_PORT);
  addLine("UDP escuchando:");
  addLine("Puerto " + String(UDP_PORT));
  addLine("----------------");
}

/* ========= LOOP ========= */
void loop() {
  int packetSize = udp.parsePacket();
  if (packetSize) {
    char buffer[256];
    int len = udp.read(buffer, sizeof(buffer) - 1);
    if (len > 0) {
      buffer[len] = 0;
    }

    String msg = String(buffer);

    // Formato visual:
    // [IP_origen] mensaje
    String line = udp.remoteIP().toString() + " | " + msg;
    addLine(line);
  }

  delay(10);
}