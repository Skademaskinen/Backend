from lib.Table import Table
from lib.tables.Threads import Threads

class Posts(Table):
    def columns(self) -> list[str]:
        return ["id integer primary key",
                "content varchar not null",
                "threadId integer not null",
                f"foreign key(threadId) references {Threads.__name__} (id)"
        ]

    def ids(self, id:int):
        data = self.database.doSQL(f"select id from {type(self).__name__} where threadId = ?", [id])
        if data:
            return [id for id, in data]
        else:
            return []
        
    def get(self, id:int):
        data = self.database.doSQL(f"select content from {type(self).__name__} where id = ?", [id])[0]
        return {
            "content":data[0]
        }
    
    def new(self, id:int, content:str):
        self.database.doSQL(f"insert into {type(self).__name__} (content,threadId) values (?, ?)" , [content, id])

    def setContent(self, id:int, content:str):
        self.database.doSQL(f"update {type(self).__name__} set content = ? where id = ?", [content, id])

    def delete(self, id:int):
        self.database.doSQL(f"delete from {type(self).__name__} where id = ?", [id])