#!/usr/bin/env python
import json
import gzip

def parse(filename):
    f = gzip.open(filename, 'r')
    entry = {}
    for l in f:
        l = l.strip()
        colonPos = l.find(':')
        if colonPos == -1:
            yield entry
            entry = {}
            continue
        eName = l[:colonPos]
        rest = l[colonPos+2:]
        if eName == "review/score":
            entry[eName] = float(rest)
        elif eName == "review/time":
            entry[eName] = int(rest)
        else:
            entry[eName] = rest        
    yield entry


# parse data to json file
jsonfile = open("Electronics-mongo.json","w")
for e in parse("Electronics.txt.gz"):
    jsonitem = json.dumps(e)
    jsonfile.write(jsonitem)
    jsonfile.write("\n")





