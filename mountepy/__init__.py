import pkg_resources

from mountepy.mountepy import Mountebank, HttpService, ServiceGroup, HttpStub, wait_for_port

__version__ = pkg_resources.get_distribution(__name__).version
