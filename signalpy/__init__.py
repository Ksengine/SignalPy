#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
SignalPy
Real-time Communication for web applications with SignalR Incredibly simple real-time web for python WSGI servers and frameworks
- Realtime
- WSGI compatible
- Open source, open protocol
- Connect from everywhere
- Simple
"""

from __future__ import print_function

try:
    from sl.server import ThreadingWSGIServer
except:
    try:
        from wsgiref.simple_server import ThreadingWSGIServer
    except:
        from wsgiref.simple_server import WSGIServer
        try:
            from socketserver import ThreadingMixIn
        except:
            from SocketServer import ThreadingMixIn

        class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):

            pass


from wsocket import WebSocketHandler

import threading
import json
import logging
from .app import WSGIApp
import time
import socket

logger = logging.getLogger(__name__)

app = WSGIApp()


def _get_free_port(min=1024, max=65536):
    """
    find a free localhost port for server.
    """
    port = min-1
    while port <= max:
        port += 1
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('localhost', port))
            except OSError:
                logger.warning('Port %s is in use' % port)
                continue
            else:
                return port


class Server(ThreadingWSGIServer):

    """
    builtin server for SignalPy.
    You can use another one(should be WSGI server).eg: GUNICORN
    """

    def __init__(self, server_address=('', None), _app=app, port=None):
        server_address = list(server_address)
        server_address[1] = port or server_address[1]
        if server_address[1] == None:
            server_address = (server_address[0], _get_free_port())
        elif isinstance(server_address[1], (tuple, list)):
            server_address = (server_address[0], _get_free_port())
        ThreadingWSGIServer.__init__(self, tuple(server_address),
                                     WebSocketHandler)
        ThreadingWSGIServer.set_app(self, _app)

    def serve_forever(self, Async=True):
        if Async:
            t = \
                threading.Thread(target=ThreadingWSGIServer.serve_forever,
                                 args=[self])
            t.start()
        else:
            ThreadingWSGIServer.serve_forever(self)


class Hub:

    """
    SignalPy Hub for communication.
    """

    def __init__(self, url='/', _async=True):

        # This will freeze websocket connections

        self.chats = {}
        self._async = _async
        app.routes[url] = self.handle
        self._abort = False
        self.client_counter = 0

    def handle(self, environ, start_response):
        """
        Handle all requests
        """
        if self._abort:
            return
        if environ.get('wsgi.websocket'):
            self.ws(environ, start_response)
            return
        if len(environ.get('QUERY_STRING')) == 3:
            start_response('200 OK', [])
            self.client_counter += 1
            _id = str(self.client_counter)
            self.chats[_id] = []
            self.async_run(self.Client, [_id])
            return [_id.encode()]
        else:
            start_response('200 OK', [])
            if environ.get('CONTENT_LENGTH') != '0':
                msg = read_json(environ.get('CONTENT_LENGTH'),
                                environ.get('wsgi.input'))
                self.async_run(self.Message, [msg,
                                              environ.get('QUERY_STRING')[3:]])
                return
            else:
                while self.chats.get(environ.get('QUERY_STRING')[3:]) \
                        == []:
                    pass
                msg = \
                    json.dumps(self.chats.get(environ.get('QUERY_STRING'
                                                          )[3:])).encode()
                self.chats[environ.get('QUERY_STRING')[3:]] = []
                return [msg]

    def Message(self, msg, client):
        """
        Handle Messages. Replace this...
        --------code----------
        def msg(message,client):print(message)
        Hub.Message=msg
        """
        logger.warn('client ' + str(client) + ' : ' + msg)

    def Client(self, client):
        """
        Handle Clients. Replace this...
        --------code----------
        def c(client):print(message)
        Hub.Client=c
        """
        logger.warn('client ' + str(client) + ' connected')

    def Send(self, msg, client):
        """
        Send Messages.
        --------code----------
        Hub.Send(message, code)
        """

        if client.startswith('ws'):
            self.chats.get(client).send(msg)
        else:
            self.chats.get(client).append(msg)

    def ws(self, environ, start_response):
        """
        WebSocket Handler
        """

        self.client_counter += 1
        _id = 'ws' + str(self.client_counter)
        self.chats[_id] = environ.get('wsgi.websocket')
        ws = environ.get('wsgi.websocket')
        self.async_run(self.Client, [_id])
        while True:
            try:
                msg = ws.receive()
                if msg == None:
                    del self.chats[_id]
                    break
                self.async_run(self.Message, [msg, _id])
            except Exception as e:
                logger.warn(' error : ' + str(e))
                del self.chats[_id]
                break

    def async_run(self, func, args=[]):
        """
        run handlers(sync or async)
        """

        if self._async:
            t = threading.Thread(target=func, args=args)
            t.start()
        else:
            func(*args)


def read_json(cl, request_file):
    """
    simple json reader for ajax.
    """

    if cl:
        n_bytes = int(cl)
        content_bytes = request_file.read(n_bytes)
        content_string = content_bytes.decode('ascii')
        return content_string
    return ''
