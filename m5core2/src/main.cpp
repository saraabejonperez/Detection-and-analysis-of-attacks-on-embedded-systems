#include <M5Core2.h>
#include <WiFi.h>
#include <WiFiUdp.h>

/* ========= CONFIG WIFI ========= */
const char* WIFI_SSID = "MotoG(4)9983";
const char* WIFI_PASS = "162a63f763c0";

/* ========= CONFIG UDP ========= */
const uint16_t UDP_PORT = 9999;
WiFiUDP udp;

/* ========= DISPLAY ========= */
String screenLines[10];
int screenIndex = 0;

/* ========= MOSTRAR INFORMACIÓN ========= */
void addLine(const String& line) {
  screenLines[screenIndex] = line;
  screenIndex = (screenIndex + 1) % 10;

  M5.Lcd.fillScreen(BLACK);
  M5.Lcd.setCursor(0, 0);
  M5.Lcd.setTextSize(2);
  M5.Lcd.setTextColor(GREEN);

  for (int i = 0; i < 10; i++) {
    int idx = (screenIndex + i) % 10;
    M5.Lcd.println(screenLines[idx]);
  }
}

/* ========= PARSER ========= */
bool parseFlow(
  const String& msg,
  String& srcIP,
  int& srcPort,
  String& dstIP,
  int& dstPort,
  String& proto,
  uint32_t& bytes
) {
  int n = sscanf(
    msg.c_str(),
    "%s %d %s %d %s %lu",
    (char*)srcIP.c_str(),
    &srcPort,
    (char*)dstIP.c_str(),
    &dstPort,
    (char*)proto.c_str(),
    &bytes
  );
  return (n == 6);
}

/* ========= SETUP ========= */
void setup() {
  M5.begin();
  M5.Lcd.fillScreen(BLACK);

  addLine("UDP Flow v2");
  addLine("Conectando WiFi...");

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  addLine("WiFi OK");
  addLine(WiFi.localIP().toString());
  addLine("----------------");

  udp.begin(UDP_PORT);
  addLine("UDP port " + String(UDP_PORT));
}

/* ========= LOOP ========= */
void loop() {
  int packetSize = udp.parsePacket();
  if (packetSize) {
    char buf[256];
    int len = udp.read(buf, sizeof(buf) - 1);
    if (len <= 0) return;
    buf[len] = 0;

    String msg(buf);

    // Campos del flujo
    String srcIP, dstIP, proto;
    int srcPort = 0, dstPort = 0;
    uint32_t bytes = 0;

    // Parsing simple (split)
    int p1 = msg.indexOf(' ');
    int p2 = msg.indexOf(' ', p1 + 1);
    int p3 = msg.indexOf(' ', p2 + 1);
    int p4 = msg.indexOf(' ', p3 + 1);
    int p5 = msg.indexOf(' ', p4 + 1);

    if (p1 < 0 || p2 < 0 || p3 < 0 || p4 < 0 || p5 < 0) return;

    srcIP   = msg.substring(0, p1);
    srcPort = msg.substring(p1 + 1, p2).toInt();
    dstIP   = msg.substring(p2 + 1, p3);
    dstPort = msg.substring(p3 + 1, p4).toInt();
    proto   = msg.substring(p4 + 1, p5);
    bytes   = msg.substring(p5 + 1).toInt();

    // Mostrar en pantalla
    addLine(srcIP);
    addLine(String(srcPort) + " -> " + dstIP + ":" + dstPort);
    addLine(proto + "  " + String(bytes) + " bytes");
    addLine("----------------");
  }

  delay(5);
}

