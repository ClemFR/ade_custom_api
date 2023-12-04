from flask import Flask, request
from waitress import serve
import signal
import os


def receive_signal(signum, stack):
    print('Received signal', signal.Signals(signum).name)
    if signum == signal.SIGINT or signum == signal.SIGTERM:
        exit(0)


def create_app():
    app = Flask(__name__)

    with app.app_context():
        signal.signal(signal.SIGINT, receive_signal)
        signal.signal(signal.SIGTERM, receive_signal)

        @app.route("/week/<promo_id>/<day>")
        def get_week(promo_id, day):
            """
            Get entire week for the specified promotion
            :param promo_id: The promotion (Ex : B3INFOTPA2)
            :param day: A day in the week (format AAAAMMJJ)
            :return: Json array representing the schedule.
            """
            pass

        @app.route("/day/<promo_id>/<day>")
        def get_day(promo_id, day):
            """
            Get specific day for the specified promotion
            :param promo_id: The promotion (Ex : B3INFOTPA2)
            :param day: A day in the week (format AAAAMMJJ)
            :return: Json array representing the schedule.
            """
            pass

        @app.route("/teacher/<name>/<day>")
        def get_teacher_schedule(name, day):
            """
            Get the schedule for the specified teacher
            :param name: The name of the teacher to get the schedule
            :param day: A day in the week (format AAAAMMJJ)
            :return: Json array representing the schedule.
            """
            pass

        @app.route("/room/<name>/<day>")
        def get_room_schedule(name, day):
            """
            Get the schedule for the specified room
            :param name: The name of the room to get the schedule
            :param day: A day in the week (format AAAAMMJJ)
            :return: Json array representing the schedule.
            """
            pass

    return app


def validate_settings():
    SETTINGS_LIST = [
        "DATABASE_HOST",
        "DATABASE_PORT",
        "APP_MODE"
    ]

    for setting in SETTINGS_LIST:
        if setting not in os.environ:
            print(f"Missing setting {setting} in environment variables")
            exit(1)


if __name__ == '__main__':

    validate_settings()

    app_mode = os.environ.get('APP_MODE', 'prod')

    if app_mode == "prod":
        serve(create_app(), host='0.0.0.0', port=5000)
    else:
        app = create_app()
        app.run(host='0.0.0.0')
