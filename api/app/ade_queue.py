import ade as ade
from queue import Queue

import ade_utils
import chrome_setup
import threading as th
import work as work

import os

queueWork = Queue()
queueResult = Queue()

workers = []
workers_count = 0


def init_workers():
    global workers_count
    workers_count = int(os.environ.get('WORKERS_COUNT', 1))

    if workers_count == 0:
        print("[WARNING] Workers count = 0, no worker will be created")
    for i in range(workers_count):
        th.Thread(target=thread_init_worker, args=(i,)).start()


def thread_init_worker(worker_id=0):
    global workers
    workers.append(Worker(worker_id))


def stop_workers():
    for w in workers:
        w.thread_end = True
    for i in range(workers_count):
        queueWork.put(work.EndThread())


def wait_workers_end():
    for w in workers:
        w.thr_process.join()


class Worker:
    status = "stopped"
    driver = None
    thread_end = False
    thr_process: th.Thread
    selected_days = None
    selected_week = None
    selected_id = None

    def __init__(self, worker_id=0):
        self.worker_id = worker_id
        self.status = "init"
        print(f"Worker {worker_id} initializing...")

        self.driver = chrome_setup.setup_browser()
        ade.auth(self.driver)

        self.thr_process = th.Thread(target=self.thread)
        self.thr_process.start()
        print(f"Worker {worker_id} started !")

    def thread(self):
        self.status = "running"
        while not self.thread_end:
            item = queueWork.get(block=True, timeout=None)
            if not self.thread_end:
                self.process(item)
                queueWork.task_done()
            else:
                break
        self.status = "stopped"
        try:
            self.driver.close()
        except:
            pass
        self.driver = None
        print(f"Worker {self.worker_id} stopped !")

    def process(self, item):
        if isinstance(item, work.EndThread):
            self.thread_end = True
            return

        # Le travail n'est pas un travail de fin de thread
        if not ade.test_driver_cnx(self.driver):  # Vérifie si le token ade est toujours valide, sinon reconnecte
            ade.auth(self.driver)
            # reset selected days, week, and id
            self.selected_days = None
            self.selected_week = None
            self.selected_id = None



        ###############################################
        #             GENERATION SEMAINES             #
        ###############################################
        if isinstance(item, work.GenerateWeek):
            item: work.GenerateWeek  # Autocomplétion IDE
            if self.selected_week != ade_utils.calculate_week(item.date):
                self.selected_week = ade_utils.calculate_week(item.date)
                ade.switch_week_date(self.driver, item.date)

            if self.selected_days != (0, 1, 2, 3, 4,):
                self.selected_days = (0, 1, 2, 3, 4,)
                ade.switch_selected_days(self.driver, (0, 1, 2, 3, 4,))

            if self.selected_id != item.ade_id:
                self.selected_id = item.ade_id
                ade.switch_id(self.driver, item.ade_id)

            img = ade.get_edt_image(self.driver, item.width, item.height)
            queueResult.put((item.work_id, img,))

        ###############################################
        #              GENERATION JOURS               #
        ###############################################
        elif isinstance(item, work.GenerateDay):
            item: work.GenerateDay  # Autocomplétion IDE
            if self.selected_week != ade_utils.calculate_week(item.date):
                self.selected_week = ade_utils.calculate_week(item.date)
                ade.switch_week_date(self.driver, item.date)

            day_id = (ade_utils.calculate_day_id(item.date),)

            if self.selected_days != day_id:
                self.selected_days = day_id
                ade.switch_selected_days(self.driver, day_id)

            if self.selected_id != item.ade_id:
                self.selected_id = item.ade_id
                ade.switch_id(self.driver, item.ade_id)

            img = ade.get_edt_image(self.driver, item.width, item.height)
            queueResult.put((item.work_id, img,))