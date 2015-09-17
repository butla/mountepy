import pkg_resources

from mountepy.mountepy import Mountebank, HttpService, ServiceGroup, HttpStub

__version__ = pkg_resources.get_distribution(__name__).version
