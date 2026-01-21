#include <WiFi.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>
#include <M5Core2.h>

/* ========= CONFIG WIFI ========= */
const char* WIFI_SSID = "WiFi";
const char* WIFI_PASS = "contraseña";

WiFiServer server(80);

/* ========= IDS ========= */
constexpr unsigned long SYN_WINDOW_MS = 10000;
constexpr int SYN_THRESHOLD = 5;
constexpr int MAX_SYNS = 50;

unsigned long synTimestamps[MAX_SYNS];
int headIndex = 0;
int tsCount   = 0;

/* ========= ESTADOS ========= */
enum EstadoIDS {
  REPOSO,
  CAPTURANDO,
  ATAQUE
};

EstadoIDS estado = REPOSO;

/* ========= ESTADÍSTICAS ========= */
unsigned long totalPkts = 0;
unsigned long synPkts   = 0;
String lastAttackTimestamp = "N/A";
unsigned long attackPktCount = 0;
unsigned long attackLengthSum = 0;
float attackPayloadRatioSum = 0.0;

/* ========= UI ========= */
unsigned long lastUiUpdate = 0;
constexpr unsigned long UI_REFRESH_MS = 500;

/* ========= PANTALLA LIVE ========= */
void mostrarEstadoLive() {
  M5.Lcd.clear();
  M5.Lcd.setCursor(0, 0);
  M5.Lcd.setTextSize(2);
  M5.Lcd.setTextColor(WHITE);
  
  M5.Lcd.print("\nEstado: ");
  if (estado == REPOSO)          M5.Lcd.println("REPOSO");
  else if (estado == CAPTURANDO) M5.Lcd.println("CAPTURA");
  else {
    M5.Lcd.setTextColor(RED);
    M5.Lcd.println("POSIBLE ATAQUE");
  }

  M5.Lcd.setTextColor(WHITE);
  M5.Lcd.print("IP: ");
  M5.Lcd.println(WiFi.localIP());

  M5.Lcd.println();
  M5.Lcd.printf("SYN total: %lu\n", synPkts);
  M5.Lcd.printf("SYN (10s): %d / %d\n", tsCount, SYN_THRESHOLD);

  M5.Lcd.println("\nA: Captura");
  M5.Lcd.println("B: Reposo");
  M5.Lcd.println("C: Stats");
}

/* ========= MOSTRAR ESTADÍSTICAS DE LA CAPTURA ========= */
void mostrarStats() {
  M5.Lcd.clear();
  M5.Lcd.setCursor(0, 0);
  M5.Lcd.setTextSize(2);
  M5.Lcd.setTextColor(WHITE);

  M5.Lcd.printf("Total pkts recibidos: %lu\n", totalPkts);
  M5.Lcd.println("\n- Estadisticas de ataque -");
  M5.Lcd.printf("Ultimo ataque: \n\t-> %s\n", lastAttackTimestamp);
  M5.Lcd.printf("Pkts ataque recibidos: \n\t-> %lu\n", attackPktCount);
  if (attackPktCount > 0) {
    float avgLen = (float)attackLengthSum / attackPktCount;
    float avgRatio = attackPayloadRatioSum / attackPktCount;

    M5.Lcd.printf("Longitud media pkt: \n\t-> %.0f B\n", avgLen);
    M5.Lcd.printf("Ratio Payload/Longitud: \n\t-> %.2f\n", avgRatio);
  }
  else {
    M5.Lcd.printf("Longitud media pkt: \n\t-> N/A\n");
    M5.Lcd.printf("Ratio Payload/Longitud: \n\t-> N/A\n");
  }

  M5.Lcd.println("\nPulsa A/B");
}

/* ========= SETUP ========= */
void setup() {
  M5.begin();

  M5.Lcd.clear();
  M5.Lcd.setTextSize(2);
  M5.Lcd.println("Iniciando IDS...");

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    M5.Lcd.println(".");
  }

  M5.Lcd.println("\nWiFi conectado");
  M5.Lcd.println(WiFi.localIP());
  delay(2000);

  server.begin();

  mostrarEstadoLive();
}

/* ========= LOOP ========= */
void loop() {
  M5.update();

  // ───── BOTON A → CAPTURA ─────
  if (M5.BtnA.wasPressed()) {
    estado = CAPTURANDO;
    mostrarEstadoLive();
  }

  // ───── BOTON B → REPOSO ─────
  if (M5.BtnB.wasPressed()) {
    estado = REPOSO;
    mostrarEstadoLive();
  }

  // ───── BOTON C → ESTADÍSTICAS ─────
  if (M5.BtnC.wasPressed()) {
    mostrarStats();
  }

  // ───── REFRESCO LIVE ─────
  if (estado != REPOSO && millis() - lastUiUpdate > UI_REFRESH_MS) {
    mostrarEstadoLive();
    lastUiUpdate = millis();
  }

  if (estado == REPOSO) return;

  // ───── Servidor HTTP ─────
  WiFiClient client = server.available();
  if (!client) return;

  String request;
  unsigned long start = millis();
  while (client.connected() && millis() - start < 1000) {
    while (client.available()) {
      request += char(client.read());
      start = millis();
    }
  }

  int idx = request.indexOf("\r\n\r\n");
  if (idx < 0) {
    client.stop();
    return;
  }

  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, request.substring(idx + 4));
  if (err) {
    client.stop();
    return;
  }

  totalPkts++;

  String protocol = doc["protocol"] | "";
  String flags    = doc["flags"] | "";
  unsigned long now = millis();
  int length = doc["length"] | 0;
  int payload_len = doc["payload_len"] | 0;
  unsigned long packetTimestamp = doc["timestamp"] | 0;

  unsigned long totalSeconds = packetTimestamp / 1000;
  unsigned long seconds = totalSeconds % 60;
  unsigned long minutes = (totalSeconds / 60) % 60;
  unsigned long hours = totalSeconds / 3600;

  char buffer[10];
  snprintf(buffer, sizeof(buffer), "%02lu:%02lu:%02lu", hours, minutes, seconds);
  String timestamp = String(buffer);

  // ───── Detección SYN Flood ─────
  if (protocol == "TCP" && flags.indexOf("SYN") >= 0) {
    synPkts++;

    int pos = (headIndex + tsCount) % MAX_SYNS;
    synTimestamps[pos] = now;

    if (tsCount < MAX_SYNS) {
      tsCount++;
    } else {
      headIndex = (headIndex + 1) % MAX_SYNS;
    }

    // Limpiar fuera de ventana
    while (tsCount > 0 && now - synTimestamps[headIndex] > SYN_WINDOW_MS) {
      headIndex = (headIndex + 1) % MAX_SYNS;
      tsCount--;
    }

    if (tsCount >= SYN_THRESHOLD && estado != ATAQUE) {
      estado = ATAQUE;
      lastAttackTimestamp = timestamp;

      // Resetear estadísticas del ataque anterior
      attackPktCount = 0;
      attackLengthSum = 0;
      attackPayloadRatioSum = 0;

      mostrarEstadoLive();
    } else if (estado == ATAQUE && tsCount < SYN_THRESHOLD) {
      estado = CAPTURANDO;
      mostrarEstadoLive();
    }

    if (estado == ATAQUE && length > 0) {
      attackPktCount++;
      attackLengthSum += length;
      attackPayloadRatioSum += (float)payload_len / length;
    }
  }

  // ───── Respuesta HTTP ─────
  client.println("HTTP/1.1 200 OK");
  client.println("Connection: close");
  client.println();
  client.stop();
}