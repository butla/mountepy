# -*- coding: utf-8 -*-
import os.path
from setuptools import setup

project_name = 'mountepy'
version = '0.3.0'

setup_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(setup_dir, 'requirements.txt')) as req_file:
    requirements = [lib.split('==')[0] for lib in req_file.readlines()]
with open(os.path.join(setup_dir, 'README.rst')) as readme_file:
    readme = readme_file.read()

setup(
    name=project_name,
    version=version,
    description='Utilities for creating (micro)service tests. Based on Mountebank.',
    long_description=readme,
    author='Michał Bultrowicz',
    author_email='michal.bultrowicz@gmail.com',
    url='https://github.com/butla/mountepy',
    packages=[
        project_name,
    ],
    package_dir={project_name: project_name},
    include_package_data=True,
    install_requires=requirements,
    license="BSD Zero Clause",
    keywords='test http mountebank microservice',
    classifiers=[
        'Programming Language :: Python :: 3.4',
        'Operating System :: POSIX :: Linux',
        'Development Status :: 3 - Alpha',
        'License :: Freely Distributable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
    ],
)
