import paho.mqtt.client as mqtt
import time
from datetime import datetime
import json

from dateutil import tz

import GhHttpClient
import Log

date_format = '%Y-%m-%d %H:%M:%S.%f'
seq_num = round(time.time() * 1000)


class SendMsg:
    log = Log.Log()
    gh = GhHttpClient.GhApi()
    broker = "tcp://localhost:1883"
    port = 1883
    topic = "guardhat/+/outbound/#"
    client_id = "kyra_integration"
    username = 'guardhat'
    password = 'xrJGwCDnj'
    # credentials

    received_messages = []

    def __init__(self):
        self.client = mqtt.Client(client_id=self.client_id,
                                  clean_session=False,
                                  userdata=None,
                                  protocol=mqtt.MQTTv311,
                                  transport="tcp")

        self.client.username_pw_set(username=self.username, password=self.password)

        self.client.connect("localhost", 1883, 60)
        # self.client.subscribe(topic=self.topic, qos=1)
        # self.client.on_message = self.on_message
        self.client.loop_start()

    def send(self, channel, message):
        self.client.publish(topic=channel, payload=message, qos=0, retain=False, properties=None)

    def receive(self, channel):
        self.client.subscribe(topic=channel, qos=1)

    def receive_message(self, number):
        for count in range(number):
            self.receive(channel=f"guardhat/{self.gh.guid_list[count]}/outbound/#")
            self.log.log_info(f"Subscribe the topic= guardhat/{self.gh.guid_list[count]}/outbound/#")

    def raw_event(self, user_id, x=-83.33097, y=42.561265, z=50.0, ble=[]):
        return self.message(user_id=user_id, timestamp=self.timestamp(), x=x, y=y, z=z, ble=ble)

    def next_seq(self):
        global seq_num
        seq_num += 1
        return seq_num

    def timestamp(self):
        return datetime.now(tz.UTC).isoformat()

    def message(self, guid, user_id,
                timestamp,
                x=-83.33097,
                y=42.561265,
                z=50.0,
                ble=[],
                msg_code="",
                activated=False,
                event_type="RAW"):
        self.log.log_info(f"Message contains Timestamp= {self.timestamp()} Sequence= {self.next_seq()} Guid= {guid}")
        return json.dumps(
            {
                "header": {
                    "ackReqd": False,
                    "activated": activated,
                    "guid": guid,
                    "msgCode": msg_code,
                    "priority": 3,
                    "sequence": self.next_seq(),
                    "staleData": False,
                    "synthetic": False,
                    "timestamp": timestamp,
                    "type": event_type,
                    "userId": user_id
                },
                "payload": {
                    "ctx": {
                        "accel": {
                            "x": 0.0,
                            "y": 0.0,
                            "z": 0.0
                        },
                        "altitude": 0.0,
                        "batt": 8,
                        "gyro": {
                            "x": 0.0,
                            "y": 0.0,
                            "z": 0.0
                        },
                        "location": {
                            "blackout": False,
                            "resolvedLoc": {
                                "coordinates": [
                                    x,
                                    y,
                                    z
                                ],
                                "crs": {
                                    "properties": {},
                                    "type": "name"
                                },
                                "type": "Point"
                            },
                            "trustedMethod": "GPS"
                        },
                        "mag": {
                            "x": 0.0,
                            "y": 0.0,
                            "z": 0.0
                        },
                        "ble": ble
                    },
                    "env": {
                        "atmPressure": -1000.0,
                        "gas": [
                            {
                                "ppm": -1000.0,
                                "type": "CO"
                            }
                        ],
                        "humidity": -1000.0,
                        "noise": -1000.0,
                        "temp": -1000.0
                    },
                    "ext": {}
                }
            }
        )

    def next_received(self):
        if len(self.received_messages) > 0:
            return self.received_messages.pop(0)
        else:
            return None

    def on_message(self, client, userdata, message):
        self.received_messages.append(message)
        recd_message = str(message.payload.decode("utf-8"))
        self.log.log_info(f"\nMessage Received at {datetime.now().strftime(date_format)} - {recd_message}")

    def send_raw_at(self, activated, guid, user_id, x, y, z, ble=[]):
        self.send(channel=f"guardhat/{guid}/inbound/raw",
                  message=self.message(activated=activated, guid=guid, user_id=user_id, timestamp=self.timestamp(), x=x,
                                       y=y, z=z, ble=ble))

    def send_sos(self, activated, guid, user_id, x, y, z, ble=[]):
        self.send(channel=f"guardhat/{guid}/inbound/notif",
                  message=self.message(guid=guid, user_id=user_id, event_type="EVENT", msg_code="EX000",
                                       activated=activated, timestamp=self.timestamp(), x=x, y=y, z=z, ble=ble))

    def generated_device_send_sos(self, activated, number, user_id, x, y, z, ble=[]):
        for count in range(number):
            self.send_sos(activated=activated, guid=self.gh.guid_list[count], user_id=user_id, x=x, y=y, z=z, ble=ble)
            self.log.log_info(
                f"Sending sos event Guid= {self.gh.guid_list[count]} activated= {activated} x= {x},y= {y}, z= {z}")

    def generated_device_send_raw(self, activated, number, user_id, x, y, z, ble=[]):
        for count in range(number):
            self.send_raw_at(activated=activated, guid=self.gh.guid_list[count], user_id=user_id, x=x, y=y, z=z,
                             ble=ble)
            self.log.log_info(
                f"Sending raw message Guid= {self.gh.guid_list[count]} activated= {activated} x= {x},y= {y}, z= {z}")
