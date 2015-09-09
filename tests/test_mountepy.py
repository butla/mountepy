from mountepy import Mountebank

import pytest
import requests


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
        stub_address = 'http://{}:{}'.format(mb.hostname, stub_port)
        assert requests.get(stub_address).json() == test_response

    # process should be closed now
    with pytest.raises(requests.exceptions.ConnectionError):
        mb.add_imposter(imposter_config)


def test_mountebank_timeout_and_cleanup():
    mb = Mountebank()

    with pytest.raises(TimeoutError):
        mb.start(timeout=0.001)
    mb._mountebank_proc.wait(timeout=3.0)


#TODO reset imposters

#TODO normal process test with http.server

#TODO proper disposing on timeout for process and mountebank

#TODO starting and stopping all at the same time
