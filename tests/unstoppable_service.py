"""
A service that will not stop on receiving SIGINT (CTRL+C).
"""

import sys
from bottle import route, run

@route('/')
def example():
    return 'Just some text.'

app_port = int(sys.argv[1])
while True:
    try:
        run(port=app_port)
    except KeyboardInterrupt:
        pass
