from signalpy import *
import signalpy.jslib
myserver=Server(('',9001))
myserver.serve_forever()
def read_json(cl, request_file):
    n_bytes = int(cl)
    content_bytes = request_file.read(n_bytes)
    content_string = content_bytes.decode('ascii')
    return content_string

a='''<html>
<head><script src="/signalpy.js"></script></head>
<body>
    <script>
    var sock = SignalPy('localhost:9001/py');
    sock.onmessage=function(data) {console.log(data);sock.send(data.data);};
    </script>
</body>
</html>
'''

myhub=Hub('/py')
@app.route('/')
def test(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-Type', 'text/html')]
    start_response(status, response_headers)
    return[a.encode()]
@app.route('/signalpy.js')
def t(environ, start_response):
    status = '200 OK'
    response_headers = []
    start_response(status, response_headers)
    return[signalpy.jslib.data.encode()]
@app.route('/err')
def ts(environ, start_response):
    status = '200 OK'
    response_headers = []
    start_response(status, response_headers)
    raise Exception('MODA BABA meka baluwa')
    return[b'''hi''']
#@app.route('/chatHub*')

