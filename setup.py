# -*- coding: utf-8 -*-

from setuptools import setup
import mountepy


version = mountepy.__version__

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [
    'requests',
]

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
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
    ],
)
