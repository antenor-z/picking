from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.camera0 = 'x'
        self.camera1 = 'y'
        super().__init__(*args, **kwargs)
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.path)
        name = query_params['name'][0] 
        if query_params['camera'][0] == 0:
            self.camera0 = name
        else:
            self.camera1 = name
        self.send_response(200)
        self.send_header("Content-type", "text/olain")
        self.end_headers()
        if self.camera0 == self.camera1:
            self.wfile.write(b"Detected Picking at Box ", self.name)
        else:
            self.wfile.write(b"No Picking Detected")

server_address = ("0.0.0.0", 8000)
httpd = HTTPServer(server_address, MyHTTPRequestHandler)
print("Server running at http://localhost:8000")
httpd.serve_forever()
