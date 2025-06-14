# ====== IMPORTACIÓN DE LIBRERÍAS NECESARIAS ======
import threading                  # Para ejecutar lectura serial en segundo plano (sin bloquear)
import serial                     # Para comunicación con el puerto serial (Arduino)
import matplotlib.pyplot as plt  # Para graficar en tiempo real
import matplotlib.animation as animation  # Para animar el gráfico
from collections import deque     # Cola de datos eficiente, útil para buffers tipo FIFO
import tkinter as tk              # Interfaz gráfica para botones
import pandas as pd               # Para exportar datos a CSV

# ====== CONFIGURACIÓN SERIAL ======
PUERTO = 'COM9'                 # Puerto al que está conectado el Arduino (modifica si es otro)
VELOCIDAD = 115200               # Debe coincidir con Serial.begin() en Arduino

# ====== BUFFER Y ESCALAS ======
BUFFER_SIZE_MAX = 1000           # Máximo de muestras almacenadas
valores_ch0 = deque([0]*BUFFER_SIZE_MAX, maxlen=BUFFER_SIZE_MAX)  # Buffer canal 0
valores_ch1 = deque([0]*BUFFER_SIZE_MAX, maxlen=BUFFER_SIZE_MAX)  # Buffer canal 1
valores_ch2 = deque([0]*BUFFER_SIZE_MAX, maxlen=BUFFER_SIZE_MAX)  # Buffer canal 2
buffer_lock = threading.Lock()   # Lock para proteger acceso simultáneo desde hilos
escala_vertical = [0, 1024]      # Rango del eje Y (ADC de 10 bits)
ventana_muestras = 200           # Muestras visibles en pantalla
pausado = False                  # Estado de pausa

# ====== LECTURA SERIAL ======
def leer_serial():
    """Lee continuamente datos del puerto serial y actualiza los buffers"""
    while True:
        try:
            linea = ser.readline().decode('utf-8', errors='ignore').strip()  # Lee línea
            partes = linea.split(',')  # Divide por coma
            #if len(partes) == 3 and partes[0].isdigit() and partes[1].isdigit():
                #ch0 = int(partes[0])
                #ch1 = int(partes[1])
                #ch2 = int (partes[2])
            if len(partes) == 3 and all(parte.isdigit() for parte in partes):
                ch0, ch1, ch2 = map(int, partes) #convierte en enteros a todos los numeros
                with buffer_lock:  # Protección para evitar conflictos al escribir en buffers
                    valores_ch0.append(ch0)
                    valores_ch1.append(ch1)
                    valores_ch2.append(ch2) # nuevo canal
        except Exception as e:
            print("Error:", e)

# ====== INICIO DEL PUERTO SERIAL Y HILO DE LECTURA ======
ser = serial.Serial(PUERTO, VELOCIDAD, timeout=1)
ser.reset_input_buffer()  # Limpia el buffer inicial
threading.Thread(target=leer_serial, daemon=True).start()  # Ejecuta lectura en segundo plano

# ====== CONTROL DE VISIBILIDAD DE CANAL ======
canal_ch0_visible = True    # Canal 0 visible por defecto
canal_ch1_visible = True    # Canal 1 visible por defecto
canal_ch2_visible = True    # Canal 2 visible por defecto

# ====== CONFIGURACIÓN DEL GRÁFICO ======
fig, ax = plt.subplots()
linea_ch0, = ax.plot([], [], color='blue', label='CH0')  # Línea para canal 0
linea_ch1, = ax.plot([], [], color='red', label='CH1')   # Línea para canal 1
linea_ch2, = ax.plot([], [], color='green', label='CH2') # Línea para canal 2
ax.legend()  # Mostrar leyenda
ax.set_title("Osciloscopio Digital - 3 Canales")
ax.set_ylabel("Valor ADC")
ax.set_xlabel("Tiempo (muestras)")
ax.set_ylim(*escala_vertical)       # Escala vertical inicial
ax.set_xlim(0, ventana_muestras)    # Escala horizontal inicial

# ====== FUNCIÓN PARA ACTUALIZAR EL GRÁFICO ======
def actualizar(frame):
    """Actualiza los datos mostrados en el gráfico cada intervalo"""
    if pausado:
        #return linea_ch0, linea_ch1  # Si está pausado, no actualiza nada
        return linea_ch0, linea_ch1, linea_ch2
    with buffer_lock:
        datos_ch0 = list(valores_ch0)[-ventana_muestras:]  # Últimas N muestras
        datos_ch1 = list(valores_ch1)[-ventana_muestras:]
        datos_ch2 = list(valores_ch2)[-ventana_muestras:]  # nuevo canal
    #linea_ch0.set_data(range(len(datos_ch0)), datos_ch0)
    #linea_ch1.set_data(range(len(datos_ch1)), datos_ch1)
    #linea_ch2.set_data(range(len(datos_ch2)), datos_ch2)  # nuevo canal
    #ax.set_xlim(0, ventana_muestras)  # Actualiza el eje X
    #return linea_ch0, linea_ch1, linea_ch2

    #Actualiza datos solo si el canal está visible
    if canal_ch0_visible:
        linea_ch0.set_data(range(len(datos_ch0)), datos_ch0)
        linea_ch0.set_visible(True)
    else:
        linea_ch0.set_visible(False)
    
    if canal_ch1_visible:
        linea_ch1.set_data(range(len(datos_ch1)), datos_ch1)
        linea_ch1.set_visible(True)
    else:
        linea_ch1.set_visible(False)
    
    if canal_ch2_visible:
        linea_ch2.set_data(range(len(datos_ch2)), datos_ch2)
        linea_ch2.set_visible(True)
    else:
        linea_ch2.set_visible(False)
    
    ax.set_xlim(0, ventana_muestras)  # Actualiza el eje X
    return linea_ch0, linea_ch1, linea_ch2

# ====== TECLADO PARA CAMBIAR ESCALAS EN VIVO ======
def on_key(evento):
    """Permite modificar escalas vertical y horizontal con el teclado"""
    global escala_vertical, ventana_muestras
    if evento.key == 'up':
        escala_vertical[1] = max(escala_vertical[1] - 500, 100)  # Reduce Ymax
    elif evento.key == 'down':
        escala_vertical[1] = min(escala_vertical[1] + 500, 4200)  # Aumenta Ymax
    elif evento.key == 'r':
        escala_vertical = [0, 1024]  # Restaura escala original
        ventana_muestras = 200
    elif evento.key == 'left':
        ventana_muestras = max(50, ventana_muestras - 50)  # Menos muestras visibles
    elif evento.key == 'right':
        ventana_muestras = min(BUFFER_SIZE_MAX, ventana_muestras + 50)  # Más muestras visibles

    ax.set_ylim(*escala_vertical)  # Aplica nueva escala Y
    print(f"Vertical: {escala_vertical}, Horizontal: {ventana_muestras}")

fig.canvas.mpl_connect('key_press_event', on_key)  # Vincula teclado al gráfico

# ====== FUNCIONES ADICIONALES (BOTONES) ======

def exportar_csv():
    """Guarda los datos actuales en un archivo CSV (por ahora fija ruta)"""
    with buffer_lock:
        datos_ch0 = list(valores_ch0)
        datos_ch1 = list(valores_ch1)
        datos_ch2 = list(valores_ch2)  # nuevo canal
    df = pd.DataFrame({'CH0': datos_ch0, 'CH1': datos_ch1, 'CH2': datos_ch2})
    df.to_csv('datos_capturados.csv', index=False)
    print("Datos exportados a 'datos_capturados.csv'")

def pausar_reanudar():
    """Alterna el estado de pausa del gráfico"""
    global pausado
    pausado = not pausado
    estado = "Pausado" if pausado else "Reanudado"
    print(f"Estado: {estado}")

def guardar_imagen():
    """Guarda una imagen PNG del gráfico actual"""
    fig.savefig("captura_osciloscopio.png")
    print("Gráfico guardado como 'captura_osciloscopio.png'")

def crear_ventana_csv():
    """Crea una pequeña ventana con botones gráficos"""
    ventana = tk.Tk()
    ventana.title("Opciones del Osciloscopio")
    ventana.geometry("380x320")

    # ====== SECCIÓN DE CONTROL DE CANALES ======
    frame_canales = tk.LabelFrame(ventana, text="Control de Canales", padx=10, pady=10)
    frame_canales.pack(pady=10, padx=10, fill="x")
    
    # Botones individuales de canales
    boton_ch0 = tk.Button(frame_canales, text="On/Off CH0", command=toggle_ch0, 
                         bg='lightblue', width=12)
    boton_ch0.grid(row=0, column=0, padx=5, pady=5)
    
    boton_ch1 = tk.Button(frame_canales, text="On/Off CH1", command=toggle_ch1, 
                         bg='lightcoral', width=12)
    boton_ch1.grid(row=0, column=1, padx=5, pady=5)
    
    boton_ch2 = tk.Button(frame_canales, text="On/Off CH2", command=toggle_ch2, 
                         bg='lightgreen', width=12)
    boton_ch2.grid(row=0, column=2, padx=5, pady=5)
    
    # Botones maestros
    boton_todos_on = tk.Button(frame_canales, text="Activar Todos", command=activar_todos,
                              bg='green', fg='white', width=15)
    boton_todos_on.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
    
    boton_todos_off = tk.Button(frame_canales, text="Desactivar Todos", command=desactivar_todos,
                               bg='red', fg='white', width=15)
    boton_todos_off.grid(row=1, column=2, columnspan=1, padx=5, pady=5)
    
    # ====== SECCIÓN DE FUNCIONES EXISTENTES ======
    frame_funciones = tk.LabelFrame(ventana, text="Funciones", padx=10, pady=10)
    frame_funciones.pack(pady=10, padx=10, fill="x")
    
    boton_csv = tk.Button(frame_funciones, text="Exportar CSV", command=exportar_csv, bg='yellow')
    boton_csv.pack(pady=5)

    boton_pausa = tk.Button(frame_funciones, text="Pausar/Reanudar", command=pausar_reanudar, bg='orange')
    boton_pausa.pack(pady=5)

    boton_imagen = tk.Button(frame_funciones, text="Guardar Imagen", command=guardar_imagen, bg='lightgreen')
    boton_imagen.pack(pady=5)

    ventana.mainloop()

# ====== FUNCIONES DE CONTROL DE CANALES ======
def toggle_ch0():
    """Activa/desactiva la visualización del canal 0"""
    global canal_ch0_visible
    canal_ch0_visible = not canal_ch0_visible
    estado = "Activado" if canal_ch0_visible else "Desactivado"
    print(f"Canal 0: {estado}")

def toggle_ch1():
    """Activa/desactiva la visualización del canal 1"""
    global canal_ch1_visible
    canal_ch1_visible = not canal_ch1_visible
    estado = "Activado" if canal_ch1_visible else "Desactivado"
    print(f"Canal 1: {estado}")

def toggle_ch2():
    """Activa/desactiva la visualización del canal 2"""
    global canal_ch2_visible
    canal_ch2_visible = not canal_ch2_visible
    estado = "Activado" if canal_ch2_visible else "Desactivado"
    print(f"Canal 2: {estado}")

def activar_todos():
    """Activa todos los canales"""
    global canal_ch0_visible, canal_ch1_visible, canal_ch2_visible
    canal_ch0_visible = canal_ch1_visible = canal_ch2_visible = True
    print("Todos los canales activados")

def desactivar_todos():
    """Desactiva todos los canales"""
    global canal_ch0_visible, canal_ch1_visible, canal_ch2_visible
    canal_ch0_visible = canal_ch1_visible = canal_ch2_visible = False
    print("Todos los canales desactivados")

# ====== LANZAR LA VENTANA DE BOTONES EN SEGUNDO PLANO ======
threading.Thread(target=crear_ventana_csv, daemon=True).start()

# ====== INICIAR ANIMACIÓN DEL GRÁFICO ======
ani = animation.FuncAnimation(fig, actualizar, interval=10, blit=False)
plt.show()