#include <M5Core2.h>
#include <WiFi.h>
#include <WiFiUdp.h>

/* ========= CONFIG WIFI ========= */
const char* WIFI_SSID = "WiFi";
const char* WIFI_PASS = "contraseña";

/* ========= CONFIG UDP ========= */
WiFiUDP udp;
const uint16_t UDP_PORT = 9999;

/* ========= DISPLAY ========= */
String lines[12];
int idx = 0;

/* ========= MOSTRAR INFORMACIÓN ========= */
void addLine(const String& s) {
  lines[idx] = s;
  idx = (idx + 1) % 12;

  M5.Lcd.fillScreen(BLACK);
  M5.Lcd.setCursor(0, 0);
  M5.Lcd.setTextSize(2);
  M5.Lcd.setTextColor(GREEN);

  for (int i = 0; i < 12; i++) {
    int j = (idx + i) % 12;
    M5.Lcd.println(lines[j]);
  }
}

/* ========= EXTRAER INFORMACIÓN ========= */
String getField(const String& msg, const String& key) {
  int k = msg.indexOf(key + "=");
  if (k < 0) return "-";
  int start = k + key.length() + 1;
  int end = msg.indexOf(' ', start);
  if (end < 0) end = msg.length();
  return msg.substring(start, end);
}

/* ========= SETUP ========= */
void setup() {
  M5.begin();
  M5.Lcd.fillScreen(BLACK);

  addLine("Flow Monitor L3");
  addLine("Conectando WiFi");

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) delay(300);

  addLine("WiFi OK");
  addLine(WiFi.localIP().toString());
  addLine("----------------");

  udp.begin(UDP_PORT);
  addLine("UDP " + String(UDP_PORT));
}

/* ========= LOOP ========= */
void loop() {
  int size = udp.parsePacket();
  if (!size) return;

  char buf[512];
  int len = udp.read(buf, sizeof(buf) - 1);
  if (len <= 0) return;
  buf[len] = 0;

  String msg(buf);

  String src  = getField(msg, "src");
  String dst  = getField(msg, "dst");
  String sport= getField(msg, "sport");
  String dport= getField(msg, "dport");
  String proto= getField(msg, "proto");
  String app  = getField(msg, "app");
  String tx   = getField(msg, "tx");
  String rx   = getField(msg, "rx");
  String dur  = getField(msg, "dur");

  // Mostrar en pantalla
  addLine(app + " " + proto);
  addLine(src + ":" + sport);
  addLine("-> " + dst + ":" + dport);
  addLine("TX " + tx + " RX " + rx);
  addLine("DUR " + dur + " ms");
  addLine("----------------");
}