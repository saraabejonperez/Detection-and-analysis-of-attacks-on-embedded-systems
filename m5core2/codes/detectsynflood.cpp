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

/* ========= PANTALLA PRINCIPAL: ESTADO + IP + OPCIONES ========= */
void mostrarEstado() {
  M5.Lcd.clear();
  M5.Lcd.setCursor(0, 0);
  M5.Lcd.setTextSize(2);

  M5.Lcd.print("Estado: ");
  if (estado == REPOSO)      M5.Lcd.println("REPOSO");
  else if (estado == CAPTURANDO) M5.Lcd.println("CAPTURA");
  else                       M5.Lcd.println("ATAQUE");

  M5.Lcd.println("\nIP: ");
  M5.Lcd.println(WiFi.localIP());

  M5.Lcd.println("\nA: Captura");
  M5.Lcd.println("B: Reposo");
  M5.Lcd.println("C: Stats");
}

/* ========= MOSTRAR ESTADÍSTICAS DE LA CAPTURA ========= */
void mostrarStats() {
  M5.Lcd.clear();
  M5.Lcd.setCursor(0, 0);
  M5.Lcd.setTextSize(2);

  M5.Lcd.printf("Total pkts: %lu\n", totalPkts);
  M5.Lcd.printf("SYN pkts:   %lu\n", synPkts);
  M5.Lcd.printf("SYN/10s:    %d\n", tsCount);

  M5.Lcd.println("\nPulsa A/B");
}

/* ========= SETUP ========= */
void setup() {
  M5.begin();
  Serial.begin(115200);

  M5.Lcd.clear();
  M5.Lcd.setTextSize(2);
  M5.Lcd.println("Iniciando IDS...");

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi conectado");
  Serial.println(WiFi.localIP());
  delay(3000);

  server.begin();

  mostrarEstado();
}

/* ========= LOOP ========= */
void loop() {
  M5.update();

  // ───── BOTON A → CAPTURA ─────
  if (M5.BtnA.wasPressed()) {
    estado = CAPTURANDO;
    mostrarEstado();
  }

  // ───── BOTON B → REPOSO ─────
  if (M5.BtnB.wasPressed()) {
    estado = REPOSO;
    mostrarEstado();
  }

  // ───── BOTON C → ESTADÍSTICAS ─────
  if (M5.BtnC.wasPressed()) {
    mostrarStats();
  }

  if (estado == REPOSO) {
    delay(10);
    return;
  }

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
      mostrarEstado();
    } else if (estado == ATAQUE && tsCount < SYN_THRESHOLD) {
      estado = CAPTURANDO;
      mostrarEstado();
    }
  }

  // ───── Respuesta HTTP ─────
  client.println("HTTP/1.1 200 OK");
  client.println("Connection: close");
  client.println();
  client.stop();
}