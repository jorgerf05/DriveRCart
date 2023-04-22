import socket
import gc
import network
from dcmotor import DCMotor
from machine import Pin, PWM
from time import sleep


# Socket
HOST = ""
PORT = 5000

#AP
ssid = 'El carrito follador'
password = '12345678'

print("Setting up AP...")

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid)

#MOTORS

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

gc.collect()
conn, addr = s.accept()

while True:
    #We will receive a string like "x.xx:y.yy", totaling 9 bytes
    data = conn.recv(11).decode()
    print(data)
    accel, reverse, direction = data.split(':')
    sleep(0.1)
    if data != "":
        direction = int(direction)
        accel = int(accel)
        reverse = int(reverse)

        if -30 < direction < 30:
            motor_direction.stop()
        else:
            if direction >= 0:
                motor_direction.forward(direction+30)
            else:
                motor_direction.backwards((-1*direction)+30)

        if accel > 0 and reverse == 0:
            motor_traction.forward(accel)

        elif accel == 0 and reverse > 0:
            motor_traction.backwards(reverse)
        else:
            motor_traction.stop()

        #conn.sendall(data)