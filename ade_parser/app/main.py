from flask import Flask, request
import signal
import icsgenerator_thread as icsgenerator
import os
import init_mysql
import auto_trigger


def create_app():
    def receive_signal(signal_number, frame):
        print(f"Received signal {signal_number}")
        ics_gen_instance.stop_workers()
        auto_trigger.stop_trigger_thread()
        exit(0)

    app = Flask(__name__)

    with app.app_context():
        signal.signal(signal.SIGINT, receive_signal)
        signal.signal(signal.SIGTERM, receive_signal)

        ics_gen_instance = icsgenerator.IcsGenerator()
        auto_trigger.start_trigger_thread(ics_gen_instance.queueWork)


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

    @app.route('/parse/ask/all/<datedebut>/<datefin>')
    def parse_all(datedebut, datefin):
        """
        Démarre le parsing d'ade pour toutes les catégories
        --> génère un fichier ics
        --> parse le fichier ics
        --> ajoute/modifie les informations dans la base de données

        Ex : http://localhost:5001/parse/ask/all/20231201/20231231
        :param datedebut: la date de début de la période à parser (format AAAAMMJJ)
        :param datefin: la date de fin de la période à parser (format AAAAMMJJ)
        """

        work = icsgenerator.IcsAll(date_debut=datedebut, date_fin=datefin)
        ics_gen_instance.queueWork.put(work)

        return "OK"

    return app


def validate_settings():
    SETTINGS_LIST = [
        "ADE_URL",
        "APP_MODE",
        "SELENIUM_SERVICE_NAME",
        "MONGO_SERVICE_NAME",
        "MYSQL_SERVICE_NAME",
    ]

    settings_ok = True
    for setting in SETTINGS_LIST:
        if setting not in os.environ and setting.strip() == "":
            print(f"Missing or empty setting {setting} in environment variables")
            settings_ok = False

    if settings_ok:
        print("Settings validated !")
    else:
        exit(1)


if __name__ == '__main__':
    validate_settings()
    init_mysql.wait_database_available()
    init_mysql.create_tables()
    init_mysql.update_ressources_available()

    app = create_app()
    app.run(host="0.0.0.0", port=5000)
