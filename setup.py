#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup  # noqa, analysis:ignore
except ImportError:
    print ('''please install setuptools
python -m pip install setuptools
or
python -m pip install setuptools''')
    raise ImportError()

from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file

with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

## Setup

setup(
    name='SignalPy',
    version='1.0.0',
    author='Kavindu Santhusa',
    author_email='kavindusanthusa@gmail.com',
    license='MIT',
    url='https://github.com/Ksengine/SignalPy',
    download_url='https://pypi.python.org/pypi/SignalPy',
    keywords='simple, lightweight, WSGI, micro, server, library, python,signalr,signalpy, websocket, ajax, xhr, long polling, xhr,alternative, wsocket, servelight '
        ,
    description='Realtime communication for Python web applications'
        ,
    long_description=long_description,
    long_description_content_type='text/markdown',
    platforms='any',
    packages=["signalpy"],
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3',
        ],
    include_package_data=True,
    zip_safe=False
    )
