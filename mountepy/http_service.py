"""
Abstractions for management of HTTP service processes.
"""

import atexit
import concurrent.futures
import logging
import os
import signal
import socket
import subprocess
import time

import port_for


def wait_for_port(port, host='localhost', timeout=5.0):
    """Wait until a port starts accepting TCP connections.

    Args:
        port (int): Port number.
        host (str): Host address on which the port should exist.
        timeout (float): In seconds. How long to wait before raising errors.

    Raises:
        TimeoutError: The port isn't accepting connection after time specified in `timeout`.
    """
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((host, port)):
                break
        except OSError:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError('Waited too long for the port {} on host {} to start accepting '
                                   'connections.'.format(port, host))


class HttpService:
    """Manages a HTTP service instance on localhost. Can start and stop the process.

    Args:
        process_command: Command that will start the service.
            It is a string or a list of strings (like parameters to subprocess.Popen).
            Command strings may contain '{port}' - it will be filled with the provided port.
        port (int): Port on which the service will listen.
            If not provided then the service will run on a random free port.
        env (dict): Environment variables that will be visible for the service process.
            All values of this dictionary must be strings.
            E.g. {'EXAMPLE_VARIABLE_NAME': 'some_example_value'}
            Values may contain '{port}' string - it will be filled with the provided port.
        copy_parent_env (bool): If set to True then environment of the service process will
            contain environment of the parent process updated with `env`.
            If set to False, then only `env` will be set as the service's environment.

    Attributes:
        port (int): Localhost port taken by the service.
        url (int): Address on which the service is available on when it's started.
    """

    def __init__(self, process_command, port=None, env=None, copy_parent_env=True):
        if port is None:
            self.port = port_for.select_random()
        else:
            self.port = port
        self.url = 'http://localhost:{}'.format(self.port)
        self._process_command = self._format_process_command(process_command, self.port)
        self._service_env = self._format_process_env(copy_parent_env, env, self.port)
        self._service_proc = None

    def start(self, timeout=5.0):
        """Starts service process and waits for it to start accepting connections.

        Args:
            timeout (float): How long to wait (in seconds) before raising an error.

        Raises:
            TimeoutError: If the service process didn't start in time.
        """
        self._service_proc = subprocess.Popen(self._process_command, env=self._service_env)
        atexit.register(self.stop)

        try:
            wait_for_port(self.port, timeout=timeout)
        except Exception:
            logging.exception("Service '%s' didn't start", self._process_command)
            self.stop()
            raise

    def stop(self):
        """Closes the service process and wait's for it to close."""
        atexit.unregister(self.stop)
        # Sending SIGINT (ctrl+C) because Python handles it by default.
        # Terminate could also be sent, but if the service process spawned
        # another process, then it would need to intercept SIGTERM if we'd
        # want to have a multiprocess coverage report.
        self._service_proc.send_signal(signal.SIGINT)
        # TODO add timeout and some error
        self._service_proc.wait()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @staticmethod
    def _format_process_command(command, port):
        if not isinstance(command, str):
            return [part.format(port=port) if ('{port}' in part) else part for part in command]
        else:
            return command

    @staticmethod
    def _format_process_env(copy_parent_env, env, port):
        env = env or {}

        formatted_env = env.copy()
        for key, value in env.items():
            if '{port}' in value:
                formatted_env[key] = value.format(port=port)

        if copy_parent_env:
            final_env = os.environ.copy()
            final_env.update(formatted_env)
            return final_env
        else:
            return formatted_env


class ServiceGroup:
    """Manages a group of service processes.
    Can be used to concurrently start or stop more than one service.

    Args:
        *service_processes (list[`HttpService`]): A list of not yet started HTTP services.
    """

    def __init__(self, *service_processes):
        self._services = service_processes
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=7)

    def start(self, timeout=5.0):
        """Starts all the service processes and waits them to start accepting connections.

        Args:
            timeout (float): How long (in seconds) to wait before raising an error.

        Raises:
            TimeoutError: If all of the services didn't start in time.
        """
        start_futures = [self._executor.submit(service.start) for service in self._services]
        results = concurrent.futures.wait(start_futures, timeout=timeout)
        if results.not_done:
            raise TimeoutError('Not all processes started in time.')

    def stop(self, timeout=5.0):
        """
        Stops all the service processes. Waits for full stop.
        Args:
            timeout (float): How long (in seconds) to wait before raising an error.

        Raises:
            TimeoutError: If all of the services didn't stop in time.
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
