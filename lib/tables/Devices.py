from lib.Table import Table

class Devices(Table):
    def columns(self) -> list[str]:
        return ["mac varchar primary key",
                "alias varchar",
                "flags varchar"
        ]
    
    def add(self, mac:str, alias=""):
        if alias:
            self.database.doSQL(f"insert or replace into {type(self).__name__} (mac,alias) values (?, ?)", [mac, alias])
        else:
            self.database.doSQL(f"insert or replace into {type(self).__name__} (mac) values(?)", [mac])

    def all(self) -> list[dict[str, str]]:
        data = self.database.doSQL(f"select * from {type(self).__name__}")
        if data:
            return [{"mac":mac, "alias":alias, "flags":flags} for mac,alias,flags, in data]
        return []
    
    def get(self, mac:str) -> dict[str, str]:
        data = self.database.doSQL(f"select * from {type(self).__name__} where mac = ?", [mac])
        if data:
            mac, alias, flags, = data[0]
            return {"mac":mac, "alias":alias, "flags":flags}
        return None
    
    def setAlias(self, mac:str, alias:str):
        self.database.doSQL(f"update {type(self).__name__} set alias = ? where mac = ?", [alias, mac])

    def setFlags(self, mac:str, flags:str):
        self.database.doSQL(f"update {type(self).__name__} set flags = ? where mac = ?", [flags, mac])
