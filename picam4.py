import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server

PAGE="""\
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
		<meta name="mobile-web-app-capable" content="yes">
		<meta name="viewport" content = "height = device-height, width = device-width, user-scalable = no" />
		<title>PiCamera</title>
		<link rel="shortcut icon" sizes="196x196" href="http://192.168.0.202:8000/html/img/home-icon.png"/>
	</head>
	<style>
		body{
		background-color:MediumSeaGreen;
		background-repeat:no-repeat;
		background-position:center;
		background-size:cover;
		font: bold 18px/25px Tahoma, sans-serif;
		color: White;
		}
		ul {
		list-style-type: none;
		margin: 0;
		padding: 0;
		overflow: hidden;
		background-color: DarkSlateGray;
		}
		li{
		float: left;
		}
		li a {
		display: block;
		color: White;
		text-align: center;
		padding: 16px;
		text-decoration: none;
		}
img{
border-style: solid;
border-width: 5px;
border-color: DarkSlateGray;
}
	</style>
	<body>
		<ul>
			<li><a href="http://192.168.0.202:8000/index.html">LED Control</a></li>
			<li><a href="http://192.168.0.202:5000/index.html">Camera</a></li>
		</ul>
		<h1>PiCamera</h1>
		<div><img align="middle" src="stream.mjpg" width="348" height="261"/></div>
	</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 5000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
