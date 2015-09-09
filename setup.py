# -*- coding: utf-8 -*-

import os.path
from setuptools import setup

version = '0.1.0'

# TODO extract this automatically without the specific versions
requirements = [
    'port_for',
    'requests',
]

setup_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(setup_dir, 'README.md')) as readme_file:
    readme = readme_file.read()

setup(
    name='mountepy',
    version=version,
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
