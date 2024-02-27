from typing import Any
from lib.Database import Database


class Table:
    def __init__(self, database):
        self.database:Database = database

    def columns(self) -> list[str]:
        raise NotImplementedError()
    
    def rows(self) -> list[dict[str, Any]]:
        rows = self.database.doSQL("select * from ?", [type(self).__name__.lower()])
        columns = self.database.doSQL("PRAGMA table_info(?)", [type(self).__name__.lower()])
        return [{column:row[i] for i,column in enumerate(columns)} for row in rows]