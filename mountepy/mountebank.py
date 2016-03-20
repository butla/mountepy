"""
Abstractions representing aspects of Mountebank.
"""

import collections
import time

import dateutil.parser
import port_for
import requests

from .http_service import HttpService
from .mb_mgmt import get_mb_command


class Mountebank(HttpService):
    """Manages Mountebank instance on localhost. Can start and stop the process.

    Args:
        port (int): Port on which Mountebank will listen for impostor configuration commands.
            If not provided then a random free port will be selected.
    """

    def __init__(self, port=None):
        super().__init__(get_mb_command() + ['--mock', '--port', '{port}'], port)
        self._imposters_url = 'http://localhost:{}/imposters'.format(self.port)

    def add_imposter(self, imposter_cfg):
        """Adds a HTTP service stub (imposter) to Mountebank instance.

        Args:
            imposter_cfg (dict): JSON with Mountebank configuration for an impostor.
                Consult Mountebank documentation.

        Returns:
            `Imposter`: The created service stub.
        """
        resp = requests.post(self._imposters_url, json=imposter_cfg)
        resp.raise_for_status()
        return Imposter(self.port, imposter_cfg['port'])

    def add_imposter_simple(self, port=None, method='GET',  # pylint: disable=too-many-arguments
                            path='/', status_code=200, response=''):
        """Adds an imposter with a single HTTP service stub to Mountebank instance.
        Takes a simplified configuration.

        Args:
            port (int): Port the imposter will listen on. If none, a random port will be selected.
            method (str): HTTP method that the imposter will wait for. GET by default.
            path (str): HTTP path the imposter will wait for. '/' by default.
            status_code (int): HTTP status code the imposter will return. 200 by default.
            response (str): body of the imposters response. Empty string by default.

        Returns:
            `Imposter`: The newly created imposter.
        """
        if port is None:
            port = port_for.select_random()

        return self.add_multi_stub_imposter_simple(
            port,
            [HttpStub(method, path, status_code, response)])

    def add_multi_stub_imposter_simple(self, port, stubs):
        """Adds a Mountebank imposter with multiple HTTP stubs on one port.
        Takes a simplified configuration in comparison to `add_imposter`.

        Args:
            port (int): Port the imposter will listen on.
            stubs (list[`HttpStub`]): HTTP stubs to be created on the port.

        Returns:
            `Imposter`: The newly created imposter.
        """
        imposter_config = {
            'port': port,
            'protocol': 'http',
            'stubs': []
        }

        for stub in stubs:
            stub_json = {
                'responses': [
                    {
                        'is': {
                            'statusCode': stub.status_code,
                            'headers': {
                                'Content-Type': 'application/json'
                            },
                            'body': stub.response
                        }
                    }
                ],
                'predicates': [
                    {
                        'and': [
                            {
                                'equals': {
                                    'path': stub.path,
                                    'method': stub.method,
                                }
                            },
                        ]
                    }
                ]
            }
            imposter_config['stubs'].append(stub_json)
        return self.add_imposter(imposter_config)

    def reset(self):
        """Removes configured imposters (HTTP stubs).
        """
        # TODO add validation
        requests.delete(self._imposters_url)


class Imposter:
    """A Mountebank imposter. It can contain stubs of HTTP, HTTPS, TCP or SMTP services.

    Args:
        mountebank_port (int): Mountebank's localhost port.
        port (int): Port for the imposter..

    Attributes:
        url (str): Management URL for the Imposter.
        port (int): Port on localhost taken by this Imposter.
    """

    def __init__(self, mountebank_port, port):
        self.url = 'http://localhost:{}/imposters/{}'.format(mountebank_port, port)
        self.port = port

    def requests(self):
        """
        Returns:
            list[`ImposterRequest`]: The requests made on the impostor.
        """
        imposter_json = requests.get(self.url).json()
        imposter_requests = []
        for request in imposter_json.get('requests', []):
            imposter_requests.append(ImposterRequest(
                body=request['body'],
                headers=request['headers'],
                method=request['method'],
                path=request['path'],
                query=request['query'],
                request_from=request['requestFrom'],
                timestamp=dateutil.parser.parse(request['timestamp']),
            ))
        return imposter_requests

    def wait_for_requests(self, count=1, timeout=5.0):
        """Wait until a number of requests arrive to the imposter.

        Args:
            count (int): How many requests to wait for.
            timeout (float): How long to wait for requests.

        Returns:
            list[`ImposterRequest`]: The requests made on the impostor.
        """
        start_time = time.perf_counter()
        while True:
            received_requests = self.requests()
            if len(received_requests) >= count:
                return received_requests
            else:
                time.sleep(0.01)
                if time.perf_counter() - start_time >= timeout:
                    raise TimeoutError('Waited too long for requests on stub.')

    def destroy(self):
        """Deletes this `Imposter` from Mountebank.
        This object cannot be used afterwards.
        """
        requests.delete(self.url)


ImposterRequest = collections.namedtuple(
    'ImposterRequest',
    'body, headers, method, path, query, request_from, timestamp')
ImposterRequest.__doc__ = """Data of a request made on an imposter.

Attributes:
    body (str): Request's body. Can be any valid JSON (this includes raw values)
    headers (dict): HTTP headers.
    method (str): HTTP method.
    path (str): Request's path (e.g. "/bla/1" or "/").
    query (dict): Query arguments (after "?" in a URL).
    request_from (str): Request's source address.
    timestamp (`datetime.datetime`): Time at which the request was made.
"""

HttpStub = collections.namedtuple('HttpStub', ['method', 'path', 'status_code', 'response'])
HttpStub.__doc__ = """A configuration for a simple Mountebank impostor, not including the port.

Attributes:
    method (str): HTTP method to which the stub will answer.
    path (str): Request's path (e.g. "/bla/1" or "/")
    status_code (int): Status code that will be returned by the stub.
    response (str): Stub will send it in response to a request matching other parameters.
"""
