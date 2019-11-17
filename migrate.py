import json
import os.path



with open("commands.json") as f:
    thing = json.load(f)
commandDict = {}
with open("commands.txt") as f:
    for line in f:
        (key, val) = line.split(" : ")
        commandDict[key] = val

thing["Economy"] = commandDict

with open("commands.json", 'w') as f:
    json.dump(thing, f)