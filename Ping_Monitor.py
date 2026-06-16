import subprocess

def ping(ip):
    result = subprocess.run(
        ["ping", "-n", "1", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0

with open("ips.txt") as f:
    for ip in f:
        ip = ip.strip()
        if ping(ip):
            print(f"{ip} -> UP")
        else:
            print(f"{ip} -> DOWN")
