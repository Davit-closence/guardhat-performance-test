import time

from RandomWordGenerator import RandomWord
import requests
import json
import random
import uuid


class GhApi:
    scc_url = "http://localhost"
    base_scc_url = "http://localhost/api-gw/kyra/1.0"
    grant_type = "password"
    username = "sccadmin"
    password = "KyraSccAdminPassword"
    client_secret = "66eb512c-81ba-4025-8ff7-be580db0bde8"
    client_id = "scc-web-app"
    guid = "a0581ddb-ea05-4d45-9df3-6663806f4111"

    guid_list = []
    user_id_list = []

    def generate_word(self, number):
        return RandomWord(max_word_size=number).generate()

    def rnd_uuid(self, guid_count):
        for i in range(guid_count):
            self.guid_list.append(uuid.uuid4())

    def login_to_scc(self):
        url = f"{self.scc_url}/oauth2/token"
        payload = f"grant_type={self.grant_type}&" \
                  f"username={self.username}&" \
                  f"password={self.password}&" \
                  f"client_secret={self.client_secret}&" \
                  f"client_id={self.client_id}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(url, headers=headers, data=payload)
        access_token = "Bearer " + response.json()["access_token"]
        return access_token

    def create_user(self, token):
        url = f"{self.base_scc_url}/users"
        headers = {
            "Authorization": f"{token}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, data=self.build_user_json())
        if response.ok:
            print("The user is created")
        else:
            print("The user not is created")
        return response.text

    def generate_user(self, token, user_count):
        for x in range(user_count):
            self.user_id_list.append(self.create_user(token))
        print(f"Generated users with {user_count} count. User IDs= {self.user_id_list}")

    def create_feature(self, token):
        url = f"{self.base_scc_url}/features"
        payload = {}
        files = [
            ('featureGeoJSON',
             ('feature.json', open('/Users/davitarzumanyan/Desktop/feature.json', 'rb'), 'application/json'))
        ]
        headers = {
            "Authorization": f"{token}"
        }

        response = requests.post(url, headers=headers, data=payload, files=files)
        if response.ok:
            print("The feature is created")
        else:
            print("The feature not is created")
        return response.text

    def create_device(self, token, guid):
        url = f"{self.base_scc_url}/devices"
        headers = {
            "Authorization": f"{token}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers,
                                 data=self.build_device_json(device_type="Communicator Hat", guid=guid))

        if response.ok:
            print("The device is created")
        else:
            print("The device not is created")
        return response.text

    def generate_devices(self, token, guid_count):
        for count in range(guid_count):
            self.rnd_uuid(guid_count=guid_count)
            self.create_device(token=token, guid=self.guid_list[count])
        print(f"Generated devices with {guid_count} count. Guids= {self.guid_list}")

    def build_device_json(self, guid, device_type):
        return json.dumps({
            "name": f"{self.generate_word(10)}",
            "guid": f"{guid}",
            "tagAddress": f"{random.randint(10, 99)}:"
                          f"{random.randint(10, 99)}:"
                          f"{random.randint(10, 99)}:"
                          f"{random.randint(10, 99)}:"
                          f"{random.randint(10, 99)}:"
                          f"{random.randint(10, 99)}",
            "serialNo": f"{random.randint(1000, 10000)}",
            "deviceType": {
                "id": 6,
                "name": f"{device_type}",
                "ableToSendPowerOff": True,
                "firmwares": [],
                "configurations": []
            },
            "enabled": True
        })

    def assign_device_user(self, guid, user_id):
        url = f"{self.scc_url}:8080/kyra-platform-app/rest/v1/device-users/devices/{guid}/users/{user_id}/permanent"
        response = requests.post(url)
        if response.ok:
            print("The device  is assigned to user")
        else:
            print("The device not is assigned to user")
        return response.text

    def build_user_json(self):
        return json.dumps({
            "userName": f"user_name_{self.generate_word(10)}",
            "sysUser": False,
            "hatUser": True,
            "enabled": True,
            "userProfile": {
                "firstName": f"first_name_{self.generate_word(10)}",
                "lastName": f"last_name_{self.generate_word(10)}",
                "employeeId": f"EMP-444455{random.randint(1000, 5000)}",
                "userTitle": "SQA_Dave",
                "fulltimeEmployee": True,
                "phone": f"+23423{random.randint(1000, 5000)}",
                "email": "test@email.test",
                "companyId": None,
                "site": None,
                "department": None
            },
            "userCredentials": {
                "enabled": True,
                "sipUsername": f"sip_username_{self.generate_word(10)}",
                "sipPassword": "SQA_Dave"
            }
        })
