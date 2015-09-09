# -*- coding: utf-8 -*-

import os.path
from setuptools import setup
from configparser import ConfigParser


# TODO extract this automatically without the specific versions
requirements = [
    'port_for',
    'requests',
]

with open('README.md') as readme_file:
    readme = readme_file.read()


def _get_package_version():
    setup_cfg_path = os.path.realpath(__file__)[:-2] + 'cfg'

    config = ConfigParser()
    config.read(setup_cfg_path)
    return config['metadata']['version']


setup(
    name='mountepy',
    version=_get_package_version(),
    description='Utilities for creating (micro)service tests. Based on Mountebank.',
    long_description=readme,
    author='Michał Bultrowicz',
    author_email='michal.bultrowicz@gmail.com',
    url='https://github.com/butla/mountepy',
    packages=[
        'mountepy',
    ],
    package_dir={'mountepy': 'mountepy'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    keywords='mountepy mountebank microservice',
    classifiers=[
        'Development Status :: 3 - Alpha'
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
    ],
)
