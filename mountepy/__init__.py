import pkg_resources

from mountepy.http_service import HttpService, ServiceGroup, wait_for_port
from mountepy.mountebank import Mountebank, HttpService, HttpStub

__version__ = pkg_resources.get_distribution(__name__).version
