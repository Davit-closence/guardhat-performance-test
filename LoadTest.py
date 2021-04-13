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


@events.test_start.add_listener
def on_test_start(**kwargs):
    guid = "a0581ddb-ea05-4d45-9df3-6663806f4111"
    gh_http_client = GhHttpClient.GhApi
    token = gh_http_client.login_to_scc()
    id_user = gh_http_client.create_user(token)
    gh_http_client.create_device(token)
    gh_http_client.assign_device_user(guid, id_user)
    gh_http_client.create_feature(token)


class SenderMsg(SequentialTaskSet):
    @task
    def send_message(self):
        print("Mqtt start")
        start_time = time.time()

        try:
            GhMqttClient.SendMsg().send_raw_at(-1, 0.0, 0.0, 0.0, [])
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