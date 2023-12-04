from ics import Calendar
from pymongo import MongoClient
import os
from datetime import datetime
import re

client: None | MongoClient = None


def mongo_connect():
    global client
    if client is None:
        client = MongoClient(os.environ["DATABASE_HOST"], int(os.environ["DATABASE_PORT"]))

    db = client.ade
    return db


def parse_file(filename):
    inserted = 0
    updated = 0

    # get file name
    col_name = os.path.basename(filename)

    # remove extension
    col_name = os.path.splitext(col_name)[0]

    with open(filename, 'r') as my_file:
        c = Calendar(my_file.read())

    db = mongo_connect()
    # col = db[col_name]  # Ex : B3INFOTPA2
    col = db["schedules"]

    for e in c.events:
        # regex match profs : ([a-zA-Z\-]* [a-zA-Z\-]*)
        # regex match groupes : [a-zA-Z][0-9][a-zA-Z]*[0-9]*
        # regex retirer heure génération ics : \\(Exporté le:([0-9]{2}\\/){2}[0-9]{4} [0-9]{2}:[0-9]{2}\\)

        e.description = re.sub("\\(Exporté le:([0-9]{2}\\/){2}[0-9]{4} [0-9]{2}:[0-9]{2}\\)", "", e.description)
        e.description = e.description.strip()

        profs = re.findall(r"([a-zA-Z\-]+ [a-zA-Z\-]+)", e.description)
        groupes = re.findall(r"[a-zA-Z][0-9][a-zA-Z]*[0-9]*", e.description)

        elem = {
            "summary": e.name,
            "teachers": profs,
            "group": groupes,
            "description": e.description,
            "location": e.location,
            "start": datetime.fromisoformat(e.begin.isoformat()),
            "end": datetime.fromisoformat(e.end.isoformat()),
            "_id": e.uid,
        }

        # check if event already exists
        find_elem = col.find_one({"_id": e.uid})
        if find_elem is None:
            # insert
            col.insert_one(elem)
            inserted += 1
        else:
            # update
            col.update_one({"_id": e.uid}, {"$set": elem})
            updated += 1

    return inserted, updated
