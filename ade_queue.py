import multi.ade as ade
from queue import Queue
import chrome_setup
import threading as th
import multi.work as work
from time import sleep

queueWork = Queue()
queueResult = Queue()


class Worker:
    driver = None
    thread_end = False
    thr_process: th.Thread

    def __init__(self):
        self.driver = chrome_setup.setup_browser()
        ade.auth(self.driver)

        thr_process = th.Thread(target=self.thread)
        thr_process.start()

    def thread(self):
        while not self.thread_end:
            item = queueWork.get()
            self.process(item)
            queueWork.task_done()

    def process(self, item):
        if isinstance(item, work.EndThread):
            thread_end = True
        elif isinstance(item, work.GenerateWeek):
            item: work.GenerateWeek
            ade.switch_week_date(self.driver, item.date)
            ade.switch_id(self.driver, item.ade_id)
            img = ade.get_edt_image(self.driver, item.width, item.height)
            queueResult.put((item.work_id, img,))
