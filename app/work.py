import uuid
from time import sleep

import ade_queue


class GenerateWeek:
    def __init__(self, ade_id, date, width=1280, height=720):
        self.ade_id = ade_id
        self.date = date
        self.width = width
        self.height = height

        self.work_id = uuid.uuid4()


class GenerateDay:
    def __init__(self, ade_id, date, width=400, height=720):
        self.ade_id = ade_id
        self.date = date
        self.width = width
        self.height = height

        self.work_id = uuid.uuid4()


class EndThread:
    pass


def wait_for_work_done(queue_id):
    work_found = False
    work_done = None

    while not work_found:
        for i in range(ade_queue.queueResult.qsize()):
            work_done = ade_queue.queueResult.get(block=True, timeout=None)
            if str(work_done[0]) == str(queue_id):
                work_found = True
                break
            else:
                ade_queue.queueResult.put(work_done)
        sleep(.4)

    return work_done