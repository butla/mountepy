# mountepy
Utilities for creating (micro)service tests. Based on Mountebank. Test-framework-agnostic (use unittest, nose, py.test or whatever... but I like py.test).

**This is a work in progress.**

See the roadmap below for planned features.

Tested on Python 3.4

## Installation
Install NodeJS and NPM. On Ubuntu it's `sudo apt-get install -y nodejs-legacy npm`

Install Mountebank according to instructions [here](https://github.com/bbyars/mountebank)

**TBD**

## Testing
Install and run tox
```
pip install tox
tox
```

## Examples
**TBD**

## Motivation
* Why Mountebank? It can be deployed as standalone application, is actively developed and supports TCP mocks which can be used to simulate broken HTTP messages.
* Why not [Pretenders](https://github.com/pretenders/pretenders)? Doesn't support TCP, the development doesn't seem to be active.
* Why not [WireMock](https://github.com/tomakehurst/wiremock)? I don't want to be forced to install Java to run tests and it doesn't seem to have more features than Mountebank.
* Why create a new project? There already is a [Python Mountebank wrapper](https://github.com/aholyoke/mountebank-python), but it doesn't offer much.

## Roadmap
1. Wrapper classes for starting and stopping services and Mountebank.
  * Services need to take configuration through environment variables.
  * *(Maybe for another project)* This configuration can be CloudFoundry specific (VCAP_SERVICES, VCAP_APPLICATION).
  * *(Maybe for another project)* Validate if services defined in VCAP_SERVICES are in application's manifest.
2. Class for managing all spawned processes to enable faster overall start.
3. Assign services and Mountebank to an unused port. Use [port-for](https://pypi.python.org/pypi/port-for/)?
4. Add example of calling services through client generated with [Bravado](https://github.com/Yelp/bravado)
5. Make Python 2.7 compatible.
