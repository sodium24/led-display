#!/usr/bin/python
#
from setuptools import setup, find_packages

setup(
    name='led-display',
    version='0.1.0',
    author='Malcolm Stagg',
    author_email='malcolm@sodium24.com',
    description='LED Display Application Framework',
    packages=find_packages(include=['led_display', 'led_display.*']),
    install_requires=['pillow', 'flask'],
)
