#!/usr/bin/env python3

import os
from setuptools import setup, find_packages


def get_requirements():
    requirements_txt = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')
    with open(requirements_txt) as fd:
        return fd.read().splitlines()


def get_version():
    with open(os.path.join('demo_worker', '__init__.py')) as f:
        for line in f.readlines():
            if line.startswith('__version__ = '):
                version = line[len('__version__ = "'):-2]
                return version

    raise ValueError("No version information found in 'demo_worker/__init__.py'")


setup(
    name='demo-worker',
    version=get_version(),
    packages=find_packages(),
    package_data={
        'demo_worker': [
            os.path.join('config', '*.yaml'),
            os.path.join('config', '*.yml'),
            os.path.join('config', 'flows', '*.yaml'),
            os.path.join('config', 'flows', '*.yml')
        ]
    },
    scripts=[],
    install_requires=get_requirements(),
    include_package_data=True,
    author='Fridolin Pokorny',
    author_email='fridolin.pokorny@gmail.com',
    maintainer='Fridolin Pokorny',
    maintainer_email='fridolin.pokorny@gmail.com',
    description='Selinon demo example application',
    license='MIT',
    keywords='selinon celery',
    url='https://github.com/selinon/demo-worker',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Intended Audience :: Developers",
    ]
)

