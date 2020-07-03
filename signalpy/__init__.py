#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from sl.server import ThreadingWSGIServer
from wsocket import WebSocketHandler
import threading
import json
import logging
from .app import WSGIApp
import time
logger = logging.getLogger(__name__)

app = WSGIApp()

def _get_random_port():
    while True:
        port = random.randint(1023, 65535)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('localhost', port))
            except OSError:
                logger.warning('Port %s is in use' % port)
                continue
            else:
                return port

class Server(ThreadingWSGIServer):
    def __init__(self, server_address=('',None), _app=app):
        if server_address[1]==None:
            server_address=(server_address[0], _get_random_port())
        ThreadingWSGIServer.__init__(self,server_address, WebSocketHandler)
        ThreadingWSGIServer.set_app(self, _app)
    def serve_forever(self, Async=True):
        if Async:
            t = threading.Thread(target=ThreadingWSGIServer.serve_forever,args=[self])
            t.start()
        else:
            ThreadingWSGIServer.serve_forever(self)

class Hub:

    def __init__(
        self,
        url='/',
        _async=True
        ):
        self.chats = {}
        self._async = _async
        app.routes[url] = self.handle
        self._abort = False
        self.client_counter = 0

    def handle(self, environ, start_response):
        if self._abort:
            return
        if environ.get('wsgi.websocket'):
            self.ws(environ, start_response)
            return
        if len(environ.get('QUERY_STRING'))==3:
            start_response('200 OK', [])
            self.client_counter+=1
            _id=str(self.client_counter)
            self.chats[_id]=[]
            self.async_run(self.Client,[_id])
            return[_id.encode()]
        else:
            start_response('200 OK', [])
            if environ.get('CONTENT_LENGTH')!='0':
                msg=read_json(environ.get('CONTENT_LENGTH'),environ.get('wsgi.input'))
                self.async_run(self.Message, [msg, environ.get('QUERY_STRING')[3:]])
                return
            else:
                while self.chats.get(environ.get('QUERY_STRING')[3:])==[]:
                    pass
                msg=json.dumps(self.chats.get(environ.get('QUERY_STRING')[3:])).encode()
                self.chats[environ.get('QUERY_STRING')[3:]]=[]
                return [msg]
    def Message(self, msg, client):
        logger.warn('client '+str(client)+' : '+msg)
    def Client(self, client):
        logger.warn('client '+str(client)+' connected')
    def Send(self, msg, client):
        if client.startswith('ws'):
            self.chats.get(client).send(msg)
        else:
            self.chats.get(client).append(msg)
    def ws(self, environ, start_response):
        self.client_counter+=1
        _id='ws'+str(self.client_counter)
        self.chats[_id]=environ.get('wsgi.websocket')
        ws=environ.get('wsgi.websocket')
        self.async_run(self.Client, [_id])  
        while True:
            msg=ws.receive()
            self.async_run(self.Message, [msg, _id])    
    def async_run(self,func,args=[]):
        if self._async:
            t = threading.Thread(target=func,args=args)
            t.start()
        else:
            func(*args)
    
def read_json(cl, request_file):
    if cl:
        n_bytes = int(cl)
        content_bytes = request_file.read(n_bytes)
        content_string = content_bytes.decode('ascii')
        return content_string
    return ''
    
