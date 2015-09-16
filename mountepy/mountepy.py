import atexit
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
            time.sleep(0.001)
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
        :raises TimeoutError: If Mountebank didn't start in time.
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
