#include <M5Core2.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <vector>

/* ========= CONFIG WIFI ========= */
const char* WIFI_SSID = "WiFi";
const char* WIFI_PASS = "contraseña";

/* ========= CONFIG UDP ========= */
WiFiUDP udp;
const uint16_t UDP_PORT = 9999;

/* ========= ESTADOS ========= */
enum State { IDLE, CAPTURING, SHOW_STATS };
State state = IDLE;

/* ========= ESTADÍSTICAS ========= */
uint32_t totalFlows = 0;
uint32_t tcpFlows = 0;
uint32_t udpFlows = 0;
uint32_t totalTx = 0;
uint32_t totalRx = 0;

std::vector<String> srcIPs;
std::vector<String> dstIPs;

bool contains(std::vector<String>& v, const String& s) {
  for (auto& x : v) if (x == s) return true;
  return false;
}

/* ========= EXTRAER INFORMACIÓN ========= */
String getField(const String& msg, const String& key) {
  int k = msg.indexOf(key + "=");
  if (k < 0) return "";
  int start = k + key.length() + 1;
  int end = msg.indexOf(' ', start);
  if (end < 0) end = msg.length();
  return msg.substring(start, end);
}

/* ========= RESETEAR VENTANA DE ESTADÍSTICAS ========= */
void resetStats() {
  totalFlows = tcpFlows = udpFlows = 0;
  totalTx = totalRx = 0;
  srcIPs.clear();
  dstIPs.clear();
}

/* ========= PANTALLA EN ESTADO DE REPOSO ========= */
void showIdleScreen() {
  M5.Lcd.fillScreen(BLACK);
  M5.Lcd.setCursor(0, 0);
  M5.Lcd.setTextSize(2);
  M5.Lcd.setTextColor(WHITE);

  M5.Lcd.println("MODO REPOSO");
  M5.Lcd.println("");
  M5.Lcd.println("A: Capturar");
  M5.Lcd.println("C: Stats");
}

/* ========= MOSTRAR ESTADÍSTICAS ========= */
void showStats() {
  M5.Lcd.fillScreen(BLACK);
  M5.Lcd.setCursor(0, 0);
  M5.Lcd.setTextSize(2);
  M5.Lcd.setTextColor(CYAN);

  M5.Lcd.println("== ESTADISTICAS ==");
  M5.Lcd.println("Flows: " + String(totalFlows));
  M5.Lcd.println("TCP: " + String(tcpFlows));
  M5.Lcd.println("UDP: " + String(udpFlows));
  M5.Lcd.println("Src IPs: " + String(srcIPs.size()));
  M5.Lcd.println("Dst IPs: " + String(dstIPs.size()));
  M5.Lcd.println("TX: " + String(totalTx));
  M5.Lcd.println("RX: " + String(totalRx));
}

/* ========= SETUP ========= */
void setup() {
  M5.begin();
  M5.Lcd.setTextSize(2);

  M5.Lcd.println("Flow Monitor v4.2");
  M5.Lcd.println("Conectando WiFi");

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) delay(300);

  M5.Lcd.println("WiFi OK");
  M5.Lcd.println(WiFi.localIP().toString());
  M5.Lcd.println("----------------");

  udp.begin(UDP_PORT);
  M5.Lcd.println("UDP " + String(UDP_PORT));

  delay(2000);

  showIdleScreen();
}

/* ========= LOOP ========= */
void loop() {
  M5.update();

  // ───── BOTON B → REPOSO ─────
  if (M5.BtnB.wasPressed()) {
    state = IDLE;
    showIdleScreen();
    return;
  }

  // ───── BOTON A → INICIAR CAPTURA ─────
  if (M5.BtnA.wasPressed()) {
    resetStats();
    state = CAPTURING;
    M5.Lcd.fillScreen(BLACK);
    M5.Lcd.setCursor(0, 0);
    M5.Lcd.setTextSize(2);
    M5.Lcd.setTextColor(GREEN);
    M5.Lcd.println("CAPTURANDO...");
  }

  // ───── BOTON C → MOSTRAR ESTADISTICAS ─────
  if (M5.BtnC.wasPressed()) {
    if (state == CAPTURING || state == SHOW_STATS) {
      state = SHOW_STATS;
      showStats();
    }
  }

  // ───── SOLO CAPTURAMOS EN ESTE ESTADO ─────
  if (state != CAPTURING) return;

  int size = udp.parsePacket();
  if (!size) return;

  char buf[512];
  int len = udp.read(buf, sizeof(buf) - 1);
  if (len <= 0) return;
  buf[len] = 0;

  String msg(buf);

  totalFlows++;

  String proto = getField(msg, "proto");
  if (proto == "TCP") tcpFlows++;
  else if (proto == "UDP") udpFlows++;

  String src = getField(msg, "src");
  String dst = getField(msg, "dst");

  if (!contains(srcIPs, src)) srcIPs.push_back(src);
  if (!contains(dstIPs, dst)) dstIPs.push_back(dst);

  totalTx += getField(msg, "tx").toInt();
  totalRx += getField(msg, "rx").toInt();
}