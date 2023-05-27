import socket
import gc
import network
from dcmotor import DCMotor
from dcmotor import Servo
from dcmotor import HCSR04
from machine import Pin, PWM
from time import sleep
import dht


def control(data):
    distancia = sensor.distance_cm()
    print(distancia)

    if 2 < distancia < 60:
        print("Distancia muy corta")
        motor_traction.stop()
        motor_traction.backwards(100)
        sleep(0.3)
        motor_traction.stop()
        return

    try:

        accel, reverse, direction, headlight, demo = data.split(':')

        if data != "":
            direction = int(direction)
            accel = int(accel)
            reverse = int(reverse)
            headlight = int(headlight)
            demo = int(demo)

            if demo == 1:
                demonstration()
                return

            if headlight == 1:
                headlights_1.duty(1023)  # 1024 = 100%
                headlights_2.duty(1023)
            else:
                headlights_1.duty(100)
                headlights_2.duty(100)

            if -30 < direction < 30:
                motor_direction.stop()
                servom.move(95)
            else:
                if direction >= 0:
                    print("Derecha")
                    motor_direction.forward(direction + 30)
                    servom.move(50)
                else:
                    print("Izquierda")
                    motor_direction.backwards((-1 * direction) + 30)
                    servom.move(140)

            if accel > 0 and reverse == 0:
                print("Avanzando")
                motor_traction.forward(accel)

            elif accel == 0 and reverse > 0:
                # Prender led reversa
                print("Retrocediendo")
                motor_traction.backwards(reverse)
            else:
                motor_traction.stop()

    except Exception as e:
        print(f"Data erronea: {data} {e}")
        return

        # conn.sendall(data)

def demonstration():
    #Movemos servo
    servom.move(90)
    sleep(0.2)
    servom.move(0)

    # Cambio de luces

    for i in range(0, 5):
        headlights_1.duty(1023)  # 1024 = 100%
        headlights_2.duty(1023)
        sleep(1)
        headlights_1.duty(100)  # 1024 = 100%
        headlights_2.duty(100)
        sleep(1)


    #Movemos direccion
    motor_direction.backwards(100)
    sleep(0.5)
    motor_direction.forward(100)
    sleep(0.5)
    motor_direction.backwards(100)
    sleep(0.5)
    motor_direction.forward(100)
    sleep(0.5)
    motor_direction.backwards(100)
    sleep(0.5)
    motor_direction.forward(100)
    sleep(0.5)
    motor_direction.backwards(100)
    sleep(0.5)
    motor_direction.forward(100)
    sleep(0.5)

    #avanzar y retroceder
    motor_traction.forward(80)
    sleep(2)
    motor_traction.stop()
    motor_traction.backwards(80)
    sleep(2)

    #Circulos a la izquierda
    motor_direction.backwards(100)
    motor_traction.forward(100)
    sleep(3)
    motor_direction.stop()
    motor_direction.backwards(100)
    sleep(3)

    print("Finalizando demo.")


# Socket
HOST = ""
PORT = 5000

# Ultrasonico
sensor = HCSR04(trigger_pin=23, echo_pin=22, echo_timeout_us=10000)

headlights_1 = PWM(Pin(12), freq=5000)
headlights_1.init()
headlights_1.duty(1023)

headlights_2 = PWM(Pin(13), freq=5000)
headlights_2.init()
headlights_2.duty(1023)

#Servo
servom = Servo(pin=15)

#DHT
d = dht.DHT11(Pin(2))

# AP
ssid = 'El carrito follador'

print(d.temperature(), "grados") # eg. 23 (°C)
print("Setting up AP...")

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid)

# MOTORS

print("Setting up motors...")

frequency = 15000
pin1 = Pin(26, Pin.OUT)
pin2 = Pin(27, Pin.OUT)
enable_direction = PWM(Pin(25), frequency)
motor_direction = DCMotor(pin1, pin2, enable_direction, 350, 1023)

pin3 = Pin(21, Pin.OUT)
pin4 = Pin(19, Pin.OUT)
enable_traction = PWM(Pin(18), frequency)
motor_traction = DCMotor(pin3, pin4, enable_traction, 350, 1023)

print("Starting socket...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
s.bind((HOST, PORT))
s.listen()

print("Socket started.")

gc.collect()  # Limpia memoria
conn, addr = s.accept()  # Aceptanmos la conexion

while True:
    data = conn.recv(15).decode()
    control(data)

    try:
        d.measure()
        #sleep(3)
        temperature = str(d.temperature())
        print(f"Temp is -> {temperature}")
        conn.send(temperature.encode())
    except:
        conn.send("25".encode())