import paho.mqtt.client as mqtt
import time
from datetime import datetime
import json
import GhHttpClient


class SendMsg:
    broker = "tcp://localhost:1883"
    port = 1883
    guid = "a0581ddb-ea05-4d45-9df3-6663806f4111"
    topic = f"guardhat/${guid}/outbound/#"
    client_id = "kyra_integration"
    username = 'guardhat'
    password = 'xrJGwCDnj'
    # credentials
    seq_num = round(time.time() * 1000)

    def __init__(self):
        self.client = mqtt.Client(client_id=self.client_id,
                                  clean_session=False,
                                  userdata=None,
                                  protocol=mqtt.MQTTv311,
                                  transport="tcp")

        self.client.username_pw_set(username=self.username, password=self.password)

        self.client.subscribe(topic=self.topic, qos=1)
        self.client.connect("localhost", 1883, 60)

    def send(self, channel, message):
        self.client.publish(topic=channel, payload=message, qos=0, retain=False, properties=None)

    def raw_event(self, user_id, x=-83.33097, y=42.561265, z=50.0, ble=[]):
        return self.message(user_id=user_id, timestamp=self.timestamp(), x=x, y=y, z=z, ble=ble)

    def next_seq(self):
        self.seq_num += 1
        return self.seq_num

    def timestamp(self):
        return datetime.now().isoformat()

    def message(self, user_id,
                timestamp,
                x=-83.33097,
                y=42.561265,
                z=50.0,
                ble=[],
                msg_code="",
                activated=False,
                event_type="RAW"):
        return json.dumps(
            {
                "header": {
                    "ackReqd": False,
                    "activated": activated,
                    "guid": self.guid,
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

    def send_raw_at(self, guid, user_id, x, y, z, ble=[]):
        self.send(channel=f"guardhat/{guid}/inbound/raw",
                  message=self.message(user_id=user_id, timestamp=self.timestamp(), x=x, y=y, z=z, ble=ble))

    def generated_device_send_raw(self, number, user_id, x, y, z, ble=[]):
        gh = GhHttpClient.GhApi()
        for count in range(number):
            self.send_raw_at(guid=gh.guid_list[count], user_id=user_id, x=x, y=y, z=z, ble=ble)
            print(f"Sending raw message Guid= {gh.guid_list[count]}")


# sender = SendMsg()
# for x in range(39):
#     sender.send_raw_at(-1, 0.0, 0.0, 0.0, [])
#     time.sleep(1)
