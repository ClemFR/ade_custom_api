import chrome_setup
from flask import Flask, request
import ade
from uuid import uuid4

app = Flask(__name__)


@app.route('/week/image/<id>/<date>')
def ade_get_image(id, date):
    """
    Renvoie l'image de l'edt pour la ressource id à la date date
    :param id: l'identifiant de la ressource
    :param date: la date de la semaine au format AAAAMMJJ
    """
    ade.switch_date(date)
    ade.switch_id(id)
    img = ade.get_edt_image(1920, 1080)



    if img is None:
        return "Timeout", 408
    else:
        html_img = f"<img src='{img}'/>"
        return html_img


with app.app_context():
    if chrome_setup.check_driver() is None:
        print("Chrome driver not found, exiting")
        exit(1)
    else:
        print("Chrome driver found, continuing")
        chrome_setup.setup_browser()
        ade.auth()

if __name__ == '__main__':
    app.run()
