import threading as th
import time
from datetime import datetime, timedelta
from icsgenerator_thread import IcsAll

stop_loop_thread = False
timer_exit = th.Event()


def start_trigger_thread(queue_work):
    """
    Démarre le thread qui va lancer le scan de tous les edt tous les jours à 4h du matin
    """
    thread = th.Thread(target=trigger_thread, args=(queue_work,))
    thread.start()


def stop_trigger_thread():
    """
    Arrête le thread qui va lancer le scan de tous les edt tous les jours à 4h du matin
    """
    global stop_loop_thread
    global timer_exit
    stop_loop_thread = True
    timer_exit.set()


def trigger_thread(queue_work):
    """
    Fonction qui va lancer le scan de tous les edt tous les jours à 4h du matin
    """
    global stop_loop_thread
    global timer_exit
    while not stop_loop_thread:

        # On regarde si on est entre 00 et 04h du matin
        now = datetime.now()
        time_goal = datetime.now()

        if 0 <= now.hour < 4:
            # On ne change pas la date du jour, on mets juste l'heure à 4h00
            time_goal = time_goal.replace(hour=4, minute=0, second=0)
        else:
            # On passe au jour suivant et on mets l'heure à 4h00
            time_goal = time_goal.replace(hour=4, minute=0, second=0)
            time_goal = time_goal + timedelta(days=1)

        # On calcule le temps à attendre avant d'effectuer le scan
        time_to_wait = (time_goal - now).total_seconds()

        # On attend le temps calculé
        print(f"[AutoTrigger] Waiting {time_to_wait} seconds before triggering scan ...")
        timer_exit.wait(time_to_wait)

        if stop_loop_thread:
            break

        date_debut = time.strftime("%Y%m%d")
        date_fin = time.strftime("%Y%m%d", time.localtime(time.time() + 3600 * 24 * 15))
        queue_work.put(IcsAll(date_debut=date_debut, date_fin=date_fin))
