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
ramp = machine.PWM(machine.Pin(12), freq=50, duty=80)
gate = machine.PWM(machine.Pin(14), freq=50, duty=90)

def servos(x):
    ramp.duty(x)
    time.sleep(1)
    gate.duty(120)
    time.sleep_ms(300)
    gate.duty(90)
    time.sleep_ms(700)
    ramp.duty(80)

    
# Amazon Web Services config
CERT_FILE = "/cert/cert.der"
KEY_FILE = "/cert/private.der"

MQTT_CLIENT_ID = 'esp8266'
MQTT_PORT = 8883

MQTT_TOPIC = 'Effizienzanalyse_neu'

MQTT_HOST = '<host>' # change host

def convert_to_iso(datetime):
    y, m, d, _, h, mi, s, _ = datetime
    return "{}-{:02d}-{:2d}T{:02d}:{:02d}:{02d}".format(y, m, d, h, mi, s)

def pub_msg(mqtt_client, msg):
    try:
        mqtt_client.publish(MQTT_TOPIC, msg)
        print("Sent: " + msg)
    except Exception as e:
        print("Exception publish: " + str(e))
        raise

def create_dummy_msg():

    iso_timestamp = convert_to_iso(machine.RTC().datetime())
    message = {
        "RGB": tcs.rgb(),
        "Light": tcs.light(),
        "Brightness": tcs.brightness(),
        'Timestamp': convert_to_iso()
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
    for _ in range(300):
        pub_msg(mqtt_client, create_dummy_msg())

        # measure RGB values
        measured_value_red = tcs.rgb()[0]
        measured_value_green = tcs.rgb()[1]
        measured_value_blue = tcs.rgb()[2]

        # colour: RED
        if 195 < measured_value_red < 215 and 32 < measured_value_green < 65 and 35 < measured_value_blue < 65:
            print(tcs.rgb())
            print('Das Objekt ist rot')
            servos(30)

        # colour: GREEN
        elif 75 < measured_value_red < 115 and 110 < measured_value_green < 130 and 65 < measured_value_blue < 100:
            print(tcs.rgb())
            print('Das Objekt ist grün')
            servos(60)

        # colour: BLUE
        elif 80 < measured_value_red < 115 and 85 < measured_value_green < 110 and 90 < measured_value_blue < 120:
            print(tcs.rgb())
            print('Das Objekt ist blau')
            servos(100)

        # colour: DEFICIENT ITEM
        else:
            print(tcs.rgb())
            print('Die Farbe konnte nicht ermittelt werden')
            servos(130)

        time.sleep(10)

    print("Done")

except Exception as e:
    print(str(e))
