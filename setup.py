#!/usr/bin/env python3

import os
from setuptools import setup, find_packages


def get_requirements():
    requirements_txt = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')
    with open(requirements_txt) as fd:
        return fd.read().splitlines()


def get_version():
    with open(os.path.join('thoth', 'worker', '__init__.py')) as f:
        for line in f.readlines():
            if line.startswith('__version__ = '):
                version = line[len('__version__ = "'):-2]
                return version

    raise ValueError("No version information found in 'thoth.worker/__init__.py'")


setup(
    name='thoth-worker',
    version=get_version(),
    packages=[
        'thoth.worker',
        'thoth.worker.tasks',
    ],
    package_data={
        'thoth.worker': [
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
    description='Selinon thoth example application',
    license='MIT',
    keywords='selinon celery',
    url='https://github.com/thoth-station/selinon-worker',
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Intended Audience :: Developers",
    ]
)

