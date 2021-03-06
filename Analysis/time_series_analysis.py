# importing all required libraries
import machine
from tcs34725 import tcs3472
import time
import json
import network
from umqttsimple import MQTTClient


# colour sensor config
bus = machine.I2C(sda=machine.Pin(4), scl=machine.Pin(5)) # adjust pin numbers as per hardware
tcs = tcs3472(bus, address=0x29)


# servo motors config
servo_gate = machine.PWM(machine.Pin(14), freq=50, duty=90)

def gate():
    servo_gate.duty(120)
    time.sleep_ms(320)
    servo_gate.duty(90)


# Amazon Web Services config
CERT_FILE = "/cert/cert.der"
KEY_FILE = "/cert/private.der"

MQTT_CLIENT_ID = 'esp8266'
MQTT_PORT = 8883

MQTT_TOPIC = 'Lichtverhaeltnis_Dunkel_Blau'

MQTT_HOST = '<host>' # change host

def pub_msg(mqtt_client, msg):
    try:
        mqtt_client.publish(MQTT_TOPIC, msg)
        print("Sent: " + msg)
    except Exception as e:
        print("Exception publish: " + str(e))
        raise

def create_dummy_msg():
    message = {
        "RGB": tcs.rgb(),
        "Light": tcs.light(),
        "Brightness": tcs.brightness()
    }
    return json.dumps(message)

def connect_mqtt():
    try:
        with open(KEY_FILE, "r") as f:
            key = f.read()

        print("Got Key")

        with open(CERT_FILE, "r") as f:
            cert = f.read()

        print("Got Cert")

        mqtt_client = MQTTClient(
            client_id=MQTT_CLIENT_ID,
            server=MQTT_HOST,
            port=MQTT_PORT,
            keepalive=5000,
            ssl=True,
            ssl_params={"cert": cert, "key": key, "server_side": False},
        )
        mqtt_client.connect()
        print("MQTT Connected")

        return mqtt_client

    except Exception as e:
        print("Cannot connect MQTT: " + str(e))
        raise

def connect_wlan():

    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('<wifi>', '<wifi password>') # change wifi and password
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
try:
    connect_wlan()
    print("Connecting MQTT")
    mqtt_client = connect_mqtt()

    print("Publishing data")
    
    # running the machine
    for _ in range(50):
        pub_msg(mqtt_client, create_dummy_msg())
        gate()
        time.sleep(3)
    print("Done")
except Exception as e:
    print(str(e))
