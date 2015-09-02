from mountepy import Mountebank

import requests
import pytest

# TODO get mountebank address from mountebank
def test_mountebank_start_impostor_stop():
    test_response = 333
    with Mountebank() as mb:
        mb.add_imposter({
            "port": 4545,
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
                        }]
                }]
        })
        assert requests.get('http://localhost:4545').json() == test_response
    # process should be closed now
    with pytest.raises(requests.exceptions.ConnectionError):
        requests.get('http://localhost:2525')

#TODO normal process test with http.server

#TODO proper disposing on timeout for process and mountebank

# TODO testing with "with" and normally

#TODO starting and stopping all at the same time