from locust import User, between, task, SequentialTaskSet, events
import GhMqttClient
import GhHttpClient
import time


class LocustError(Exception):
    pass


class TimeoutError(ValueError):
    pass


class ConnectError(Exception):
    pass


class DisconnectError(Exception):
    pass


def time_delta(t1, t2):
    return int((t2 - t1) * 1000)


count_of_users_devices = 10

coordinatesZoneInSite = [[-83.050040585037, 42.33595364286762],
                         [-83.04937561932185, 42.335065477679194],
                         [-83.04836874931688, 42.33573476666646],
                         [-83.04955084790198, 42.33621851006674],
                         [-83.050040585037, 42.33595364286762]
                         ]


@events.test_start.add_listener
def on_test_start(**kwargs):
    gh_http_client = GhHttpClient.GhApi()
    token = gh_http_client.login_to_scc()
    if not gh_http_client.get_feature_by_name(token):
        print("There is not feature. Creating feature")
        gh_http_client.create_feature(token)
    else:
        print("There is a feature.")

    between(1, 2)
    gh_http_client.generate_user(token=token, user_count=count_of_users_devices,
                                 feature=gh_http_client.get_feature_by_name(token)[0])
    gh_http_client.generate_devices(token=token, guid_count=count_of_users_devices)
    gh_http_client.assign_generated_device_user(number_for_assign=count_of_users_devices)
    gh_http_client.create_zone(token=token, name="Tst", coordinates=coordinatesZoneInSite,
                               zone_type=gh_http_client.get_zone_type_by_name(token=token, zone_type_name="GEOFENCE"),
                               users=[], authorized_beacons=[])


class SenderMsg(SequentialTaskSet):

    @task
    def send_message(self):
        print("Mqtt start")
        start_time = time.time()

        try:
            GhMqttClient.SendMsg().generated_device_send_raw(number=count_of_users_devices, user_id=-1,
                                                             x=-83.049845649704,
                                                             y=42.335889840062066, z=1.0, ble=[])
        except:
            events.request_failure.fire(
                request_type="MQTT",
                name='connect',
                response_time=time_delta(start_time, time.time()),
                exception=ConnectError("Could not connect to host:[...]"),
                response_length=0
            )

    @task
    def exit_task_execution(self):
        self.interrupt()


class MyUser(User):
    wait_time = between(1, 2)
    tasks = [SenderMsg]
