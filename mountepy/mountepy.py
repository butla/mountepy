import os
import requests
import subprocess
import time
import socket
import logging

from urllib.parse import urlparse


def _wait_for_endpoint(url, timeout=5.0):
    """
    Waits for the HTTP endpoint to appear by trying to connect to it with TCP.
    :param str url: Service url, e.g. "http://localhost:2525/imposters". Port needs to be specified.
    :rtype: None
    :raises TimeoutError: If the service doesn't start in time.
    """
    parsed_url = urlparse(url)
    host, port_str = parsed_url.netloc.split(':')
    port = int(port_str)

    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((host, port)):
                break
        except ConnectionRefusedError:
            time.sleep(0.001)
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError('Waited too long fot the process')


class Mountebank:

    def __init__(self):
        self._hostname = 'localhost'
        self._port = 2525
        self._imposters_url = 'http://{}:{}/imposters'.format(self._hostname, self._port)

    def add_imposter(self, imposter_cfg):
        """
        :param dict imposter_cfg: Mountebank configuration for an impostor.
        :rtype: None
        """
        resp = requests.post(self._imposters_url, json=imposter_cfg)
        resp.raise_for_status()

    def start(self):
        mb_proc = subprocess.Popen('mb')
        try:
            _wait_for_endpoint(self._imposters_url)
        except Exception:
            logging.exception("Mountebank didn't start")
            self.stop()
            raise

    def stop(self):
        subprocess.check_call(['mb', 'stop'])

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
