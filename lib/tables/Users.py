from lib.Table import Table
from lib.Utils import getArg
import bcrypt

with open(getArg(["--keyfile", "-kf"], "/tmp/skademaskinen-keyfile", str), "r") as file:
    MASTERKEY = file.read()

class Users(Table):
    def columns(self) -> list[str]:
        return ["username varchar primary key", 
                "password varbinary not null", 
                "salt varbinary not null", 
                "authorized boolean not null"
        ]
    
    def add(self, username:str, password:str):
        data = self.database.doSQL(f"select * from {type(self).__name__} where username = ?", [username])
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(password.encode() + salt +  MASTERKEY.encode(), salt)
        if data:
            return
        self.database.doSQL(f"insert into {type(self).__name__} values(?, ?, ?, False)", [username, hash.decode(), salt.decode()])

    def has(self, username:str) -> bool:
        return not self.database.doSQL(f"select * from {type(self).__name__} where username = ?", [username]) == []
    def delete(self, username):
        self.database.doSQL(f"delete from {type(self).__name__} where username = ?", [username])

    def verify(self, username:str, password:str):
        data = self.database.doSQL(f"select * from {type(self).__name__} where username = ?", [username])
        if not data:
            return False
        elif not data[0][3]:
            return False
        _, stored_hash, salt, _ = data[0]
        hash = bcrypt.hashpw(password.encode() + salt.encode() + MASTERKEY.encode(), salt.encode())
        return hash == stored_hash.encode()
    
    def all(self) -> list[dict[str, str | bool]]:
        data = self.database.doSQL(f"select username,authorized from {type(self).__name__}")
        if not data:
            return data
        return [{"username":username, "authorized":authorized==1} for username,authorized, in data]
        
    def toggle(self, username:str):
        self.database.doSQL(f"update {type(self).__name__} set authorized = (1 - authorized) where username = ?", [username])
    

    
