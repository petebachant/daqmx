#!/usr/bin/env python
# coding=utf-8

from distutils.core import setup

setup(
    name='daqmx',
    version='0.0.1',
    author='Pete Bachant',
    author_email='petebachant@gmail.com',
    packages=['daqmx'],
    scripts=[],
    url='https://github.com/petebachant/daqmx.git',
    license='LICENSE',
    description='Wrapper for the National Instruments DAQmx driver.',
    long_description=open('README.md').read(),
    install_requires=[]
)