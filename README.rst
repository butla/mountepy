mountepy
========

.. image:: https://snap-ci.com/butla/mountepy/branch/master/build_image
    :target: https://snap-ci.com/butla/mountepy/branch/master
.. image:: https://coveralls.io/repos/butla/mountepy/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/butla/mountepy?branch=master
.. image:: https://requires.io/github/butla/mountepy/requirements.svg?branch=master
    :target: https://requires.io/github/butla/mountepy/requirements/?branch=master

Utilities for creating (micro)service tests. Based on `Mountebank <http://www.mbtest.org/>`_.

Mountepy works by spawning and cleaning after given HTTP service
processes and Mountebank. Thanks to that you no longer need that "start X
before running the tests" for your application. No. Your tests start
"X", it's put up or down only when it needs to and as many times as you
need.

- Test-framework-agnostic (use unittest, nose, py.test or whatever...
  but I like py.test).
- Enables fast and reliable end-to-end testing of microservices. They
  won't be aware that they are in some testing mode.
- Tested on Python 3.4, Ubuntu 14 x64.
- Planned features in the road map below.
  If you have suggestions, just post them as Github issues.
  Pull requests are also welcome :)

I recommend Pytest for elastic composition of service process test
fixtures. Your process may start once per test suite, once per test,
etc.

Installation
------------

.. code-block:: bash

    $ pip install mountepy

A standalone distribution of Mountebank (including NodeJS) will be
downloaded on first run.

If you don't want Mountepy to download Mountebank:

1. Install NodeJS and NPM. On Ubuntu it's

.. code-block:: bash

    $ sudo apt-get install -y nodejs-legacy npm

2. Install Mountebank yourself

.. code-block:: bash

    $ npm install -g mountebank --production

Examples
--------

Mountebank acts as a mock for external HTTP services.
Here's how you spawn a Mountebank process, configure it with a stub
of some HTTP service, assert that it's actually responding.
Mountebank process is killed after the ``with`` block.

.. code-block:: python

    # requests is installed alongside Mountepy
    import mountepy, requests

    with mountepy.Mountebank() as mb:
        imposter = mb.add_imposter_simple(path='/something', response='mock response')
        stub_url = 'http://localhost:{}/something'.format(imposter.port)
        assert requests.get(stub_url).text == 'mock response'

It's a good idea to test your service as a whole process.
Let's say that you have an one-file WSGI (e.g. Flask or Bottle) app
that responds to a ``GET`` on its root path (``'\'``) with a string
it sees in ``RET_STR`` environment variable.
Also, the app needs to know on what port to run, so we also pass it
as an environment variable. ``{port}`` is a special value for Mountepy.
It will be filled with the application's port, whether it's passed
during object construction or automatically selected from free ports.

.. code-block:: python

    # port_for is installed alongside Mountepy
    import mountepy, requests, port_for, os, sys

    service_port = port_for.select_random()
    service = mountepy.HttpService(
        [sys.executable, 'sample_app.py'],
        port=service_port,
        env={
            'PORT': '{port}',
            'RET_STR': 'Just some text.'
        })
    with service:
        assert requests.get(service.url).text == 'Just some text.'

Starting a more complex service running on `Gunicorn <http://gunicorn.org/>`_
can look like this:

.. code-block:: python

    import os, sys

    gunicorn_path = os.path.join(os.path.dirname(sys.executable), 'gunicorn')
    service_command = [
        gunicorn_path,
        'your_package.app:get_app()',
        '--bind', ':{port}',
        '--enable-stdio-inheritance',
        '--pythonpath', ','.join(sys.path)]

    service = HttpService(service_command)
    
    # You can use start/stop methods instead of using the "with" statement.
    # It's the same for Mountebank objects.
    service.start()
    
    # now you test stuff...
    service.stop()
    
"Real world" use of ``mountepy`` can be found in `PyDAS <https://github.com/butla/pydas>`_.

Measuring test coverage
-----------------------

Mountepy starts your code in a separate process, so it's normally hard to get
information about the code covered by the tests.
Fortunately, this problem is solved by `Coverage <https://pypi.python.org/pypi/coverage>`_.
See `this documentation page <http://coverage.readthedocs.io/en/coverage-4.0.3/subprocess.html>`_.

In short, you need to:

- run ``coverage.process_startup()`` in each new Python process 
  (this can be enforced by installing ``coverage_pth``, but some caution is required)
- set ``COVERAGE_PROCESS_START`` environment variable to location of your ``.coveragerc``
- run the tests themselves: ``coverage run (...)``, ``coverage combine`` and then ``coverage report -m``

Again, see `PyDAS's tox.ini <https://github.com/butla/PyDAS/blob/master/tox.ini>`_ for demonstration.

Running tests
-------------

Clone the repo with submodules, then install and run tox.

.. code-block:: bash

    $ git clone --recursive git@github.com:butla/mountepy.git
    $ sudo pip install tox
    $ cd mountepy
    $ tox

Motivation (on 2015-12-30)
--------------------------

- Why `Mountebank <https://github.com/bbyars/mountebank>`__? It can be
  deployed as standalone application, is actively developed and
  supports TCP mocks which can be used to simulate broken HTTP
  messages.
- Why not `Pretenders <https://github.com/pretenders/pretenders>`_?
  Doesn't support TCP and the development doesn't seem to be really
  active.
- Why not `WireMock <https://github.com/tomakehurst/wiremock>`_?
  Doesn't support TCP and I don't want to be forced to install Java to
  run tests and it doesn't seem to have more features than Mountebank.
- Why create a new project? There already is a `Python Mountebank
  wrapper <https://github.com/aholyoke/mountebank-python>`_, but it
  doesn't offer much.

License
-------
Mountepy is licensed under `BSD Zero Clause license <https://spdx.org/licenses/0BSD.html>`_.

Why I didn't use one of the more popular licenses like MIT, 2 or 3-Clause BSD or Apache2? Well, this one is practically equal to 2-Clause BSD (and I don't see any functional differences between it and MIT license) with the exception of the rule about retaining the original license text in derivative work. So if you'd happen to redistribute my library along with your software you don't have to attach a copy of my license. So you won't break any copyright laws by being lazy (which I like to be, for instance). You're welcome.

