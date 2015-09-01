# service-test-py
Utilities for creating (micro)service tests. Based on Mountebank.

**This is a work in progress.**

See the roadmap below for planned features.

## Installation
**TBD**

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
3. Decide if it's better to just download mountebank executable or to install it with npm.
4. Assign services and Mountebank to an unused port. Use [port-for](https://pypi.python.org/pypi/port-for/)?
5. (Maybe for another project) Add verifier of 
