from lib.Table import Table

class Threads(Table):
    def columns(self) -> list[str]:
        return ["id integer primary key",
                "name varchar not null",
                "description varchar not null"
        ]

    def ids(self):
        data = self.database.doSQL(f"select id from {type(self).__name__}")
        if data:
            return [id for id, in data]
        else:
            return []
    def get(self, id:int):
        data = self.database.doSQL(f"select name,description from {type(self).__name__} where id = ?", [id])[0]
        return {"name":data[0], "description":data[1]}
        
    def new(self, name:str, description:str):
        self.database.doSQL(f"insert into {type(self).__name__} (name,description) values (?, ?)", [name, description])

    def setDescription(self, id:int, description:str):
        self.database.doSQL(f"update {type(self).__name__} set description = ? where id = ?", [description, id])

    def setName(self, id:int, name:str):
        self.database.doSQL(f"update {type(self).__name__} set name = ? where id = ?", [name, id])

    def delete(self, id:int):
        self.database.doSQL(f"delete from {type(self).__name__} where id = ?", [id])