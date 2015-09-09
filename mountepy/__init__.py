from mountepy.mountepy import Mountebank, HttpService
from configparser import ConfigParser

import os.path


def _get_package_version():
    package_dir = os.path.dirname(os.path.realpath(__file__))
    setup_cfg_path = os.path.join(package_dir, '../setup.cfg')

    config = ConfigParser()
    config.read(setup_cfg_path)
    return config['metadata']['version']


__version__ = _get_package_version()
