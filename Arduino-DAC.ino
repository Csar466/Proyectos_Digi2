const int pinesDAC[8] = {9, 8, 7, 6, 5, 4, 3, 2};  // D0 a D7 para el DAC0808

// ==== Botón para cambiar de forma de onda ====
const int pinBoton = 10;  // Botón con resistencia pull-up (a GND)

// ==== Tablas de onda de 64 muestras ====
const uint8_t onda_senoidal[64] = {
127, 139, 152, 165, 176, 187, 197, 206,
213, 219, 224, 227, 229, 230, 229, 227,
224, 219, 213, 206, 197, 187, 176, 165,
152, 139, 127, 114, 101,  88,  77,  66,
 56,  47,  40,  34,  29,  26,  24,  23,
 24,  26,  29,  34,  40,  47,  56,  66,
 77,  88, 101, 114, 127, 139, 152, 165,
176, 187, 197, 206, 213, 219, 224, 227
};

const uint8_t onda_triangular[64] = {
  0,8,16,24,32,40,48,56,
  64,72,80,88,96,104,112,120,
  128,136,144,152,160,168,176,184,
  192,200,208,216,224,232,240,248,
  255,248,240,232,224,216,208,200,
  192,184,176,168,160,152,144,136,
  128,120,112,104,96,88,80,72,
  64,56,48,40,32,24,16,8
};

const uint8_t onda_cuadrada[64] = {
  255,255,255,255,255,255,255,255,
  255,255,255,255,255,255,255,255,
  0,0,0,0,0,0,0,0,
  0,0,0,0,0,0,0,0,
  255,255,255,255,255,255,255,255,
  255,255,255,255,255,255,255,255,
  0,0,0,0,0,0,0,0,
  0,0,0,0,0,0,0,0
};

const int N = 64;  // Número de muestras por ciclo
int forma_de_onda = 0;  // 0 = seno, 1 = triangular, 2 = cuadrada

// ==== CONFIGURACIÓN ====
void setup() {
  // Configurar pines del DAC
  for (int i = 8; i > 0; i--) {
    pinMode(pinesDAC[i], OUTPUT);
  }

  // Configurar botón de cambio
  pinMode(pinBoton, INPUT_PULLUP);
}

// ==== Función para enviar un byte al DAC ====
void enviarDAC(uint8_t valor) {
  for (int i = 0; i < 8; i++) {
    digitalWrite(pinesDAC[i], (valor >> i) & 0x01);
  }
}

// ==== Bucle principal ====
void loop() {
  // Lógica del botón para cambiar la forma de onda
  static bool estadoPrevio = HIGH;
  bool estadoActual = digitalRead(pinBoton);

  if (estadoPrevio == HIGH && estadoActual == LOW) {
    forma_de_onda = (forma_de_onda + 1) % 3;  // 0 → 1 → 2 → 0
    delay(300);  // Debouncing simple
  }
  estadoPrevio = estadoActual;

  // Recorre la onda seleccionada
  for (int i = 0; i < N; i++) {
    uint8_t valor = 127;  // Valor por defecto

    if (forma_de_onda == 0)
      valor = onda_senoidal[i];
    else if (forma_de_onda == 1)
      valor = onda_triangular[i];
    else if (forma_de_onda == 2)
      valor = onda_cuadrada[i];

    enviarDAC(valor);           // Enviar valor al DAC
    delayMicroseconds(500);     // Control de frecuencia
  }
}