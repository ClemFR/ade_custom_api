import os
from queue import Queue
from threading import Thread
from genere_ics import get_ics_file
import icsparser_thread
import shutil


class IcsWork:
    def __init__(self, category_path, date_debut, date_fin):
        self.category_path = category_path
        self.date_debut = date_debut
        self.date_fin = date_fin

    def do_work(self):
        pass


class IcsStop:
    def __init__(self):
        pass


class IcsGenerator:

    def __init__(self):
        self.queueWork = Queue()
        self.workers = []
        self.init_workers()

        self.parser = icsparser_thread.IcsParser()

    def init_workers(self):
        for i in range(1):
            t = Thread(target=self.thread_worker, args=(i,))
            t.start()
            self.workers.append(t)

    def stop_workers(self):
        for i in range(len(self.workers)):
            self.queueWork.put(IcsStop())

        for t in self.workers:
            t.join()

        self.parser.stop_workers()

    def thread_worker(self, id):
        print(f"[IcsGenerator-{id}] Hello World !")
        while True:
            work = self.queueWork.get()
            if isinstance(work, IcsStop):
                print(f"[IcsGenerator-{id}] Stopping ...")
                break
            category_path = work.category_path
            date_debut = work.date_debut
            date_fin = work.date_fin

            print(f"[IcsGenerator-{id}] Generating ics for {category_path} from {date_debut} to {date_fin} ...")

            libelle_groupe = category_path.split(">")[-1]
            ics_filepath = get_ics_file(category_path, date_debut, date_fin)

            # set filename to the last part of the path separated by >
            filename = libelle_groupe + ".ics"

            # on renomme le fichier pour que le parser conaisse la collection à affecter (ex : B3INFOTPA2.ics)
            dst = os.path.join(os.path.dirname(ics_filepath), filename)
            shutil.move(ics_filepath, dst)

            print(f"[IcsGenerator-{id}] Ics generated for {category_path} from {date_debut} to {date_fin} !")
            print(f"[IcsGenerator-{id}] Parsing {filename} ...")
            self.parser.queueWork.put(icsparser_thread.ParseWork(dst, libelle_groupe, date_debut, date_fin))
