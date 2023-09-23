import ade as ade
from queue import Queue

import ade_utils
import chrome_setup
import threading as th
import work as work

queueWork = Queue()
queueResult = Queue()

workers = []
workers_count = 1


def init_workers():
    if workers_count == 0:
        print("[WARNING] Workers count = 0, no worker will be created")
    for i in range(workers_count):
        th.Thread(target=thread_init_worker).start()


def thread_init_worker():
    global workers
    workers.append(Worker())


def stop_workers():
    for w in workers:
        w.thread_end = True
    for i in range(workers_count):
        print("Stopping worker " + str(i))
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

    def __init__(self):
        self.status = "init"
        self.driver = chrome_setup.setup_browser()
        ade.auth(self.driver)

        self.thr_process = th.Thread(target=self.thread)
        self.thr_process.start()

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

    def process(self, item):
        if isinstance(item, work.EndThread):
            self.thread_end = True

        elif isinstance(item, work.GenerateWeek):
            item: work.GenerateWeek  # Autocomplétion IDE
            ade.switch_week_date(self.driver, item.date)

            if self.selected_days != (0, 1, 2, 3, 4,):
                self.selected_days = (0, 1, 2, 3, 4,)
                ade.switch_selected_days(self.driver, (0, 1, 2, 3, 4,))

            ade.switch_id(self.driver, item.ade_id)
            img = ade.get_edt_image(self.driver, item.width, item.height)
            queueResult.put((item.work_id, img,))

        elif isinstance(item, work.GenerateDay):
            item: work.GenerateDay  # Autocomplétion IDE
            ade.switch_week_date(self.driver, item.date)
            day_id = (ade_utils.calculate_day_id(item.date),)

            if self.selected_days != day_id:
                self.selected_days = day_id
                ade.switch_selected_days(self.driver, day_id)

            ade.switch_id(self.driver, item.ade_id)
            img = ade.get_edt_image(self.driver, item.width, item.height)
            queueResult.put((item.work_id, img,))