// ==== Tablas de onda de 64 muestras ====
const uint8_t onda_senoidal[64] = {
  127,140,152,165,176,187,197,206,
  213,219,224,227,229,230,229,227,
  224,219,213,206,197,187,176,165,
  152,140,127,115,103, 90, 79, 68,
   58, 49, 42, 36, 31, 28, 26, 25,
   26, 28, 31, 36, 42, 49, 58, 68,
   79, 90,103,115,127,140,152,165,
  176,187,197,206,213,219,224,227
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

// ==== Configuración ====
const int pinPWM = 9;       // Salida PWM (conectada al filtro RC)
const int N = 64;           // Número de muestras por ciclo

// Variable para seleccionar la onda
int forma_de_onda = 0;  // 0 = seno, 1 = triangular, 2 = cuadrada

// ==== Pines para cambio de forma de onda ====
const int boton = 2;     // Pulsador conectado a GND con resistencia pull-up

void setup() {
  pinMode(pinPWM, OUTPUT);
  pinMode(boton, INPUT_PULLUP);
}

void loop() {
  // Cambiar forma de onda si se presiona el botón
  static bool boton_prev = HIGH;
  bool boton_actual = digitalRead(boton);

  if (boton_prev == HIGH && boton_actual == LOW) {
    forma_de_onda = (forma_de_onda + 1) % 3; // Cambia entre 0, 1 y 2
    delay(300); // Debouncing simple
  }
  boton_prev = boton_actual;

  // Reproducir una forma de onda
  for (int i = 0; i < N; i++) {
    uint8_t valor = 127;
    if (forma_de_onda == 0)
      valor = onda_senoidal[i];
    else if (forma_de_onda == 1)
      valor = onda_triangular[i];
    else if (forma_de_onda == 2)
      valor = onda_cuadrada[i];

    analogWrite(pinPWM, valor); // PWM proporcional al valor de la onda
    delayMicroseconds(500);     // Ajusta este valor para cambiar frecuencia
  }
}