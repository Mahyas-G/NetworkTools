import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INV_FILE = os.path.join(BASE_DIR, "inventory.json")

with open(INV_FILE) as f:
    inventory = json.load(f)

    for device in inventory:
        print(f"{device['name']:<5} {device['ip']:<12} {device["status"]}")
