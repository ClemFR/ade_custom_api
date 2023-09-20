import chrome_setup
from flask import Flask, request
import ade_queue
import work
from time import sleep
import atexit
import os
import signal

app = Flask(__name__)


@app.route('/week/image/<id>/<date>')
def ade_get_image(id, date):
    """
    Renvoie l'image de l'edt pour la ressource id à la date date
    :param id: l'identifiant de la ressource
    :param date: la date de la semaine au format AAAAMMJJ
    """
    w = work.GenerateWeek(ade_id=id, date=date)
    queue_id = str(w.work_id)

    ade_queue.queueWork.put(w)
    work_found = False
    img = None

    while not work_found:
        for i in range(ade_queue.queueResult.qsize()):
            work_id, img = ade_queue.queueResult.get(block=True, timeout=None)
            if str(work_id) == str(queue_id):
                work_found = True
                break
            else:
                ade_queue.queueResult.put((work_id, img,))
        sleep(.4)

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
        ade_queue.init_workers()

if __name__ == '__main__':

    app.run()
