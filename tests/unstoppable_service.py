"""
A service that will not stop on receiving SIGINT (CTRL+C).
"""

import sys
from wsgiref.simple_server import make_server


def example_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]

    start_response(status, headers)
    return [b'Just some text.']


if __name__ == '__main__':
    app_port = int(sys.argv[1])
    httpd = make_server('', app_port, example_app)
    print('Serving unstoppable_service.py on port', app_port)

    while True:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
