from queue import Queue
from threading import Thread
from parse_ics import parse_file
import os


class ParseWork:
    def __init__(self, ics_path, group, start_date, end_date):
        self.ics_path = ics_path
        self.group = group
        self.start_date = start_date
        self.end_date = end_date


class ParseStop:
    def __init__(self):
        pass


class IcsParser:

    def __init__(self):
        self.queueWork = Queue()
        self.workers = []
        self.init_workers()

    def init_workers(self):
        for i in range(1):
            t = Thread(target=self.thread_worker, args=(i,))
            t.start()
            self.workers.append(t)

    def stop_workers(self):
        for i in range(len(self.workers)):
            self.queueWork.put(ParseStop())

        for t in self.workers:
            t.join()

    def thread_worker(self, id):
        print(f"[IcsParser-{id}] Hello World !")
        while True:
            work = self.queueWork.get()
            if isinstance(work, ParseStop):
                print(f"[IcsParser-{id}] Stopping ...")
                break

            ics_path = work.ics_path
            group = work.group
            start_date = work.start_date
            end_date = work.end_date

            print(f"[IcsParser-{id}] Parsing {ics_path} ...")
            inserted, updated = parse_file(ics_path, group, start_date, end_date)
            print(f"[IcsParser-{id}] Parsing {ics_path} done, {inserted} inserted, {updated} updated !")

            os.remove(ics_path)
