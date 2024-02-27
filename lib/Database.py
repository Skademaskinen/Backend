from typing import Any
import sqlite3

import sys
import os
# fix include paths
sys.path.append(f'{os.path.dirname(__file__)}/..')

from lib.Utils import getArg

debug = getArg(["--debug", "-d"], False, bool)
verbose = getArg(["--verbose", "-v"], False, bool)
showSQL = getArg(["--showSQL", "-sql"], False, bool)

class Database(sqlite3.Connection):
    def __init__(self, path:str, tables:list):
        super().__init__(path)
        self._tables = []
        for table in tables:
            tableObject = table(self)
            self._tables.append(tableObject)
            self.doSQL(f"create table if not exists {table.__name__} ({', '.join(tableObject.columns())})")
    
    def doSQL(self, sql:str, args:list[str] = []) -> list[Any]:
        cursor = sqlite3.Cursor(self)
        if args:
            cursor.execute(sql, args)
        else:
            cursor.execute(sql)
        self.commit()
        data = cursor.fetchall()
        cursor.close()
        if verbose or showSQL:
            print(f"\033[38;2;100;100;100mSQL:  {sql}\nArgs: {args}\nData: {data}\033[0m")
        return data
    
    def tables(self) -> dict:
        return {type(table).__name__:table for table in self._tables}
    
if __name__ == "__main__":
    from lib.tables.Devices import Devices
    from lib.tables.Guestbook import Guestbook
    from lib.tables.Tokens import Tokens
    from lib.tables.Users import Users
    from lib.tables.Visits import Visits
    from time import time
    from os import system

    # scuffed speedy unit tests...
    db = "/tmp/testing.db3"
    system(f"rm {db}")
    t = int(time()) # system gets wonky if we start taking different timestamps, especially around midnight, might wanna work with epoch instead?

    database = Database("/tmp/testing.db3", [Devices,Guestbook,Tokens,Users,Visits])
    users = database.tables()[Users.__name__]
    guestbook = database.tables()[Guestbook.__name__]
    tokens = database.tables()[Tokens.__name__]
    devices = database.tables()[Devices.__name__]
    visits = database.tables()[Visits.__name__]
    print("Database initialized correctly")

    assert type(users) is Users
    users.add("tester", "tester")
    users.delete("tester")
    assert not users.verify("tester", "tester")
    assert users.all() == [{"username":"tester", "authorized":False}]
    users.authorize("tester")
    assert users.all() == [{"username":"tester", "authorized":True}]
    users.deauthorize("tester")
    assert users.all() == [{"username":"tester", "authorized":False}]
    print("Users table is functional")

    assert type(guestbook) is Guestbook
    guestbook.append("tester", t, "test msg")
    assert len(guestbook.ids()) == 1
    for id in guestbook.ids():
        assert guestbook.get(id) == {"name":"tester", "time":t, "message":"test msg"}
    assert guestbook.timestamps("tester") == [t]
    print("Guestbook table is functional")
    
    assert type(tokens) is Tokens
    assert not tokens.verify(tokens.get("tester"))
    users.authorize("tester")
    assert tokens.verify(tokens.get("tester"))
    print("Tokens table is functional")
    
    assert type(devices) is Devices
    devices.add("11:22:33:44:55:66", "tester")
    assert devices.get("11:22:33:44:55:66") == {"mac":"11:22:33:44:55:66", "alias":"tester", "flags":None}
    assert devices.all() == [{"mac":"11:22:33:44:55:66", "alias":"tester", "flags":None}]
    devices.setAlias("11:22:33:44:55:66", "tester1")
    assert devices.get("11:22:33:44:55:66") == {"mac":"11:22:33:44:55:66", "alias":"tester1", "flags":None}
    devices.setFlags("11:22:33:44:55:66", "f")
    assert devices.get("11:22:33:44:55:66") == {"mac":"11:22:33:44:55:66", "alias":"tester1", "flags":"f"}
    print("Devices table is functional")

    assert type(visits) is Visits
    visits.register(visits.new(), t)
    assert visits.get(t) == (1,0,1)
    print("Visits table is functional")