import os.path
import subprocess
import sys
import threading

import port_for
import pytest
import requests

from mountepy import HttpService, ServiceGroup

# starting Python 3 (current Python) HTTP server on a port, that will be set by HttpService
TEST_SERVICE_COMMAND = [sys.executable, '-m', 'http.server', '{port}']


def test_service_base_url():
    service = HttpService('fake-command', 12345)
    assert service.url == 'http://localhost:12345'


def test_service_start_and_cleanup():
    service_port = port_for.select_random()

    with HttpService(TEST_SERVICE_COMMAND, service_port) as service:
        assert requests.get(service.url).status_code == 200

    with pytest.raises(requests.exceptions.ConnectionError):
        requests.get(service.url)


def test_service_single_string_command():
    single_string_command = 'mb'
    service = HttpService(single_string_command, 12345)
    assert service._process_command == single_string_command


def test_service_start_timeout_and_cleanup():
    test_service = HttpService(TEST_SERVICE_COMMAND)

    with pytest.raises(TimeoutError):
        test_service.start(timeout=0.001)
    test_service._service_proc.wait(timeout=3.0)


def test_service_env_config():
    example_service_path = os.path.join(os.path.dirname(__file__), 'example_service.py')
    service = HttpService(
        [sys.executable, example_service_path],
        port=port_for.select_random(),
        env={'TEST_APP_PORT': '{port}'})

    with service:
        assert requests.get(service.url).text == 'Just some text.'


def test_timeout_error_on_too_long_service_stop():
    unstoppable_service_path = os.path.join(os.path.dirname(__file__), 'unstoppable_service.py')
    service = HttpService(
        [sys.executable, unstoppable_service_path],
        port=port_for.select_random(),
        env={'TEST_APP_PORT': '{port}'})

    service.start()
    try:
        with pytest.raises(subprocess.TimeoutExpired):
            service.stop(0.001)
    finally:
        # cleanup by ending the service process
        service._service_proc.terminate()


@pytest.mark.parametrize('service_env, parent_env, final_env', [
    ({'bla': 'aaa'}, {'something': '123', 'bla': 'bbb'}, {'something': '123', 'bla': 'aaa'}),
    (None, {'asd': 'qwe'}, {'asd': 'qwe'}),
])
def test_service_env_from_parent(service_env, parent_env, final_env):
    os.environ = parent_env
    service = HttpService('some fake command', env=service_env)
    assert service._service_env == final_env


def test_service_env_without_parent():
    service_env = {'bla': 'aaa'}
    service = HttpService('some fake command', env=service_env, copy_parent_env=False)
    assert service._service_env == service_env


def test_service_group_start():
    test_service_1 = HttpService(TEST_SERVICE_COMMAND)
    test_service_2 = HttpService(TEST_SERVICE_COMMAND)

    with ServiceGroup(test_service_1, test_service_2):
        assert requests.get(test_service_1.url).status_code == 200
        assert requests.get(test_service_2.url).status_code == 200


class FakeHttpService:

    """
    Has start and stop methods like `mountepy.HttpService` but a different context manager logic.
    """

    def __init__(self, lock_start=False, lock_stop=False):
        self._lock_start = lock_start
        self._lock_stop = lock_stop
        self._stalling_lock = threading.Lock()

    def __enter__(self):
        self._stalling_lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stalling_lock.release()

    def start(self):
        if self._lock_start:
            self._stalling_lock.acquire()

    def stop(self):
        if self._lock_stop:
            self._stalling_lock.acquire()


def test_service_group_start_timeout():
    with FakeHttpService(lock_start=True) as service_1, FakeHttpService(lock_start=True) as service_2:
        services = ServiceGroup(service_1, service_2)
        with pytest.raises(TimeoutError):
            services.start(timeout=0.00000001)


def test_service_group_stop_timeout():
    with FakeHttpService(lock_stop=True) as service_1, FakeHttpService(lock_stop=True) as service_2:
        services = ServiceGroup(service_1, service_2)
        services.start()
        with pytest.raises(TimeoutError):
            services.stop(timeout=0.00000001)