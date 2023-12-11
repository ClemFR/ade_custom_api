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

    req = """
        CREATE TABLE IF NOT EXISTS ressource (ID INT AUTO_INCREMENT PRIMARY KEY, nom VARCHAR(255), chemin VARCHAR(255));
        CREATE TABLE IF NOT EXISTS utilisateurs (ID INT AUTO_INCREMENT PRIMARY KEY, nom VARCHAR(255), prenom VARCHAR(255), mail VARCHAR(255), login VARCHAR(255), mdp VARCHAR(64), admin BOOLEAN, favorite_ressource VARCHAR(255));
    """

    cursor.execute(req, multi=True)
    conn.commit()

    cursor.close()
    conn.close()


def update_ressources_availables():
    # On vérifie que le fichier contenant les ressources existe
    if not os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ressources.txt")):
        print("[WARN] Auto scrapping des ressources désactivé : ")
        print("[WARN] Le fichier ressources.txt n'existe pas, veuillez générer une liste de ressources avec le script recupere_ressource_liste.py et le placer dans le dossier app.")
        return

    # On récupère les ressources dans le fichier
    f = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ressources.txt"), "r")
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

    req = ""

    for ressource in ressources:
        if ressource[1] not in res_name_to_path:
            req += f"DELETE FROM ressource WHERE ID = {ressource[0]};\n"
        else:
            req += f"UPDATE ressource SET chemin = '{res_name_to_path[ressource[1]]}'  WHERE ID = {ressource[0]};\n"
            del res_name_to_path[ressource[1]]

    for ressource in res_name_to_path.items():
        req += f"INSERT INTO ressource (nom, chemin) VALUES ('{ressource[0]}', '{ressource[1]}');\n"

    cursor.execute(req, multi=True)
    conn.commit()

    cursor.close()
    conn.close()
