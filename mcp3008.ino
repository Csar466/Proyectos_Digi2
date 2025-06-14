#include <SPI.h> // Incluir librería SPI para comunicar con MCP3008
const int CS_PIN=10; // Pin de selección de chip (CS)
void setup() {
  Serial.begin(115200);       // Iniciar monitor serial
  SPI.begin();              // Iniciar bus SPI
  pinMode(CS_PIN,OUTPUT);  // CS como salida
  digitalWrite(CS_PIN, HIGH); // Mantener CS en alto por defecto
}

void loop() {
  int valorCH0 = leerMCP3008(0); // Leer canal CH0
  int valorCH1 = leerMCP3008(1);
  int valorCH2 = leerMCP3008(2);
  Serial.print(valorCH0);
  Serial.print(",");  
  Serial.print(valorCH1);      // Solo imprime el número
  Serial.print(",");
  Serial.println(valorCH2);
  delay(10);
}
// Función para leer un canal del MCP3008
int leerMCP3008(int canal) {
  if (canal < 0 || canal > 3) return -1; // Validar canal (0 a 3)
  byte startBit = 0b00000110;  // Byte 1: Start bit (1), modo single-ended (1), bit 2 canal (D1)
  byte canalBits = (canal & 0x03) << 6; // Byte 2: Bits D1 y D0 de canal en los bits 7 y 6
  digitalWrite(CS_PIN, LOW); // Activar el chip
  SPI.transfer(startBit);    // Enviar primer byte (start + single + D2 canal)
  int resultado = SPI.transfer(canalBits); // Enviar segundo byte (D1 y D0 del canal)
  resultado = (resultado & 0x0F) << 8; // Solo los 4 bits inferiores son útiles → bits 11–8
  resultado |= SPI.transfer(0x00);     // Leer bits 7–0 del resultado
  digitalWrite(CS_PIN, HIGH); // Desactivar el chip
  return resultado; // Valor de 12 bits (0–4095)
}
