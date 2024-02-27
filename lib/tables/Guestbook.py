from lib.Table import Table

class Guestbook(Table):
    def columns(self) -> list[str]:
        return ["id integer primary key",
                "name varchar not null",
                "time integer not null",
                "message varchar not null"
        ]
    
    def timestamps(self, name:str) -> list[int]:
        data = self.database.doSQL(f"select time from {type(self).__name__} where name = ?", [name])
        if data:
            return [timestamp for timestamp, in data]
        return []
    
    def append(self, name:str, time:int, message:str):
        self.database.doSQL(f"insert into {type(self).__name__} (name,time,message) values(?,?,?)", [name,time,message])
    
    def get(self, id:int) -> dict[str, str | int]:
        data = self.database.doSQL(f"select name,time,message from {type(self).__name__} where id = ?", [id])
        if not data:
            return {"name":"Error", "time":0, "message":"Error!"}
        name, time, message = data[0]
        return {"name": name, "time":time, "message":message}
    
    def ids(self) -> list[int]:
        data = self.database.doSQL(f"select id from {type(self).__name__}")
        if data:
            return [id for id, in data]
        return []
    
