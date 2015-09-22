import os
from bottle import route, run

@route('/')
def example():
    return 'Just some text.'

app_port = int(os.environ['TEST_APP_PORT'])
run(port=app_port)