from flask import Flask, request
import signal
import icsgenerator_thread as icsgenerator
import os


def create_app():
    def receive_signal(signal_number, frame):
        print(f"Received signal {signal_number}")
        ics_gen_instance.stop_workers()
        exit(0)

    app = Flask(__name__)

    with app.app_context():
        signal.signal(signal.SIGINT, receive_signal)
        signal.signal(signal.SIGTERM, receive_signal)

        ics_gen_instance = icsgenerator.IcsGenerator()

    @app.route('/parse/ask/<path>/<datedebut>/<datefin>')
    def ask_parse(path, datedebut, datefin):
        """
        Démarre le parsing d'ade pour la catégorie "path"
        --> génère un fichier ics
        --> parse le fichier ics
        --> ajoute/modifie les informations dans la base de données

        Ex : http://localhost:5001/parse/ask/IUT%20Departement%20Informatique%3EBUT3%20INFORMATIQUE%20RACDV%3EUBFBA3TP%3EB3INFOTPA2/20231201/20231231
        :param path: la catégorie à parser
        :param datedebut: la date de début de la période à parser (format AAAAMMJJ)
        :param datefin: la date de fin de la période à parser (format AAAAMMJJ)
        """

        work = icsgenerator.IcsWork(category_path=path, date_debut=datedebut, date_fin=datefin)
        ics_gen_instance.queueWork.put(work)

        return "OK"



    return app


def validate_settings():
    SETTINGS_LIST = [
        "ADE_URL",
        "SELENIUM_HOST",
        "SELENIUM_PORT",
        "DATABASE_HOST",
        "DATABASE_PORT",
        "EXPOSE_PORT"
    ]

    for setting in SETTINGS_LIST:
        if setting not in os.environ:
            print(f"Missing setting {setting} in environment variables")
            exit(1)


if __name__ == '__main__':
    validate_settings()

    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ["EXPOSE_PORT"]))


