# importing all required libraries
import machine, time, network, urequests
from tcs34725 import tcs3472
from hx711 import HX711
import ussl as ssl
try:
    import usocket as socket
except:
    import socket

    
# colour sensor config
bus = machine.I2C(sda=machine.Pin(4), scl=machine.Pin(5))  # adjust pin numbers as per hardware
tcs = tcs3472(bus, address=0x29)


# servo motors config
ramp = machine.PWM(machine.Pin(12), freq=50, duty=80)
gate = machine.PWM(machine.Pin(14), freq=50, duty=90)

def servo_motors(x):
    ramp.duty(x)
    time.sleep(1)
    gate.duty(120)
    time.sleep_ms(300)
    gate.duty(90)
    time.sleep_ms(2500)
    ramp.duty(80)


# load cells config
machine.freq(160000000)
driver = HX711(d_out=15, pd_sck=13)
driver.channel = HX711.CHANNEL_A_64


# calibration of the scale
def weight_of_SLC(zero_point, factor):
    int(((driver.read() * (-0.01)) - zero_point) * (factor))  # 55 g / 10 items

    
# ThinkSpeak config
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('<wifi>', '<wifi password>') # change wifi and password

HTTP_HEADERS = {'Content-Type': 'application/json'}
API_THINGSPEAK_HOST = 'api.thingspeak.com'
API_THINGSPEAK_PORT = 443
THINGSPEAK_WRITE_KEY = '<thinkspeak key>' # change key

counter_red = 0
counter_green = 0
counter_blue = 0
weight_of_SLC = 0


# running the colour sorting machine / real-time dashboard with ThinkSpeak
while True:
    # measuring RGB, light and brightness
    measured_value_red = tcs.rgb()[0]
    measured_value_green = tcs.rgb()[1]
    measured_value_blue = tcs.rgb()[2]
    light = tcs.light()
    brightness = tcs.brightness()

    # colour: RED
    if 195 < measured_value_red < 215 and 32 < measured_value_green < 65 and 35 < measured_value_blue < 65:
        print('Colour of item: Red.')
        servo_motors(30)
        counter_red += 1

    # colour: GREEN
    elif 75 < measured_value_red < 115 and 110 < measured_value_green < 130 and 65 < measured_value_blue < 100:
        print('Colour of item: Green.')
        servo_motors(65)
        counter_green += 1

    # colour: BLUE
    elif 80 < measured_value_red < 115 and 85 < measured_value_green < 110 and 90 < measured_value_blue < 120:
        print('Colour of item: Blue.')
        servo_motors(100)
        counter_blue += 1

    # colour: DEFICIENT ITEM
    else:
        print('Colour could not be detected / Item is deficient.')
        servo_motors(130)
        weight_of_SLC(2885, -11.5)
    
    
    # sending data to ThinkSpeak
    s = socket.socket()
    ai = socket.getaddrinfo(API_THINGSPEAK_HOST, API_THINGSPEAK_PORT)
    addr = ai[0][-1]
    s.connect(addr)
    s = ssl.wrap_socket(s)
    data = {'field1': weight_of_SLC,
            'field2': counter_red,
            'field3': counter_green,
            'field4': counter_blue,
            'field5': measured_value_red,
            'field6': measured_value_green,
            'field7': measured_value_blue,
            'field8': light}
    request = urequests.post('http://api.thingspeak.com/update?api_key=' + THINGSPEAK_WRITE_KEY, json=data, headers=HTTP_HEADERS)
    request.close()
    
    # measure every five seconds
    time.sleep(5)
