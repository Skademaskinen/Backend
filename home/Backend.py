import sys
import os
# fix include paths
sys.path.append(f'{os.path.dirname(__file__)}/..')

from http.server import BaseHTTPRequestHandler, HTTPServer
from json import loads, dumps
from threading import Thread
import html

from lib.tables.Devices import Devices
from lib.Database import Database
from lib.status import systemctl, update, lsblk, errors
from lib.Utils import getArg, printHelp, verify, scan

addr = (
    getArg(["--hostname", "-H"], "", str),
    getArg(["--port", "-p"], 8081, int)
)
db = getArg(["--database", "-db"], "/tmp/skademaskinen.db3", str)
debug = getArg(["--debug", "-d"], False, bool)

if debug:
    interface = "lo"
    with open(".debugdata.json", "r") as file:
        SERVER = loads(file.read())["backend"]
else:
    interface = "end0"
    SERVER = "https://skademaskinen.win:11034"

database = Database(db, [Devices])
devices:Devices = database.tables()[Devices.__name__]

class RequestHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        if debug:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.send_header("Access-Control-Allow-Methods", "*")
        else:
            self.send_header("Access-Control-Allow-Origin", "about.skademaskinen.win")
            self.send_header("Access-Control-Allow-Headers", "about.skademaskinen.win")
        super().end_headers()

    def parseData(self):
        size = int(self.headers.get("Content-Length", 0))
        match self.command:
            case "POST":
                self.data = loads(self.rfile.read(size).decode()) if size else {}
                self.cmd = self.path[1:]
            case "DELETE":
                self.data = loads(self.rfile.read(size).decode()) if size else {}
                self.cmd = self.path[1:]
            case _:
                if "?" in self.path:
                    self.data = {kv.split("=")[0]:kv.split("=")[1] for kv in self.path.split("?")[1].split("&")}
                    self.cmd = self.path.split("?")[0][1:]
                else:
                    self.data = {}
                    self.cmd = self.path[1:]
        self.data = {key:html.escape(value) if type(value) is str and not key == "html" else value for key, value in self.data.items()}
        
    def ok(self, data=""):
        self.send_response(200)
        self.end_headers()
        if data:
            self.wfile.write(data.encode())
    def deny(self, data=""):
        self.send_error(400)
        self.end_headers()
        if data:
            self.wfile.write(data.encode())

    def do_POST(self):
        self.parseData()
        if verify(self.data["token"], SERVER, interface):
            match self.cmd:
                case "scan":
                    Thread(target=scan, args=[devices]).start()
                    self.ok()
                case "boot":
                    os.system(f"wol {devices.get(self.data['mac'])} --ipaddr={'.'.join(getArg(['--inet'], '10.225.171.0/24', str).split('.')[:3])}.255")
                    self.ok(f"Successfully booted device: {self.data['mac']}")
                case "setalias":
                    devices.setAlias(self.data["mac"], self.data["alias"])
                    self.ok()
                case "setflags":
                    devices.setFlags(self.data["mac"], self.data["flags"])
                    self.ok()
        else:
            self.deny()

    def do_GET(self):
        self.parseData()
        if verify(self.data["token"], SERVER, interface):
            match self.cmd:
                case "status":
                    self.ok(dumps({
                        "systemctl":systemctl(),
                        "update":update("System-Update"),
                        "lsblk":lsblk(),
                        "errors":errors()
                    }))
                case "devices":
                    self.ok(dumps(devices.all()))

    def do_OPTIONS(self):
        self.ok()

if __name__ == "__main__":
    if getArg(["--help", "-h", "-?"], False, bool):
        printHelp()
        exit(0)
    try:
        http = HTTPServer(addr, RequestHandler)
        http.serve_forever()
    except KeyboardInterrupt:
        print()