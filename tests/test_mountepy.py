import os.path
import port_for
import port_for.api
import pytest
import requests
import sys

from mountepy import Mountebank, HttpService, ServiceGroup, HttpStub

# starting Python 3 (current Python) HTTP server on a port, that will be set by HttpService
TEST_SERVICE_COMMAND = [sys.executable, '-m', 'http.server', '{port}']
TEST_SERVICE_URL_PATTERN = 'http://localhost:{}'


def test_service_start_and_cleanup():
    service_port = port_for.select_random()
    service_url = TEST_SERVICE_URL_PATTERN.format(service_port)

    with HttpService(TEST_SERVICE_COMMAND, service_port):
        assert requests.get(service_url).status_code == 200

    with pytest.raises(requests.exceptions.ConnectionError):
        requests.get(service_url)


def test_service_single_string_command():
    single_string_command = 'mb'
    service = HttpService(single_string_command, 12345)
    assert service._process_command == single_string_command


def test_service_timeout_and_cleanup():
    test_service = HttpService(TEST_SERVICE_COMMAND)

    with pytest.raises(TimeoutError):
        test_service.start(timeout=0.001)
    test_service._service_proc.wait(timeout=3.0)


def test_service_env_config():
    example_service_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'example_service.py'
    )
    service_port = port_for.select_random()

    service = HttpService(
        [sys.executable, example_service_path],
        port=service_port,
        env={'TEST_APP_PORT': str(service_port)})
    with service:
        assert requests.get(TEST_SERVICE_URL_PATTERN.format(service_port)).text == 'Just some text.'


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


def test_mountebank_simple_impostor_add():
    test_port = port_for.select_random()
    test_response = 'Just some reponse body (that I used to know)'

    with Mountebank() as mb:
        mb.add_imposter_simple(
            port=test_port,
            method='POST',
            path='/some-path',
            status_code=201,
            response=test_response
        )
        response = requests.post('http://localhost:{}/some-path'.format(test_port))
        assert response.status_code == 201
        assert response.text == test_response


def test_mountebank_simple_impostors_add():
    test_port = port_for.select_random()
    test_response_1 = 'Just some reponse body (that I used to know)'
    test_response_2 = '{"Hey": "a JSON!"}'
    stub_1 = HttpStub(method='PUT', path='/path-1', status_code=201, response=test_response_1)
    stub_2 = HttpStub(method='POST', path='/path-2', status_code=202, response=test_response_2)

    with Mountebank() as mb:
        mb.add_imposters_simple(
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


def test_mountebank_impostor_reset():
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


def test_service_group_start():
    test_service_1 = HttpService(TEST_SERVICE_COMMAND)
    test_service_2 = HttpService(TEST_SERVICE_COMMAND)
    test_service_1_url = TEST_SERVICE_URL_PATTERN.format(test_service_1.port)
    test_service_2_url = TEST_SERVICE_URL_PATTERN.format(test_service_2.port)

    with ServiceGroup(test_service_1, test_service_2):
        assert requests.get(test_service_1_url).status_code == 200
        assert requests.get(test_service_2_url).status_code == 200


def test_service_group_start_timeout():
    services = ServiceGroup(HttpService(TEST_SERVICE_COMMAND), HttpService(TEST_SERVICE_COMMAND))
    with pytest.raises(TimeoutError):
        services.start(timeout=0.001)


def test_service_group_stop_timeout():
    services = ServiceGroup(HttpService(TEST_SERVICE_COMMAND), HttpService(TEST_SERVICE_COMMAND))
    services.start()
    with pytest.raises(TimeoutError):
        services.stop(timeout=0.00000001)
