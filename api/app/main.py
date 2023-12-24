from flask import Flask, request
from waitress import serve
import signal
import os
import mongo_reqs as mr
from datetime import datetime, timedelta
import requests as req


def receive_signal(signum, stack):
    print('Received signal', signal.Signals(signum).name)
    if signum == signal.SIGINT or signum == signal.SIGTERM:
        exit(0)


def create_app():
    app = Flask(__name__)

    with app.app_context():
        signal.signal(signal.SIGINT, receive_signal)
        signal.signal(signal.SIGTERM, receive_signal)

        @app.route("/admin/scrap_all/<start_date>/<end_date>")
        def admin_launch_scrap_all(start_date, end_date):
            """
            Launch the scrap of all the promotions
            """

            # Getting the headers
            headers = request.headers
            # Checking if the header is present
            if "X-Admin-Key" not in headers:
                return "Missing X-Admin-Key header", 401
            # Checking if the header is correct
            if headers["X-Admin-Key"] != os.environ["ADMIN_KEY"]:
                return "Wrong X-Admin-Key header", 401

            print("Launching scrap all")
            req.get("http://" + os.environ[
                "PARSER_ADDRESS"] + f"/parse/ask/all/{start_date}/{end_date}")
            return "", 200

        @app.route("/week/<promo_id>/<day>")
        def get_week(promo_id, day):
            """
            Get entire week for the specified promotion
            :param promo_id: The promotion (Ex : B3INFOTPA2) or a list of promotions (Ex : B3INFOTPA2,B3INFOTPA3)
            :param day: A day in the week (format AAAAMMJJ)
            :return: Json array representing the schedule.
            """

            week_start = datetime.strptime(day, "%Y%m%d")
            # Get week start to monday
            week_start = week_start - timedelta(days=week_start.weekday())

            week_end = week_start + timedelta(days=6)
            print("Requete getWeek : " + str(promo_id) + " --> " + str(week_start) + " --> " + str(week_end))

            return mr.get_class_schedule(promo_id, week_start.strftime("%Y%m%d"), week_end.strftime("%Y%m%d"))

        @app.route("/day/<promo_id>/<day>")
        def get_day(promo_id, day):
            """
            Get specific day for the specified promotion
            :param promo_id: The promotion (Ex : B3INFOTPA2) or a list of promotions (Ex : B3INFOTPA2,B3INFOTPA3)
            :param day: A day in the week (format AAAAMMJJ)
            :return: Json array representing the schedule.
            """
            print("Requete getDay : " + str(promo_id) + " --> " + str(day))

            return mr.get_class_schedule(promo_id, day, day)

        @app.route("/teacher/day/<name>/<day>")
        def get_teacher_day(name, day):
            """
            Get the schedule for the specified teacher
            :param name: The name of the teacher to get the schedule
            :param day: A day in the week (format AAAAMMJJ)
            :return: Json array representing the schedule.
            """

            return mr.get_teacher_schedule(name, day, day)

        @app.route("/teacher/week/<name>/<day>")
        def get_teacher_week(name, day):
            """
            Get the schedule for the specified teacher
            :param name: The name of the teacher to get the schedule
            :param day: A day in the week (format AAAAMMJJ)
            :return: Json array representing the schedule.
            """

            week_start = datetime.strptime(day, "%Y%m%d")
            # Get week start to monday
            week_start = week_start - timedelta(days=week_start.weekday())

            week_end = week_start + timedelta(days=6)
            print("Requete getWeek : " + str(name) + " --> " + str(week_start) + " --> " + str(week_end))

            return mr.get_teacher_schedule(name, week_start.strftime("%Y%m%d"), week_end.strftime("%Y%m%d"))


        @app.route("/room/<name>/<day>")
        def get_room_schedule(name, day):
            """
            Get the schedule for the specified room
            :param name: The name of the room to get the schedule
            :param day: A day in the week (format AAAAMMJJ)
            :return: Json array representing the schedule.
            """

            return mr.get_room_schedule(name, day, day)

        @app.route("/teachers")
        def get_teachers():
            """
            Get the list of teachers
            :return: Json array representing the list of teachers
            """

            return mr.get_teachers_list()

        @app.route("/promos")
        def get_promos():
            """
            Get the list of promotions
            :return: Json array representing the list of promotions
            """

            return mr.get_promo_list()

        @app.route("/rooms")
        def get_rooms():
            """
            Get the list of rooms
            :return: Json array representing the list of rooms
            """

            return mr.get_rooms_list()

    return app


def validate_settings():
    SETTINGS_LIST = [
        "PARSER_ADDRESS",
        "ADMIN_KEY",
        "DATABASE_HOST",
        "DATABASE_PORT",
        "APP_MODE",
        "EXPOSE_PORT"
    ]

    for setting in SETTINGS_LIST:
        if setting not in os.environ and setting.strip() == "":
            print(f"Missing or empty setting {setting} in environment variables")
            exit(1)

    print("Settings validated !")


if __name__ == '__main__':

    validate_settings()

    app_mode = os.environ.get('APP_MODE', 'prod')

    if app_mode == "prod":
        serve(create_app(), host='0.0.0.0', port=int(os.environ["EXPOSE_PORT"]))
    else:
        app = create_app()
        app.run(host='0.0.0.0', port=int(os.environ["EXPOSE_PORT"]))
