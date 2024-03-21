import sys
import os
# fix include paths
sys.path.append(f'{os.path.dirname(__file__)}/..')

from http.server import HTTPServer
from json import dumps

from lib.tables.Users import Users
from lib.tables.Guestbook import Guestbook
from lib.tables.Tokens import Tokens
from lib.tables.Visits import Visits
from lib.tables.Threads import Threads
from lib.tables.Posts import Posts
from lib.Database import Database
from lib.status import systemctl, update, lsblk, errors
from lib.Utils import printHelp
from lib.Backend import Backend
from lib.Arguments import db, addr, help

database = Database(db, [Users, Tokens, Visits, Guestbook, Threads, Posts])
users:Users = database.tables()[Users.__name__]
tokens:Tokens = database.tables()[Tokens.__name__]
visits:Visits = database.tables()[Visits.__name__]
guestbook:Guestbook = database.tables()[Guestbook.__name__]
threads:Threads = database.tables()[Threads.__name__]
posts:Posts = database.tables()[Posts.__name__]

class RequestHandler(Backend):
    def exec(self):
        self.parseData()
        match self.cmd:
            case "":
                print(self.client_address)
                self.ok(dumps({
                    "unprivileged": [
                        "users/verify",
                        "users/register",
                        "guestbook/new",
                        "guestbook/ids",
                        "guestbook/get",
                        "visits/new",
                        "visits/get",
                        "threads/ids",
                        "threads/get",
                        "posts/ids",
                        "posts/get",
                        "images",
                    ],
                    "privileged": [

                        "status",
                        "users/get",
                        "users/authorize",
                        "users/delete",
                        "tokens/verify",
                        "threads/new",
                        "threads/edit",
                        "threads/delete",
                        "posts/new",
                        "posts/order",
                        "posts/delete",
                        "posts/images/all",
                        "posts/images/delete"
                    ]
                }))
            case "users/verify":
                if users.verify(self.data["username"], self.data["password"]):
                    self.ok(tokens.get(self.data["username"]))
                else:
                    self.deny("Access Denied")
            case "users/register":
                if not users.has(self.data["username"]):
                    users.add(self.data["username"], self.data["password"])
                    self.ok()
                else:
                    self.deny()
            case "guestbook/new":
                if all([self.data["time"] > (epoch + 6e10) for epoch in guestbook.timestamps(self.data["name"])]):
                    guestbook.append(self.data["name"], self.data["time"], self.data["message"])
                    self.ok()
                else:
                    self.deny()
            case "guestbook/ids":
                self.ok(dumps(guestbook.ids()))
            case "guestbook/get":
                entry = guestbook.get(self.data["id"])
                entry["id"] = self.data["id"]
                self.ok(dumps(entry))
            case "visits/new":
                token = self.data["token"] if "token" in self.data else visits.new()
                visits.register(token)
                self.ok(token)
            case "visits/get":
                today, yesterday, total = visits.get()
                self.ok(dumps({
                    "today":today,
                    "yesterday":yesterday,
                    "total":total
                }))
            case "threads/ids":
                self.ok(dumps(threads.ids()))
            case "threads/get":
                self.ok(dumps(threads.get(self.data["id"])))
            case "posts/ids":
                self.ok(dumps(posts.ids(self.data["id"])))
            case "posts/get":
                self.ok(dumps(posts.get(self.data["id"])))
            
        if self.cmd[:6] == "images":
            with open(self.cmd, "rb") as file:
                self.ok(file.read(), False)

        if not "token" in self.data or not tokens.verify(self.data["token"]):
            self.deny()
            return
        match self.cmd:
            case "status":
                self.ok(dumps({
                    "systemctl":systemctl(),
                    "update":update("nixos-upgrade"),
                    "lsblk":lsblk(),
                    "errors":errors()
                }))
            case "users/get":
                self.ok(dumps(users.all()))
            case "users/authorize":
                users.toggle(self.data["username"])
                self.ok()
            case "users/delete":
                users.delete(self.data["username"])
                self.ok()
            case "tokens/verify":
                self.ok()
            case "threads/new":
                threads.new(self.data["name"], self.data["description"])
                self.ok()
            case "threads/edit":
                if self.data["description"]:
                    threads.setDescription(self.data["id"], self.data["description"])
                if self.data["name"]:
                    threads.setName(self.data["id"], self.data["name"])
                self.ok()
            case "threads/delete":
                threads.delete(self.data["id"])
                self.ok()
            case "posts/new":
                posts.new(self.data["id"], self.data["html"])
                self.ok()
            case "posts/edit":
                posts.setContent(self.data["id"], self.data["html"])
                self.ok()
            case "posts/order":
                posts.setPriority(self.data["id"], self.data["value"])
                self.ok()
            case "posts/delete":
                posts.delete(self.data["id"])
                self.ok()
            case "posts/images/all":
                self.ok(dumps(os.listdir("images")))
            case "posts/images/new":
                with open("images/"+self.data["filename"], "wb") as file:
                    file.write(self.file)
                self.ok()
            case "posts/images/delete":
                os.remove("images/"+self.data["file"])
                self.ok()
        
            
if __name__ == "__main__":
    if help:
        printHelp()
        exit(0)
    try:
        http = HTTPServer(addr, RequestHandler)
        http.serve_forever()
    except KeyboardInterrupt:
        print()
