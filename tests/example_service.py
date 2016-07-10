import os
import sys
from bottle import route, run

@route('/')
def example():
    return 'Just some text.'

if len(sys.argv) > 1:
    app_port = int(sys.argv[1])
else:
    app_port = int(os.environ['TEST_APP_PORT'])
run(port=app_port)