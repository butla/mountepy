from mountepy import Mountebank, HttpService

import port_for
import port_for.api
import pytest
import requests
import sys


def test_service_start_and_cleanup():
    # starting Python 3 (current Python) HTTP server on a random port
    service_port = port_for.select_random()
    process_command = [sys.executable, '-m', 'http.server', '{port}']
    service_url = 'http://localhost:{}'.format(service_port)

    with HttpService(process_command, service_port):
        assert requests.get(service_url).status_code == 200

    with pytest.raises(requests.exceptions.ConnectionError):
        requests.get(service_url)

def test_service_single_string_command():
    single_string_command = 'mb'
    service = HttpService(single_string_command, 12345)
    assert service._process_command == single_string_command


def test_mountebank_set_impostor_and_cleanup():
    test_response = 333
    stub_port = 4545
    imposter_config = {
        "port": stub_port,
        "protocol": "http",
        "stubs": [
            {
                "responses": [
                    {
                        "is": {
                            "statusCode": 200,
                            "headers": {
                                "Content-Type": "application/json"
                            },
                            "body": test_response
                        }
                    }
                ],
                "predicates": [
                    {
                        "and": [
                            {
                                "equals": {
                                    "path": "/",
                                    "method": "GET",
                                }
                            },
                        ]
                    }
                ]
            }
        ]
    }

    with Mountebank() as mb:
        mb.add_imposter(imposter_config)
        stub_address = 'http://localhost:{}'.format(stub_port)
        assert requests.get(stub_address).json() == test_response

    # process should be closed now
    with pytest.raises(requests.exceptions.ConnectionError):
        mb.add_imposter(imposter_config)


def test_mountebank_timeout_and_cleanup():
    mb = Mountebank()

    with pytest.raises(TimeoutError):
        mb.start(timeout=0.001)
    mb._service_proc.wait(timeout=3.0)


#TODO reset imposters

#TODO proper disposing on timeout for process and mountebank

#TODO starting and stopping all at the same time
