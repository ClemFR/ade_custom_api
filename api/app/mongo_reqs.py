import os
from pymongo import MongoClient
from datetime import datetime

__db_cnx: None | MongoClient = None


def __get_mongo():
    global __db_cnx
    if __db_cnx is None:
        client = MongoClient(os.environ.get("MONGO_SERVICE_NAME"), 27017)

        __db_cnx = client.ade
    return __db_cnx


def YYYYMMDD_to_datetime(date):
    return datetime(int(date[:4]), int(date[4:6]), int(date[6:8]), 0, 0, 0)


def get_class_schedule(classname, start, end):
    """
    Get the schedule for the specified class.
    :param classname: The class or list of classes that request the schedule
    :param start: Starting date (YYYYMMDD, inclusive)
    :param end: Ending date (YYYYMMDD, inclusive)
    :return: json array containing the schedule
    """

    db = __get_mongo()
    col = db["schedules"]

    # On détecte si on a une liste de classes ou une seule
    if "," in classname:
        classname = classname.split(",")
    else:
        classname = [classname]

    req = {
        "tp_groups": {"$in": classname},
        "$and": [
            {"start": {"$gte": YYYYMMDD_to_datetime(start)}},
            {"end": {"$lte": YYYYMMDD_to_datetime(end).replace(hour=23, minute=59, second=59)}}
        ]
    }

    print(req)
    rep = col.find(req)

    rep = list(rep)

    for r in rep:
        r["start"] = r["start"].isoformat()
        r["end"] = r["end"].isoformat()

    return rep


def get_teacher_schedule(name, start, end):
    """
    Get the schedule for the specified teacher
    :param name: The name of the teacher to get the schedule
    :param start: Starting date (YYYYMMDD, inclusive)
    :param end: Ending date (YYYYMMDD, inclusive)
    :return: json array containing the schedule
    """

    db = __get_mongo()
    col = db["schedules"]

    req = {
        "teachers": {"$in": [name]},
        "$and": [
            {"start": {"$gte": YYYYMMDD_to_datetime(start)}},
            {"end": {"$lte": YYYYMMDD_to_datetime(end).replace(hour=23, minute=59, second=59)}}
        ]
    }

    print(req)
    rep = col.find(req)

    rep = list(rep)

    for r in rep:
        r["start"] = r["start"].isoformat()
        r["end"] = r["end"].isoformat()

    return rep


def get_room_schedule(name, start, end):
    """
    Get the schedule for the specified room
    :param name: The name of the room to get the schedule
    :param start: Starting date (YYYYMMDD, inclusive)
    :param end: Ending date (YYYYMMDD, inclusive)
    :return: json array containing the schedule
    """

    db = __get_mongo()
    col = db["schedules"]

    req = {
        "location": name,
        "$and": [
            {"start": {"$gte": YYYYMMDD_to_datetime(start)}},
            {"end": {"$lte": YYYYMMDD_to_datetime(end).replace(hour=23, minute=59, second=59)}}
        ]
    }

    print(req)
    rep = col.find(req)

    rep = list(rep)

    for r in rep:
        r["start"] = r["start"].isoformat()
        r["end"] = r["end"].isoformat()

    return rep


def get_teachers_list():
    """
    Get the list of all teachers
    :return: json array containing the list of teachers
    """

    db = __get_mongo()
    col = db["schedules"]

    aggregate = [
    {
        '$match': {
            'teachers.0': {
                '$exists': True
            }
        }
    }, {
        '$unset': [
            'start', 'end', 'location', 'description', 'tp_groups', 'ade_groups', 'summary', '_id'
        ]
    }, {
        '$unwind': {
            'path': '$teachers'
        }
    }, {
        '$group': {
            '_id': '$teachers'
        }
    }, {
        '$group': {
            '_id': 'null',
            'teachers': {
                '$push': '$$ROOT._id'
            }
        }
    }, {
        '$project': {
            '_id': 0
        }
    }
]

    rep = col.aggregate(aggregate)
    rep = list(rep)
    if len(rep) == 0:
        return []
    rep = rep[0]["teachers"]

    return list(rep)


def get_promo_list():
    """
    Get the list of all promotions
    :return: json array containing the list of promotions
    """

    db = __get_mongo()
    col = db["schedules"]

    aggregate = [
    {
        '$match': {
            'tp_groups.0': {
                '$exists': True
            }
        }
    }, {
        '$unset': [
            'start', 'end', 'location', 'description', 'teachers', 'ade_groups', 'summary', '_id'
        ]
    }, {
        '$unwind': {
            'path': '$tp_groups'
        }
    }, {
        '$group': {
            '_id': '$tp_groups'
        }
    }, {
        '$group': {
            '_id': 'null',
            'tp_groups': {
                '$push': '$$ROOT._id'
            }
        }
    }, {
        '$project': {
            '_id': 0
        }
    }
]

    rep = col.aggregate(aggregate)
    rep = list(rep)

    if len(rep) == 0:
        return []
    rep = rep[0]["tp_groups"]

    return list(rep)


def get_rooms_list():
    """
    Get the list of all rooms
    :return: json array containing the list of rooms
    """

    db = __get_mongo()
    col = db["schedules"]

    aggregate = [
    {
        '$match': {
            'location': {
                '$exists': True
            }
        }
    }, {
        '$unset': [
            'start', 'end', 'teachers', 'description', 'tp_groups', 'ade_groups', 'summary', '_id'
        ]
    }, {
        '$unwind': {
            'path': '$location'
        }
    }, {
        '$group': {
            '_id': '$location'
        }
    }, {
        '$group': {
            '_id': None,
            'location': {
                '$push': '$$ROOT._id'
            }
        }
    }, {
        '$project': {
            '_id': 0
        }
    }
]

    rep = col.aggregate(aggregate)
    rep = list(rep)

    if len(rep) == 0:
        return []
    rep = rep[0]["location"]

    return list(rep)