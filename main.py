from machine import Pin, unique_id
from network import WLAN
from time import sleep
from umqtt.simple import MQTTClient
from umqtt.simple import MQTTException
from sys import exit
from os import stat
from json import loads as json_loads
#
import ubinascii

config_file = "ratoni.json"
# Default alerted state is False
alerted = False
config_data = None

mqtt_user = None
mqtt_pass = None

if stat(config_file):
    f = open(config_file, 'r')
    config_data = json_loads(f.read(1024))

if "mqtt_broker" in config_data:
    broker_address = config_data['mqtt_broker']
else:
    broker_address = "iot.eclipse.org"

if "client_id" in config_data:
    client_id = config_data['client_id']
else:
    client_id = ubinascii.hexlify(unique_id())

if "mqtt_user" in config_data:
    mqtt_user = config_data['mqtt_user']

if "mqtt_pass" in config_data:
    mqtt_pass = config_data['mqtt_pass']


if "topic" in config_data:
    mqtt_topic = config_data['topic']
else:
    mqtt_topic = b"ratoni/jail"

if "pin" in config_data:
    pin_id = config_data['pin_id']
else:
    pin_id = 0

pin = Pin(pin_id, Pin.IN, Pin.PULL_UP)

wlan = WLAN()
while not wlan.isconnected():
    print("Waiting for WLAN to be connected...")
    sleep(1)

if mqtt_pass and mqtt_user:
    c = MQTTClient(client_id, broker_address, user=mqtt_user, password=mqtt_pass)
    print("MQTTClient will use user and password")
else:
    c = MQTTClient(client_id, broker_address)
    print("MQTTClient set to anonymous mode")

try:
    c.connect()
except MQTTException:
    print("[CRITICAL] Error connecting to MQTT broker... May have a problem with credentials! (MQTTException")
    exit(1)
except TypeError:
    print("[CRITICAL] Error connecting to MQTT broker... May have a problem with credentials! (TypeError)")
    exit(1)

print("MQTTClient seems to be fine, waiting for some mice attack!")

while True:
    #print("Pin is:" + str(pin.value()))
    if not pin.value():
        print("Circuit is closed. We might have a mouse!")
        if not alerted:
            c.publish(mqtt_topic, "ON")
            alerted = True
    sleep(2)
