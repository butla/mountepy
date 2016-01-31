"""
Abstractions representing aspects of Mountebank.
"""

import collections
import time

import port_for
import requests

from mountepy import HttpService
from mountepy.mb_mgmt import get_mb_command


class Imposter:

    """
    Represents a Mountebank imposter.
    """

    def __init__(self, mountebank_port, port):
        self._url = 'http://localhost:{}/imposters/{}'.format(mountebank_port, port)
        self.port = port

    def requests(self):
        """
        :return: The requests made on the impostor.
        :rtype: list[`ImposterRequest`]
        """
        imposter_json = requests.get(self._url).json()
        imposter_requests = []
        for request in imposter_json.get('requests', []):
            imposter_requests.append(ImposterRequest(
                body=request['body'],
                headers=request['headers'],
                method=request['method'],
                path=request['path'],
                query=request['query'],
                request_from=request['requestFrom'],
            ))
        return imposter_requests

    def wait_for_requests(self, count=1, timeout=5.0):
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
        """
        Deletes this `Imposter` from Mountebank.
        This object cannot be used afterwards.
        """
        requests.delete(self._url)


class ImposterRequest:

    """
    A request made on a Mountebank imposter. Returned by 'Imposter` object.
    """

    def __init__(self, body, headers, method, path, query, request_from):
        """
        :param body: The body of a response. Can be any valid JSON (this includes raw values)
        :param dict headers:
        :param str method:
        :param str path:
        :param dict query:
        :param str request_from:
        """
        # TODO add timestamp field, use dateutil
        self.body = body
        self.headers = headers
        self.method = method
        self.path = path
        self.query = query
        self.request_from = request_from


HttpStub = collections.namedtuple('HttpStub', ['method', 'path', 'status_code', 'response'])
HttpStub.__doc__ = """A configuration for a simple Mountebank impostor, not including the port."""


# TODO add imposter calling_url field (other url should be management_url)
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
        super().__init__(get_mb_command() + ['--mock', '--port', '{port}'], port)
        self._imposters_url = 'http://localhost:{}/imposters'.format(self.port)

    def add_imposter(self, imposter_cfg):
        """
        Adds a HTTP service stub (imposter) to Mountebank instance.
        :param dict imposter_cfg: JSON with Mountebank configuration for an impostor.
        Consult Mountebank documentation.
        :return: The created service stub.
        :rtype: Imposter
        """
        resp = requests.post(self._imposters_url, json=imposter_cfg)
        resp.raise_for_status()
        return Imposter(self.port, imposter_cfg['port'])

    def add_imposter_simple(self, port=None, method='GET', path='/', status_code=200, response=''):
        """
        Adds a HTTP service stub (imposter) to Mountebank instance.
        Takes a simplified configuration.
        :param int port: port the imposter will listen on. If none, a random port will be selected.
        :param str method: HTTP method that the imposter will wait for. GET by default.
        :param str path: HTTP path the imposter will wait for. '/' by default.
        :param int status_code: HTTP status code the imposter will return. 200 by default.
        :param str response: body of the imposters response. Empty string by default.
        :return: The created service stub.
        :rtype: Imposter
        """
        if port == None:
            port = port_for.select_random()

        imposter_config = {
            'port': port,
            'protocol': 'http',
            'stubs': [
                {
                    'responses': [
                        {
                            'is': {
                                'statusCode': status_code,
                                'headers': {
                                    'Content-Type': 'application/json'
                                },
                                'body': response
                            }
                        }
                    ],
                    'predicates': [
                        {
                            'and': [
                                {
                                    'equals': {
                                        'path': path,
                                        'method': method,
                                    }
                                },
                            ]
                        }
                    ]
                }
            ]
        }
        return self.add_imposter(imposter_config)

    def add_imposters_simple(self, port, stubs):
        """
        Adds a Mountebank imposter with multiple HTTP stubs on one port.
        Takes a simplified configuration in comparison to "add_imposter".
        :param int port: port the imposter will listen on
        :param list[HttpStub] stubs: HTTP stubs to be created on the port
        :rtype: None
        """
        # TODO make this method and add_imposter_simple more elegant and less duplicated
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
        self.add_imposter(imposter_config)

    def reset(self):
        """
        Removes configured imposters (HTTP stubs).
        :rtype: None
        """
        # TODO add validation
        requests.delete(self._imposters_url)
