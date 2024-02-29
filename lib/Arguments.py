from lib.Utils import getArg

addr:tuple[str, int] = (
    getArg(["--hostname", "-H"], "", str),
    getArg(["--port", "-p"], 8080, int)
)
db:str = getArg(["--database", "-db"], "/tmp/skademaskinen.db3", str)
debug:bool = getArg(["--debug", "-d"], False, bool)
verbose:bool = getArg(["--verbose", "-v"], False, bool)

inet:str = getArg(['--inet'], '10.225.171.0/24', str)

help:bool = getArg(["--help", "-h", "-?"], False, bool)