import time
import datetime
import paho.mqtt.client as paho

host = "research.guardhat.net"
amq_username = "ghmq"
amq_password = "EFk9r4FF"
date_format = '%Y-%m-%d %H:%M:%S.%f'


def on_message(client, userdata, message):
    time.sleep(1)
    recd_message = str(message.payload.decode("utf-8"))
    print(f"\nMessage Received at {datetime.datetime.now().strftime(date_format)} - {recd_message}")


def mqtt_on_connect(client, userdata, flags, mqtt_rc):
    if mqtt_rc == 0:
        print(f"MQTT connection successful with return code {mqtt_rc}")
    else:
        print(f"MQTT connection failed with return code {mqtt_rc}")


client = paho.Client("AMQ Subscriber")
client.username_pw_set(amq_username, amq_password)
client.on_connect = mqtt_on_connect
client.on_message = on_message

print("Connecting to ", host)
client.connect(host)
client.loop_start()
print("Subscribing to inbound topics...")
client.subscribe("guardhat/+/inbound/#")

while True:
    time.sleep(180)
