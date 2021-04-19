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


count_of_users_devices = 3


@events.test_start.add_listener
def on_test_start(**kwargs):
    gh_http_client = GhHttpClient.GhApi()
    token = gh_http_client.login_to_scc()
    if not gh_http_client.get_feature_by_name(token):
        print("There is not feature. Creating feature")
        gh_http_client.create_feature(token)
    else:
        print("There is a feature.")
    gh_http_client.generate_user(token=token, user_count=count_of_users_devices,
                                 feature=gh_http_client.get_feature_by_name(token)[0])
    gh_http_client.generate_devices(token=token, guid_count=count_of_users_devices)
    gh_http_client.assign_generated_device_user(number_for_assign=count_of_users_devices)


class SenderMsg(SequentialTaskSet):

    @task
    def send_message(self):
        print("Mqtt start")
        start_time = time.time()

        try:
            # GhMqttClient.SendMsg().send_raw_at(self.guid, -1, 0.0, 0.0, 0.0, [])
            GhMqttClient.SendMsg().generated_device_send_raw(number=count_of_users_devices, user_id=-1, x=0.0,
                                                             y=0.0, z=0.0, ble=[])
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
