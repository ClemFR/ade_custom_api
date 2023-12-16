import os
from queue import Queue
from threading import Thread
from scrappers.genere_ics import get_ics_file
import scrappers.mysql_database as mysqldb
import icsparser_thread
import shutil


class IcsWork:
    def __init__(self, category_path, date_debut, date_fin):
        self.category_path = category_path
        self.date_debut = date_debut
        self.date_fin = date_fin

    def do_work(self):
        pass


class IcsAll:
    def __init__(self, date_debut, date_fin):
        self.date_debut = date_debut
        self.date_fin = date_fin


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

    def __generate_ics(self, date_debut, date_fin, category_path, id_worker):

        libelle_groupe = category_path.split(">")[-1]

        # on génère le fichier ics
        ics_filepath = get_ics_file(category_path, date_debut, date_fin)

        if ics_filepath is None:
            print(f"[IcsGenerator-{id_worker}] ERROR ! No ics generated for {category_path} from {date_debut} to {date_fin} !")
            return

        # set filename to the last part of the path separated by >
        filename = libelle_groupe + ".ics"

        # on renomme le fichier pour que le parser conaisse la collection à affecter (ex : B3INFOTPA2.ics)
        dst = os.path.join(os.path.dirname(ics_filepath), filename)
        shutil.move(ics_filepath, dst)

        print(f"[IcsGenerator-{id_worker}] Ics generated for {category_path} from {date_debut} to {date_fin} !")
        print(f"[IcsGenerator-{id_worker}] Parsing {filename} ...")
        self.parser.queueWork.put(icsparser_thread.ParseWork(dst, libelle_groupe, date_debut, date_fin))

    def thread_worker(self, id):
        print(f"[IcsGenerator-{id}] Hello World !")
        while True:
            work = self.queueWork.get()
            if isinstance(work, IcsStop):
                print(f"[IcsGenerator-{id}] Stopping ...")
                break
            elif isinstance(work, IcsAll):
                # On génère un ics pour chaque ressource dans la base de donnée
                date_debut = work.date_debut
                date_fin = work.date_fin

                print(f"[IcsGenerator-{id}] Generating ics for all ...")
                lte_ressources = mysqldb.get_all_ressources_paths()

                max = len(lte_ressources)
                i = 0
                for res in lte_ressources:
                    i += 1
                    print(f"[IcsGenerator-{id}] Generating ics for {res} ({i}/{max})")
                    self.__generate_ics(date_debut, date_fin, res, id)
            else:
                # On génère un ics pour la ressource spécifiée en paramètre
                print(f"[IcsGenerator-{id}] Generating ics for {work.category_path} ...")
                self.__generate_ics(work.date_debut, work.date_fin, work.category_path, id)
