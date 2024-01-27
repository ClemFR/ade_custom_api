import time

from mysql import connector
import os

cnx = None


def __get_cnx():
    return connector.connect(
        host=os.environ["MYSQL_DATABASE_HOST"],
        port=int(os.environ["MYSQL_DATABASE_PORT"]),
        user="root",
        database="ade"
    )


def create_tables():
    conn = __get_cnx()

    cursor = conn.cursor()

    print("[INFO] Creating tables if not exists ...")

    cursor.execute("CREATE TABLE IF NOT EXISTS ressource (ID INT AUTO_INCREMENT PRIMARY KEY, nom VARCHAR(255), chemin VARCHAR(255))")
    cursor.execute("CREATE TABLE IF NOT EXISTS log (ID INT AUTO_INCREMENT PRIMARY KEY, date DATETIME, user VARCHAR(64), type VARCHAR(255), message TEXT, date_start DATETIME, date_end DATETIME)")
    cursor.execute("CREATE TABLE IF NOT EXISTS install (ID INT AUTO_INCREMENT PRIMARY KEY, date DATETIME, user VARCHAR(64))")

    conn.commit()

    cursor.close()
    conn.close()


def update_ressources_available():
    # On vérifie que le fichier contenant les ressources existe

    fichier = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    if os.environ["APP_MODE"] == "prod":
        fichier = os.path.join(fichier, "ressources.txt")
    else:
        fichier = os.path.join(fichier, "ressources_dev.txt")

    print(f"[INFO] Auto scrapping des ressources activé : {fichier}")

    if not os.path.exists(fichier):
        print("[WARN] Auto scrapping des ressources désactivé : ")
        print("[WARN] Le fichier ressources.txt (ressources_dev.txt) n'existe pas, veuillez générer une liste de ressources avec le script recupere_ressource_liste.py et le placer dans le dossier app.")
        return

    # On récupère les ressources dans le fichier
    f = open(fichier, "r")
    res_file_lines = f.readlines()
    f.close()

    res_name_to_path = {}
    for line in res_file_lines:
        name = line.split(">")[-1].strip()
        path = line.strip()
        res_name_to_path[name] = path

    conn = __get_cnx()
    cursor = conn.cursor()

    req = """
        SELECT * FROM ressource;
    """

    cursor.execute(req)
    ressources = cursor.fetchall()
    cursor.close()

    for ressource in ressources:
        cursor = conn.cursor()
        if ressource[1] not in res_name_to_path:
            cursor.execute(f"DELETE FROM ressource WHERE ID = '{ressource[0]}'")
        else:
            cursor.execute(f"UPDATE ressource SET chemin = '{res_name_to_path[ressource[1]]}'  WHERE ID = {ressource[0]}")
            del res_name_to_path[ressource[1]]
        cursor.close()

    for ressource in res_name_to_path.items():
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO ressource (nom, chemin) VALUES ('{ressource[0]}', '{ressource[1]}')")
        cursor.close()

    conn.commit()
    conn.close()


def wait_database_available():
    cnx_ok = False
    while not cnx_ok:
        try:
            cnx = __get_cnx()
            cnx_ok = True
            cnx.close()
        except:
            print("Waiting for database to be available ...")
            time.sleep(2)
