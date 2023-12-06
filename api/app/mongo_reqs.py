import os
from pymongo import MongoClient
from datetime import datetime


__db_cnx: None | MongoClient = None


def __get_mongo():
    global __db_cnx
    if __db_cnx is None:
        client = MongoClient(os.environ["DATABASE_HOST"], int(os.environ["DATABASE_PORT"]))

        __db_cnx = client.ade
    return __db_cnx


def YYYYMMDD_to_datetime(date):
    return datetime(int(date[:4]), int(date[4:6]), int(date[6:8]), 0, 0, 0)


def get_class_schedule(classname, start, end):
    """
    Get the schedule for the specified class.
    :param classname: The class that request the schedule
    :param start: Starting date (YYYYMMDD, inclusive)
    :param end: Ending date (YYYYMMDD, inclusive)
    :return: json array containing the schedule
    """
    
    db = __get_mongo()
    col = db["schedules"]

    req = {
        "group": {"$in": [classname]},
        "$and": [
            {"start": {"$gte": YYYYMMDD_to_datetime(start)}},
            {"end": {"$lte": YYYYMMDD_to_datetime(end).replace(hour=23, minute=59, second=59)}}
        ]
    }

    print(req)
    rep = col.find(req)

    return list(rep)


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

    return list(rep)


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

    return list(rep)
