from ics import Calendar
from pymongo import MongoClient
import os
from datetime import datetime
import re
from uuid import uuid4

client: None | MongoClient = None


def YYYYMMDD_to_datetime(date):
    return datetime(int(date[:4]), int(date[4:6]), int(date[6:8]), 0, 0, 0)


def mongo_connect():
    global client
    if client is None:
        client = MongoClient(os.environ["MONGO_DATABASE_HOST"], int(os.environ["MONGO_DATABASE_PORT"]))
    db = client.ade
    return db


def parse_file(ics_path, group_name, start_date, end_date):
    ID_PROCESS = str(uuid4())
    # On regarde si le groupe contient un nombre entre [] (ex : B3INFOTPA2[1])
    # Si oui, on le retire
    if "[" in group_name:
        group_name = group_name[:group_name.index("[")]

    print(f"[ParseFile] Updating : {group_name} from {start_date} to {end_date} with id {ID_PROCESS}")

    inserted = 0
    updated = 0
    deleted = 0

    with open(ics_path, 'r') as my_file:
        c = Calendar(my_file.read())

    db = mongo_connect()
    # col = db[col_name]  # Ex : B3INFOTPA2
    col = db["schedules"]

    # On flag les anciens cours dans la range de dates avec l'uuid du process
    col.update_many(
        {"$and": [
            {"start": {"$gte": YYYYMMDD_to_datetime(start_date)}},
            {"end": {"$lte": YYYYMMDD_to_datetime(end_date).replace(hour=23, minute=59, second=59)}},
            {"tp_groups": {"$in": [group_name]}},
        ]},
        {
            "$set": {"update_process_id": ID_PROCESS}
        }
    )

    for e in c.events:
        # regex match profs : ([a-zA-Z\-]* [a-zA-Z\-]*)
        # regex match groupes : [a-zA-Z][0-9][a-zA-Z]*[0-9]*
        # regex retirer heure génération ics : \\(Exporté le:([0-9]{2}\\/){2}[0-9]{4} [0-9]{2}:[0-9]{2}\\)

        e.description = re.sub("\\(Exporté le:([0-9]{2}\\/){2}[0-9]{4} [0-9]{2}:[0-9]{2}\\)", "", e.description)
        e.description = e.description.strip()

        profs = re.findall(r"([a-zA-Z\-]+ [a-zA-Z\-]+)", e.description)
        groupes_ade = re.findall(r"[a-zA-Z][0-9][a-zA-Z]*[0-9]*", e.description)

        elem = {
            "summary": e.name,
            "teachers": profs,
            "ade_groups": groupes_ade,
            "tp_groups": [group_name],
            "description": e.description,
            "location": e.location,
            "start": datetime.fromisoformat(e.begin.isoformat()),
            "end": datetime.fromisoformat(e.end.isoformat()),
            "_id": e.uid,
        }

        # on check si l'élément location est vide
        # si vide on supprime
        if elem["location"] == "":
            elem.pop("location")

        # check if event already exists
        find_elem = col.find_one({"_id": e.uid})
        if find_elem is None:
            # insert
            col.insert_one(elem)
            inserted += 1
        else:
            # On remets les groupes insérés en BDD dans le document qui va être modifié
            for g in find_elem["tp_groups"]:
                if g not in elem["tp_groups"]:
                    elem["tp_groups"].append(g)

            # Update
            col.update_one({"_id": e.uid}, {"$set": elem, "$unset": {"update_process_id": ""}})
            updated += 1

    # On récupère les cours qui sont encore flag
    cursor_cours = col.find({
        "update_process_id": ID_PROCESS
    })

    for cour in cursor_cours:
        deleted += 1

        if len(cour["tp_groups"]) == 1:
            # Il ne reste que ce groupe dans la liste des TP bind à ce cour, on supprime le cours de la BD
            col.delete_one({
                "_id": cour["_id"]
            })

        else:
            # On supprime l'ID de groupe dans le cours
            for i in range(len(cour["tp_groups"])):
                if cour["tp_groups"][i] == group_name:
                    cour["tp_groups"].pop(i)
                    break

            # On retire de cours le champ update_process_id
            cour.pop("update_process_id")

            # On mets à jour le cours avec le groupe en moins
            col.update_one({"_id": cour["_id"]}, {"$set": cour, "$unset": {"update_process_id": ""}})

    return inserted, updated, deleted
