from lib.Table import Table
from lib.tables.Users import Users
from secrets import token_urlsafe

class Tokens(Table):
    def columns(self) -> list[str]:
        return ["token varchar primary key",
                "username varchar",
                f"foreign key(username) references {Users.__name__} (username)"
        ]
    
    def get(self, username:str) -> str:
        data = self.database.doSQL(f"select * from {type(self).__name__} where username = ?", [username])
        if not data:
            token = token_urlsafe(32)
            self.database.doSQL(f"insert into {type(self).__name__} values(?, ?)", [token, username])
            return token
        return self.database.doSQL(f"select token from {type(self).__name__} where username = ?", [username])[0][0]
    
    def verify(self, token:str) -> bool:
        data = self.database.doSQL(f"select username from {type(self).__name__} where token = ?", [token])
        if not data:
            return False
        username = data[0][0]
        return self.database.doSQL(f"select authorized from {Users.__name__} where username = ?", [username])[0][0] == 1
    
