import subprocess

import port_for
import pytest
import requests

from mountepy import Mountebank, ExistingMountebank, HttpStub
from mountepy.mountebank import MountebankWrapper
from mountepy.mb_mgmt import get_mb_command


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


def test_mountebank_simple_impostor():
    test_port = port_for.select_random()
    test_response = 'Just some reponse body (that I used to know)'
    test_body = 'Some test message body'

    with Mountebank() as mb:
        imposter = mb.add_imposter_simple(
            port=test_port,
            method='POST',
            path='/some-path',
            status_code=201,
            response=test_response
        )

        response = requests.post('http://localhost:{}/some-path'.format(test_port), data=test_body)
        assert response.status_code == 201
        assert response.text == test_response
        assert imposter.wait_for_requests()[0].body == test_body


def test_mountebank_multiple_simple_impostors():
    test_port = port_for.select_random()
    test_response_1 = 'Just some response body (that I used to know)'
    test_response_2 = '{"Hey": "a JSON!"}'
    stub_1 = HttpStub(method='PUT', path='/path-1', status_code=201, response=test_response_1)
    stub_2 = HttpStub(method='POST', path='/path-2', status_code=202, response=test_response_2)

    with Mountebank() as mb:
        mb.add_multi_stub_imposter_simple(
            port=test_port,
            stubs=[stub_1, stub_2]
        )

        # TODO get rid of the code duplication
        response_1 = requests.put('http://localhost:{}/path-1'.format(test_port))
        assert response_1.status_code == 201
        assert response_1.text == test_response_1
        response_2 = requests.post('http://localhost:{}/path-2'.format(test_port))
        assert response_2.status_code == 202
        assert response_2.text == test_response_2


def test_impostor_destroy():
    with Mountebank() as mb:
        imposter = mb.add_imposter_simple()
        imposter.destroy()
        with pytest.raises(requests.exceptions.ConnectionError):
            requests.get('http://localhost:{}'.format(imposter.port))


def test_impostor_get_matches_timeout():
    with Mountebank() as mb:
        imposter = mb.add_imposter_simple()
        with pytest.raises(TimeoutError):
            imposter.wait_for_requests(timeout=0.001)


def test_mountebank_reset():
    test_port = port_for.select_random()
    with Mountebank() as mb:
        imposters_url = 'http://localhost:{}/imposters'.format(mb.port)
        mb.add_imposter_simple(
            port=test_port,
            method='GET',
            path='/',
            status_code=200,
            response=''
        )
        assert requests.get(imposters_url).json()['imposters'] != []
        mb.reset()
        assert requests.get(imposters_url).json()['imposters'] == []


def test_mountebank_wrapper_unimplemented_methods():
    mb = MountebankWrapper('host', 1234)
    with pytest.raises(NotImplementedError):
        mb.start()
    with pytest.raises(NotImplementedError):
        mb.stop()


def test_existing_mountebank_simple_imposter():
    mb_port = port_for.select_random()
    test_port = port_for.select_random()
    test_response = 'Just some reponse body (that I used to know)'
    test_body = 'Some test message body'

    mb_process = subprocess.Popen(get_mb_command() + ['--mock', '--port', str(mb_port)])
    with ExistingMountebank('localhost', mb_port) as mb:
        imposter = mb.add_imposter_simple(
            port=test_port,
            method='POST',
            path='/some-path',
            status_code=201,
            response=test_response
        )

        response = requests.post('http://localhost:{}/some-path'.format(test_port), data=test_body)
        assert response.status_code == 201
        assert response.text == test_response
        assert imposter.wait_for_requests()[0].body == test_body

    mb_process.terminate()
