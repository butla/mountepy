"""
A service that will not stop on receiving SIGINT (CTRL+C).
"""

import os
from bottle import route, run

@route('/')
def example():
    return 'Just some text.'

app_port = int(os.environ['TEST_APP_PORT'])
while True:
    try:
        run(port=app_port)
    except KeyboardInterrupt:
        pass
