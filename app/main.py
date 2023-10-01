import chrome_setup
from flask import Flask, request
from waitress import serve
import ade_queue
import work
import signal
import os


def create_app():
    app = Flask(__name__)

    with app.app_context():
        signal.signal(signal.SIGINT, receive_signal)
        signal.signal(signal.SIGTERM, receive_signal)

        ade_queue.init_workers()

    @app.route('/week/image/<id>/<date>')
    def ade_get_week_image(id, date):
        """
        Renvoie l'image de l'edt pour la ressource id à la date date
        :param id: l'identifiant de la ressource
        :param date: la date de la semaine au format AAAAMMJJ
        """

        width = request.args.get('width') or 1280
        height = request.args.get('height') or 720

        w = work.GenerateWeek(ade_id=id, date=date, width=width, height=height)
        queue_id = str(w.work_id)

        ade_queue.queueWork.put(w)
        _, img = work.wait_for_work_done(queue_id)

        if img is None:
            return "Timeout", 408
        else:
            return img

    @app.route('/day/image/<id>/<date>')
    def ade_get_day_image(id, date):
        """
        Renvoie l'image de l'edt pour la ressource id à la date date
        :param id: l'identifiant de la ressource
        :param date: la date du jour au format AAAAMMJJ
        """
        width = request.args.get('width') or 400
        height = request.args.get('height') or 720

        w = work.GenerateDay(ade_id=id, date=date, width=width, height=height)
        queue_id = str(w.work_id)

        ade_queue.queueWork.put(w)
        _, img = work.wait_for_work_done(queue_id)

        if img is None:
            return "Timeout", 408
        else:
            return img

    return app


def receive_signal(signum, stack):
    print('Received signal', signal.Signals(signum).name)
    if signum == signal.SIGINT or signum == signal.SIGTERM:
        print("Stopping workers")
        ade_queue.stop_workers()
        ade_queue.wait_workers_end()
        exit(0)


def validate_settings():
    SETTINGS_LIST = [
        "SELENIUM_HOST",
        "SELENIUM_PORT",
        "ADE_JSP_URL",
        "ADE_LOGIN",
        "ADE_PASSWORD",
        "ADE_YEAR_ID",
        "ADE_START_DATE",
        "APP_MODE",
        "WORKERS_COUNT",
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
