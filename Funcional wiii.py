import network
import urequests
import time
from machine import Pin, ADC, PWM

# --- CONFIGURACIÓN RED ---
SSID = "S25 FE de Anderson"
PASS = "123456789"
URL = "http://10.215.3.61:5000/update"

def conectar():
    w = network.WLAN(network.STA_IF)
    w.active(True)
    w.connect(SSID, PASS)
    while not w.isconnected():
        print("Buscando red...")
        time.sleep(1)
    print("¡Conectado! IP de la ESP32:", w.ifconfig()[0])

conectar()

# --- CONFIGURACIÓN CORRECTA DE PINES ---
lm35 = ADC(Pin(32))        # ADC1 (NO usar 27)
lm35.atten(ADC.ATTN_0DB)

pot = ADC(Pin(35))
ldr = ADC(Pin(34))

pot.atten(ADC.ATTN_11DB)
ldr.atten(ADC.ATTN_11DB)

# LEDs
led_r = Pin(21, Pin.OUT)
led_a = Pin(18, Pin.OUT)
led_v = Pin(23, Pin.OUT)

# Servo
servo = PWM(Pin(25), freq=50)

# Botón con antirrebote
boton = Pin(19, Pin.IN, Pin.PULL_UP)
sistema_habilitado = False
ultimo_tiempo = 0

def toggle(pin):
    global sistema_habilitado, ultimo_tiempo
    ahora = time.ticks_ms()
    if time.ticks_diff(ahora, ultimo_tiempo) > 300:
        sistema_habilitado = not sistema_habilitado
        ultimo_tiempo = ahora

boton.irq(trigger=Pin.IRQ_FALLING, handler=toggle)

def mover_servo(angulo):
    if angulo == 0:
        servo.duty(40)
    elif angulo == 180:
        servo.duty(115)

# --- FUNCIÓN PARA FILTRAR LM35 (más estable) ---
def leer_temperatura():
    suma = 0
    for _ in range(10):
        suma += lm35.read()
        time.sleep_ms(5)
    val = suma / 10

    voltaje = (val / 4095.0) * 1.1
    
    # CALIBRACIÓN (ajustada a tu caso real)
    temperatura = voltaje * 100.0

    return round(temperatura, 1)

# --- BUCLE PRINCIPAL ---
while True:

    datos = {
        "temp": 0, "ref": 0, "luz": 0,
        "sistema": "Deshabilitado", "servo": "Cerrado", "led": "Ninguno"
    }

    if sistema_habilitado:

        # 🔹 Sensores
        t = leer_temperatura()
        r = round(25.0 + (pot.read() / 4095.0) * 20.0, 1)
        l = ldr.read()

        # 🔹 Servo
        s_txt = "Abierto" if t >= r else "Cerrado"
        mover_servo(180 if t >= r else 0)

        # 🔹 LEDs
        led_r.value(0)
        led_a.value(0)
        led_v.value(0)

        if l < 1365:
            led_r.value(1)
            l_txt = "Rojo"
        elif l < 2730:
            led_a.value(1)
            l_txt = "Amarillo"
        else:
            led_v.value(1)
            l_txt = "Verde"

        datos = {
            "temp": t,
            "ref": r,
            "luz": l,
            "sistema": "Habilitado",
            "servo": s_txt,
            "led": l_txt
        }

        print("Enviando al PC: {}°C".format(t))

    else:
        mover_servo(0)
        led_r.value(0)
        led_a.value(0)
        led_v.value(0)

    # 🔹 Envío al servidor
    try:
        res = urequests.post(URL, json=datos) # aqui se envian los datos a la url del ervidor que se configuro mas arriba, en formato json a la variable datos
        res.close()
    except:
        print("Error: No se pudo contactar con el Servidor")

    time.sleep(0.7)