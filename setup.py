#!/usr/bin/env python3

from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
	name = 'whoshome',
	version = '1.0.0',
	description = 'Find out who\'s home based on Wi-Fi connection',
	long_description = long_description,
	url = 'https://github.com/fabiocody/Whos-Home',
	author = 'Fabio Codiglioni',
	author_email = 'fabiocody@icloud.com',
	licence = 'MIT',
	classifiers = [
		'Licence :: OSI Approved :: MIT',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
	],
	keywords = 'wifi, mac, home, arp',
	packages = ['whoshome'],
	entry_points={
        'console_scripts': [
            'whoshome=whoshome:main',
        ],
    },
)