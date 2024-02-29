import datetime
from sys import argv
import os
from typing import Any
from subprocess import check_output
from json import dumps
import nmap
from time import time

def isToday(before:int) -> bool:
    now = time()
    datetimeNow = datetime.datetime.fromtimestamp(now)
    datetimeBefore = datetime.datetime.fromtimestamp(before)
    yeardiff = datetimeNow.year - datetimeBefore.year
    monthdiff = datetimeNow.month - datetimeBefore.month
    daydiff = datetimeNow.day - datetimeBefore.day
    return yeardiff == 0 and monthdiff == 0 and daydiff == 0


def isYesterday(before:int) -> bool:
    now = time()
    datetimeNow = datetime.datetime.fromtimestamp(now)
    datetimeBefore = datetime.datetime.fromtimestamp(before)
    yeardiff = datetimeNow.year - datetimeBefore.year
    daydiff = datetimeNow.day - datetimeBefore.day
    return yeardiff == 0 and daydiff == 1

help_data = {}

def getArg(args:list[str], default="", type = str) -> Any:
    global help_data
    help_data[args[0]] = {
        "commands":args,
        "default":default,
        "type":type
    }
    match type.__name__:
        case "bool":
            value = any([arg in argv for arg in args])
            return value
        case _:
            for arg in args:
                if arg in argv:
                    value = argv.pop(argv.index(arg)+1)
                    argv[argv.index(arg)]
                    return type(value)
    return default

def printHelp():
    print(os.path.basename(os.getcwd()))
    for key in help_data:
        print(f'{key}\t[{", ".join(help_data[key]["commands"])}] {help_data[key]["type"]}')
        print(f'\tdefault: {help_data[key]["default"]}')
        print()

def verify(token:str, server:str, interface:str) -> bool:
    if getArg(["--debug", "-d"], False, bool):
        print(f"Verifying token: {token} at {server} using {interface}")
    code = check_output([
        "curl",
        "-X", "POST",
        "-d", dumps({
            "token":token
        }),
        server+"/admin/verify",
        "--interface", interface,
        "-w", "%{http_code}"
    ]).decode().strip()
    return code == "200"

ip = getArg(["--inet"], "10.225.171.0/24", str)

def scan(devices):
    nm = nmap.PortScanner()
    nm.scan(ip)
    for host in nm.all_hosts():
        if "mac" in nm[host]["addresses"]:
            mac = nm[host]["addresses"]["mac"]
            devices.add(mac)
    print("finished scan")

if __name__ == "__main__":
    if getArg(["--help", "-h", "-?"], False, bool):
        printHelp()