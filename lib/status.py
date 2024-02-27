from subprocess import check_output
import os
import requests
import sys

LSBLK_PATH = os.getenv("LSBLK_PATH") if not os.getenv("LSBLK_PATH") == None else "lsblk"

def systemctl() -> str:
    return check_output(["systemctl", "status"]).decode()
            
def update(unit) -> str:
    return f'{check_output(["journalctl", "-u", f"{unit}.service", "-n", "20"]).decode()}\n{check_output(["journalctl", "-u", f"{unit}.timer", "-n", "20"]).decode()}'

def lsblk() -> str:
    return check_output([LSBLK_PATH, "-o", "name,mountpoint,fstype,fsuse%"]).decode()

def errors() -> str:
    return "\n".join([line for line in check_output(["journalctl", "-n", "1000"]).decode() if "error" in line])


if __name__ == "__main__":
    print(systemctl())
    print(update())
    print(lsblk())
    print(errors())
    print(systemctl())
    print(update())
    print(lsblk())
    print(errors())