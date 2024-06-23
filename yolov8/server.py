from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import json

def picking(itemA, itemB):
    if itemA == 'x' or itemB == 'x':
        return "none"
    if itemA == itemB:
        return itemA
    return "none"

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    picked = False
    pickedList = {}
    box_camera_1 = 'x'
    box_camera_2 = 'x'
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.path)
        box = query_params['box'][0] 
        if query_params['camera'][0] == '0':
            MyHTTPRequestHandler.box_camera_1 = box
        elif query_params['camera'][0] == '2':
            MyHTTPRequestHandler.box_camera_2 = box
        self.send_response(200)
        self.send_header("Content-type", "text/olain")
        self.end_headers()
        boxObject = picking(MyHTTPRequestHandler.box_camera_1, 
                            MyHTTPRequestHandler.box_camera_2)
        if boxObject != "none": 
            if not MyHTTPRequestHandler.picked:
                if boxObject in MyHTTPRequestHandler.pickedList:
                    MyHTTPRequestHandler.pickedList[boxObject] += 1
                else:
                    MyHTTPRequestHandler.pickedList[boxObject] = 1
                with open("config/picked.json", "w") as fp:
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