from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import json

def picking(camA, camB):
    camA = str(camA)
    camB = str(camB)
    if camA == '1' and camB == '1':
        return 'brilhante'
    if camA == '2' and camB == '1':
        return 'borracha'
    if camA == '3' and camB == '1':
        return 'fantasma'
    if camA == '1' and camB == '2':
        return 'relogio'
    if camA == '2' and camB == '2':
        return 'chave'
    if camA == '3' and camB == '2':
        return 'celular'
    return "none"

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    camera0 = 'x'
    camera1 = 'y'
    picked = False
    pickedList = {}
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.path)
        name = query_params['name'][0] 
        if query_params['camera'][0] == '0':
            MyHTTPRequestHandler.camera0 = name
        elif query_params['camera'][0] == '2':
            MyHTTPRequestHandler.camera1 = name
        self.send_response(200)
        self.send_header("Content-type", "text/olain")
        self.end_headers()
        boxObject = picking(MyHTTPRequestHandler.camera0, MyHTTPRequestHandler.camera1)
        if boxObject != "none": 
            if not MyHTTPRequestHandler.picked:
                if boxObject in MyHTTPRequestHandler.pickedList:
                    MyHTTPRequestHandler.pickedList[boxObject] += 1
                else:
                    MyHTTPRequestHandler.pickedList[boxObject] = 1
                with open("pickedItens.json", "w") as fp:
                    json.dump(MyHTTPRequestHandler.pickedList, fp=fp, indent=4)
                MyHTTPRequestHandler.picked = True
                self.wfile.write(b"Detected Picking")
        else:
            MyHTTPRequestHandler.picked = False
            self.wfile.write(b"No Picking Detected")

server_address = ("0.0.0.0", 8000)
httpd = HTTPServer(server_address, MyHTTPRequestHandler)
print("Server running at http://localhost:8000")
httpd.serve_forever()
