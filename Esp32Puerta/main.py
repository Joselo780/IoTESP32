import network
import socket
import json
from machine import Pin, PWM
import time

# Declaración del objeto y funciones
class ServoMotor:
    def __init__(self, control_pin):
        self.pwm = PWM(Pin(control_pin), freq=50)

    def moverAng(self, angulo):
        duty = int(1638 + (angulo / 180) * (8191 - 1638))
        self.pwm.duty_u16(duty)
        print(f"Servo movido a {angulo} grados.")

    def detener(self):
        self.pwm.deinit()
        print("Servo desactivado.")

# Pines de conexión
aspersor = ServoMotor(control_pin=33)
puerta = ServoMotor(control_pin=26)

puerta_abierta = False  # Estado inicial

try:
    while True:
        comando = input("Ingrese 'A' para accionar el aspersor, 'P' para alternar puerta, o 'S' para salir: ").upper()
        
        if comando == "A":
            aspersor.moverAng(180)
            sleep(1)
            aspersor.moverAng(40)
            sleep(1)

        elif comando == "P":
            if puerta_abierta:
                puerta.moverAng(160)  # Cerrar
                print("Puerta cerrada.")
            else:
                puerta.moverAng(50)   # Abrir
                print("Puerta abierta.")
            puerta_abierta = not puerta_abierta
            sleep(1)

        elif comando == "S":
            print("Saliendo...")
            break
        else:
            print("Comando no reconocido. Intente de nuevo.")
finally:
    aspersor.detener()
    puerta.detener()

# WiFi config
ssid = 'TU_SSID'
password = 'TU_PASSWORD'

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
    print('Conectado a WiFi:', wlan.ifconfig())

def manejar_peticion(path, body):
    try:
        data = json.loads(body)
        estado = data.get("estado", False)

        if path == '/puerta':
            mover_puerta(estado)
            return "Puerta movida"
        else:
            return "Ruta no válida"
    except Exception as e:
        return f"Error: {e}"

def iniciar_servidor():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print("Servidor HTTP en puerto 80...")

    while True:
        cl, addr = s.accept()
        print('Cliente conectado desde', addr)
        request = cl.recv(1024).decode()
        headers, _, body = request.partition('\r\n\r\n')
        method, path, _ = headers.split('\n')[0].split()

        if method == 'POST':
            respuesta = manejar_peticion(path, body)
        else:
            respuesta = "Método no soportado"

        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n')
        cl.send(respuesta)
        cl.close()

# MAIN
conectar_wifi()
iniciar_servidor()
