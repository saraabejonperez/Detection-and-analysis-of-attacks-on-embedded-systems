#include <M5Core2.h>

bool pausado = false;

void setup() {
  M5.begin();
  M5.Lcd.fillScreen(BLACK);
  M5.Lcd.println("Btn B = Pausa / Reanuda");
}

void loop() {
  M5.update();

  if (M5.BtnB.wasPressed()) {
    pausado = !pausado; // alterna pausa
    M5.Lcd.setCursor(0, 30);
    M5.Lcd.printf("Estado: %s   ", pausado ? "PAUSADO" : "EJECUTANDO");
  }

  if (!pausado) {
    M5.Lcd.setCursor(0, 60);
    M5.Lcd.printf("Millis: %lu   ", millis());
  }

  delay(200);
}