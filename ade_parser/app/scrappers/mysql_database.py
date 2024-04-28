from mysql import connector
import os


def __get_cnx():
    return connector.connect(
        host=os.environ.get("MYSQL_SERVICE_NAME"),
        port=3306,
        user="root",
        database="ade"
    )


def get_all_ressources_paths():
    conn = __get_cnx()
    cursor = conn.cursor()

    req = """
        SELECT * FROM ressource;
    """

    cursor.execute(req)
    ressources = cursor.fetchall()

    cursor.close()
    conn.close()

    # On ne prend que les chemins
    ressources = [r[2] for r in ressources]

    return ressources
