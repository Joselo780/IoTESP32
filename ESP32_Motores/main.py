import network
import socket
import json
from machine import Pin
from time import sleep

# Declaración de objeto y funciones
class MotorL298N:
    def __init__(self, in1_pin, in2_pin, enable_pin):
        self.in1 = Pin(in1_pin, Pin.OUT)
        self.in2 = Pin(in2_pin, Pin.OUT)
        self.enable = Pin(enable_pin, Pin.OUT)
    
    def girarMot(self):
        self.enable.value(1)
        self.in1.value(1)
        self.in2.value(0)
        
    def detener(self):
        self.in1.value(0)
        self.in2.value(0)
        self.enable.value(0)
        print("Motor detenido y deshabilitado.")

# Pines físicos
ventilador = MotorL298N(in1_pin=25, in2_pin=26, enable_pin=27)
bomba = MotorL298N(in1_pin=13, in2_pin=12, enable_pin=14)

# Control de los motores
while True:
    comando = input("Ingrese 'V' para girar el ventilador, 'B' para girar la bomba, o 'S' para detener y salir: ").upper()
    
    if comando == "V":
        print("Ventilador funcionando...")
        ventilador.girarMot()
        sleep(5)
        ventilador.detener()
        
    elif comando == "B":
        print("Bomba funcionando...")
        bomba.girarMot()
        sleep(10)
        bomba.detener()
        
    elif comando == "S":
        ventilador.detener()
        bomba.detener()
        print("Saliendo...")
        break
    else:
        print("Comando no reconocido. Intente de nuevo.")


# Conexión WiFi
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

        if path == '/ventilador':
            pin_ventilador.value(1 if estado else 0)
            return "Ventilador actualizado"
        elif path == '/bomba':
            pin_bomba.value(1 if estado else 0)
            return "Bomba actualizada"
        else:
            return "Ruta no válida"
    except Exception as e:
        return f"Error: {e}"

def iniciar_servidor():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print("Servidor escuchando en puerto 80")

    while True:
        cl, addr = s.accept()
        print('Cliente conectado desde', addr)
        request = cl.recv(1024).decode()
        headers, _, body = request.partition('\r\n\r\n')
        first_line = headers.split('\n')[0]
        method, path, _ = first_line.split()

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
