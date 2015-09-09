import logging
import requests
import socket
import subprocess
import time


from urllib.parse import urlparse


def _host_and_port_from_url(url):
    """
    Extracts hostname and port from an url
    :param url: An URL
    :return: Hostname and port from the url.
    :rtype (str, int):
    """
    parsed_url = urlparse(url)
    host, port = parsed_url.netloc.split(':')
    return host, int(port)


def _wait_for_endpoint(url, timeout=5.0):
    """
    Waits for the HTTP endpoint to appear by trying to connect to it with TCP.
    :param str url: Service url, e.g. "http://localhost:2525/imposters". Port needs to be specified.
    :rtype: None
    :raises TimeoutError: If the service doesn't start in time.
    """
    host, port = _host_and_port_from_url(url)

    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((host, port)):
                break
        except ConnectionRefusedError:
            time.sleep(0.001)
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError('Waited too long for the endpoint to get up.')


class Mountebank:

    """
    Manages Mountebank instance. Can start and stop the process.
    """

    def __init__(self, mountebank_command = 'mb'):
        self.hostname = 'localhost'
        self.port = 2525
        self._imposters_url = 'http://{}:{}/imposters'.format(self.hostname, self.port)
        self._mountebank_command = mountebank_command
        self._mountebank_proc = None

    def add_imposter(self, imposter_cfg):
        """
        :param dict imposter_cfg: Mountebank configuration for an impostor.
        :rtype: None
        """
        resp = requests.post(self._imposters_url, json=imposter_cfg)
        resp.raise_for_status()

    def start(self, timeout=5.0):
        """
        Starts Mountebank process and waits for it to start accepting connections.
        :param timeout: How long to wait before raising an error.
        :rtype: None
        :raises TimeoutError: If Mountebank didn't start in time.
        """
        self._mountebank_proc = subprocess.Popen(self._mountebank_command)
        try:
            _wait_for_endpoint(self._imposters_url, timeout=timeout)
        except Exception:
            logging.exception("Mountebank didn't start")
            self.stop()
            raise

    def stop(self):
        self._mountebank_proc.kill()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
