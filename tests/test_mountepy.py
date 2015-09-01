from mountepy import Mountebank

import requests
import pytest

def test_mountebank_proc():
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