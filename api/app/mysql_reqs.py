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


def log(user, type, message, date_start=None, date_end=None):
    conn = __get_cnx()

    cursor = conn.cursor()

    cursor.execute("INSERT INTO log (date, user, type, message, date_start, date_end) VALUES (NOW(), %s, %s, %s, %s, %s)", (user, type, message, date_start, date_end))

    conn.commit()

    cursor.close()
    conn.close()


def install(user):
    conn = __get_cnx()

    cursor = conn.cursor()

    cursor.execute("INSERT INTO install (date, user) VALUES (NOW(), %s)", (user,))

    conn.commit()

    cursor.close()
    conn.close()