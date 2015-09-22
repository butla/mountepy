mountepy
========

[![Build Status](https://travis-ci.org/butla/mountepy.svg?branch=master)](https://travis-ci.org/butla/mountepy)
[![Coverage Status](https://coveralls.io/repos/butla/mountepy/badge.svg?branch=master&service=github)](https://coveralls.io/github/butla/mountepy?branch=master)
[![Requirements Status](https://requires.io/github/butla/mountepy/requirements.svg?branch=master)](https://requires.io/github/butla/mountepy/requirements/?branch=master)

Utilities for creating (micro)service tests. Based on Mountebank.
* Test-framework-agnostic (use unittest, nose, py.test or whatever... but I like py.test).
* Tested on Python 3.4, Ubuntu 14 x64.
* Planned features in the road map below (this is still under development).

## Installation
1. Install NodeJS and NPM. On Ubuntu it's `sudo apt-get install -y nodejs-legacy npm`
2. Install Mountebank `npm install -g mountebank --production`
3. `pip3 install git+git://github.com/butla/mountepy.git`

If you want to lock on a specific version in requirements.txt then add to it a line pointing to a specific commit, e.g.:
```
git+git://github.com/butla/mountepy.git@456f22c
```

## Testing
Install and run tox
```
pip install tox
tox
```

## Examples
**TBD**

## Motivation
* Why [Mountebank](https://github.com/bbyars/mountebank)? It can be deployed as standalone application, is actively developed and supports TCP mocks which can be used to simulate broken HTTP messages.
* Why not [Pretenders](https://github.com/pretenders/pretenders)? Doesn't support TCP, the development doesn't seem to be active.
* Why not [WireMock](https://github.com/tomakehurst/wiremock)? I don't want to be forced to install Java to run tests and it doesn't seem to have more features than Mountebank.
* Why create a new project? There already is a [Python Mountebank wrapper](https://github.com/aholyoke/mountebank-python), but it doesn't offer much.

## Road map
1. Substitute port in env variables like in command parts.
1. Fix all TODOs
1. Provide examples.
1. Translate this README to rST.
1. Add to PyPI.
1. Add example of calling services through client generated with [Bravado](https://github.com/Yelp/bravado)
1. Remove MANIFEST.in like they did in PyScaffold.
1. Requirements in setup.py should be extracted automatically from requirements.txt.
1. Make Python 2.7 compatible... maybe.
1. Check if cycling port_for.is_available() is as good as _wait_for_endpoint. If not, add that to port_for.

## Notes
* [Bottle](https://github.com/bottlepy/bottle) is used to test HTTP services' handler.