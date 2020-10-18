#!/usr/bin/python
# -*- coding: utf-8 -*-
from .data import data
import logging
from sys import version_info
import threading
if version_info.major > 2:
    unicode = str
else:
    unicode = unicode
logger = logging.getLogger(__name__)


class WSGIApp(object):

    def __init__(self):
        self.routes = {}
        self.data = data

    def __call__(self, environ, start_response):
        """ Each instance of class is a WSGI application. """

        return self.wsgi(environ, start_response)

    def wsgi(self, environ, start_response):
        """ The WSGI-interface. """

        self.environ = environ
        for route in self.routes:
            if route.endswith('*') and environ.get('PATH_INFO'
                                                   ).startswith(route[:-1]):
                try:
                    r = self.bytes(self.routes.get(route)(environ,
                                                          start_response))
                except Exception as e:
                    return self.bytes(self.ERROR(environ,
                                                 start_response, e))
                return r
            if environ.get('PATH_INFO') == route:
                try:
                    r = self.bytes(self.routes.get(route)(environ,
                                                          start_response))
                except Exception as e:
                    return self.bytes(self.ERROR(environ,
                                                 start_response, e))
                return r
        return self.bytes(self.NOT_FOUND(environ, start_response))

    def bytes(self, out):
        if not out:
            return []

        # Join lists of byte or unicode strings. Mixed lists are NOT supported

        if isinstance(out, (tuple, list)) and isinstance(out[0],
                                                         (bytes, unicode)):
            out = (out[0])[0:0].join(out)  # b'abc'[0:0] -> b''

        # Encode unicode strings

        if isinstance(out, unicode):
            out = out.encode()

        # Byte Strings are just returned

        if isinstance(out, bytes):
            return [out]

    def NOT_FOUND(self, environ, start_response):
        err = data.NOT_FOUND
        headers = [('Content-Type', 'text/html; charset=UTF-8')]
        start_response('404 NOT FOUND', headers)
        return [err]

    def ERROR(
        self,
        environ,
        start_response,
        E,
    ):

        logger.warn(' error : ' + str(E))
        err = '</br><p>SignalPy Error : ' + str(E) + '</p>'
        headers = [('Content-Type', 'text/html; charset=UTF-8')]
        try:
            start_response('500 INTERNAL SERVER ERROR', headers)
        except:
            err += \
                '<p>cannot send 500 error.because above error happened after sending status</p>'
        return [data.ERROR(err)]

    def route(self, r):

        def decorator(callback):
            self.routes[r] = callback
            return callback

        return decorator
