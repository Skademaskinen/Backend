import sys
import os
# fix include paths
sys.path.append(f'{os.path.dirname(__file__)}/..')

from http.server import BaseHTTPRequestHandler
from json import loads
import html

from lib.Arguments import debug, verbose

class Backend(BaseHTTPRequestHandler):
    exiting = False

    def end_headers(self):
        if debug:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.send_header("Access-Control-Allow-Methods", "*")
        else:
            self.send_header("Access-Control-Allow-Origin", "https://about.skademaskinen.win")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.send_header("Access-Control-Allow-Methods", "*")
        super().end_headers()

    def parseData(self):
        size = int(self.headers.get("Content-Length", 0))
        if "?" in self.path:
            self.data = {kv.split("=")[0]:kv.split("=")[1] for kv in self.path.split("?")[1].split("&")}
            self.cmd = self.path.split("?")[0].replace("/admin", "")[1:]
        else:
            self.data = {}
            self.cmd = self.path.replace("/admin", "")[1:]
        
        match self.command:
            case "POST":
                if not self.data:
                    self.data = loads(self.rfile.read(size).decode()) if size else {}
                self.cmd = self.path.replace("/admin", "")[1:]
            case "DELETE":
                if not self.data:
                    self.data = loads(self.rfile.read(size).decode()) if size else {}
                self.cmd = self.path.replace("/admin", "")[1:]
            case "PUT":
                self.file = self.rfile.read(size)
        self.data = {key:html.escape(value) if type(value) is str and not key == "html" else value for key, value in self.data.items()}
        if verbose:
            print(f"\033[38;2;100;100;100mData:    {self.data}\nCommand: {self.cmd}\nPath:    {self.path}\033[0m")


    def ok(self, data="", encode=True):
        if self.exiting: return
        self.exiting = True
        self.send_response(200)
        if data:
            if encode:
                self.send_header("Content-Type", "application/json")
                final = data.encode()
            else:
                final = data
            self.end_headers()
            self.wfile.write(final)
        else:
            self.end_headers()
        
    def deny(self, data=""):
        if self.exiting: return
        self.exiting = True
        self.send_error(400)
        self.end_headers()
        if data:
            self.wfile.write(data.encode())

    def exec(self):
        raise NotImplementedError()

    def do_GET(self):
        self.exec()
    
    def do_POST(self):
        self.exec()

    def do_PUT(self):
        self.exec()

    def do_DELETE(self):
        self.exec()
    def do_OPTIONS(self):
        self.ok()