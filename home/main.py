import sys
import os
# fix include paths
sys.path.append(f'{os.path.dirname(__file__)}/..')

from http.server import HTTPServer
from json import loads, dumps
from threading import Thread

from lib.tables.Devices import Devices
from lib.Database import Database
from lib.status import systemctl, update, lsblk, errors
from lib.Utils import scan, verify, printHelp
from lib.Backend import Backend
from lib.Arguments import debug, db, addr, inet, help

if debug:
    interface = "lo"
    with open(".debugdata.json", "r") as file:
        SERVER = loads(file.read())["backend"]
else:
    interface = "end0"
    SERVER = "https://skademaskinen.win:11034"

database = Database(db, [Devices])
devices:Devices = database.tables()[Devices.__name__]

class RequestHandler(Backend):
    def exec(self):
        self.parseData()
        if not "token" in self.data or not verify(self.data["token"], SERVER, interface):
            self.deny()
            return
        match self.cmd:
            case "scan":
                Thread(target=scan, args=[devices]).start()
                self.ok()
            case "boot":
                os.system(f"wol {devices.get(self.data['mac'])} --ipaddr={'.'.join(inet.split('.')[:3])}.255")
                self.ok(f"Successfully booted device: {self.data['mac']}")
            case "setalias":
                devices.setAlias(self.data["mac"], self.data["alias"])
                self.ok()
            case "setflags":
                devices.setFlags(self.data["mac"], self.data["flags"])
                self.ok()
            case "status":
                self.ok(dumps({
                    "systemctl":systemctl(),
                    "update":update("System-Update"),
                    "lsblk":lsblk(),
                    "errors":errors()
                }))
            case "devices":
                self.ok(dumps(devices.all()))
            

if __name__ == "__main__":
    if help:
        printHelp()
        exit(0)
    try:
        http = HTTPServer(addr, RequestHandler)
        http.serve_forever()
    except KeyboardInterrupt:
        print()