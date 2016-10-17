import os
import sys

from wsgiref.simple_server import make_server


def example_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]

    start_response(status, headers)
    return [b'Just some text.']


if __name__ == '__main__':
    if len(sys.argv) > 1:
        app_port = int(sys.argv[1])
    else:
        app_port = int(os.environ['TEST_APP_PORT'])

    httpd = make_server('', app_port, example_app)
    print('Serving example_service.py on port', app_port)
    httpd.serve_forever()
