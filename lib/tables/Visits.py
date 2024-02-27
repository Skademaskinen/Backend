from lib.Table import Table
from lib.Utils import isToday, isYesterday
from secrets import token_urlsafe

class Visits(Table):
    def columns(self) -> list[str]:
        return ["token varchar primary key", 
                "timestamp integer not null"
        ]
    
    def new(self) -> str:
        return token_urlsafe(32)
    
    def register(self, token:str, timestamp:int):
        data = self.database.doSQL(f"select * from {type(self).__name__} where token = ?", [token])
        if not data:
            self.database.doSQL(f"insert into {type(self).__name__} values(?, ?)", [token, timestamp])

    def get(self, timestamp) -> (int, int, int):
        data = self.database.doSQL(f"select timestamp from {type(self).__name__}")
        if not data:
            return (0,0,0)
        today = len([stored_timestamp for stored_timestamp, in data if isToday(timestamp, stored_timestamp)])
        yesterday = len([stored_timestamp for stored_timestamp, in data if isYesterday(timestamp, stored_timestamp)])
        total = len(data)

        return today, yesterday, total