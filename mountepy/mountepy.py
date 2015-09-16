import atexit
import concurrent.futures
import logging
import socket
import subprocess
import time

import port_for
import requests


def _wait_for_port(port, host='localhost', timeout=5.0):
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((host, port)):
                break
        except ConnectionRefusedError:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError('Waited too long for the port to start accepting connections.')


class HttpService:

    """
    Manages a HTTP service instance on localhost. Can start and stop the process.
    """

    def __init__(self, process_command, port=None):
        """
        Initializes the object without starting the service process.
        :param process_command: Command that will start the service.
        It is a string or a list of strings (like parameters to subprocess.Popen).
        Command strings may contain '{port}' - it will be filled with the provided port.
        :param int port: Port on which the service will listen.
        If not provided then the service will run on a random free port.
        """
        if port is None:
            self.port = port_for.select_random()
        else:
            self.port = port
        self._process_command = self._format_process_command(process_command, self.port)
        self._service_proc = None

    def start(self, timeout=5.0):
        """
        Starts service process and waits for it to start accepting connections.
        :param float timeout: How long to wait before raising an error.
        :rtype: None
        :raises TimeoutError: If the service process didn't start in time.
        """
        self._service_proc = subprocess.Popen(self._process_command)
        atexit.register(self.stop)

        try:
            _wait_for_port(self.port, timeout=timeout)
        except Exception:
            logging.exception("Service '%s' didn't start", self._process_command)
            self.stop()
            raise

    def stop(self):
        atexit.unregister(self.stop)
        self._service_proc.kill()
        # TODO add timeout and some error
        self._service_proc.wait()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @staticmethod
    def _format_process_command(command, port):
        if type(command) != str:
            return [part.format(port=port) if ('{port}' in part) else part for part in command]
        else:
            return command


class Mountebank(HttpService):

    """
    Manages Mountebank instance on localhost. Can start and stop the process.
    """

    def __init__(self, port=None):
        """
        Initializes the object without starting the service process.
        :param int port: Port on which Mountebank will listen for impostor configuration commands.
        If not provided then a random free port will be selected.
        """
        super().__init__(['mb', '--port', '{port}'], port)
        self._imposters_url = 'http://localhost:{}/imposters'.format(self.port)

    def add_imposter(self, imposter_cfg):
        """
        :param dict imposter_cfg: Mountebank configuration for an impostor.
        :rtype: None
        """
        resp = requests.post(self._imposters_url, json=imposter_cfg)
        resp.raise_for_status()


class ServiceGroup:

    """
    Manages a group of service processes.
    Can be used to concurrently start or stop more than one service.
    """

    def __init__(self, *service_processes):
        """
        :param service_processes: A list of HttpService objects.
        Don't start or stop them individually after passing them here.
        :raises TimeoutError:
        """
        self._services = service_processes
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=7)

    def start(self, timeout=5.0):
        """
        Starts all the service processes and waits them to start accepting connections.
        :param float timeout: How long to wait before raising an error.
        :rtype: None
        :raises TimeoutError: If all of the services didn't start in time.
        """
        start_futures = [self._executor.submit(service.start) for service in self._services]
        results = concurrent.futures.wait(start_futures, timeout=timeout)
        if results.not_done:
            raise TimeoutError('Not all processes started in time.')

    def stop(self, timeout=5.0):
        """
        Stops all the service processes. Waits for full stop.
        :param float timeout: How long to wait before raising an error.
        :rtype: None
        :raises TimeoutError: If all of the services didn't stop in time.
        """
        stop_futures = [self._executor.submit(service.stop) for service in self._services]
        results = concurrent.futures.wait(stop_futures, timeout=timeout)
        if results.not_done:
            raise TimeoutError('Not all processes stopped in time.')

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()