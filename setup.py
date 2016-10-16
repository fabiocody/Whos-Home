#!/usr/bin/env python3

from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

try:
    with open(path.join(here, 'README.md')) as f:
        long_description = f.read()
except:
    long_description = ''

setup(
    name='whoshome',
    version='1.5.1',
    description='Find out who\'s home based on Wi-Fi connection',
    long_description=long_description,
    url='https://github.com/fabiocody/Whos-Home',
    author='Fabio Codiglioni',
    author_email='fabiocody@icloud.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='whoshome, wifi, mac, home, arp',
    py_modules=['whoshome'],
    install_requires=['scapy-python3'],
    entry_points={
        'console_scripts': [
            'whoshome=whoshome:main',
        ],
    },
)
