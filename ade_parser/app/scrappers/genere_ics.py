import datetime
import re
import time
import traceback

from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import requests
import os
import zipfile
import base64
import io
from .selenium_util import open_remote_browser, ade_unroll_line


def __select_line(line_text, driver):
    # On regarde si la chaine contient un nombre entre []
    rgx = r"\[[0-9]\]"
    match = re.findall(rgx, line_text)
    if len(match) > 0:
        # On récupère le nombre
        nb = int(match[0][1:-1])

        # On enlève le nombre de la chaine
        line_text = line_text.replace(f"[{nb}]", "")

        # On sélectionne la ligne à l'index nb
        driver.find_elements(By.XPATH, f"//span[contains(text(), '{line_text}')]")[nb].click()

    else:
        # Pas de nombre, on sélectionne la première ligne
        driver.find_element(By.XPATH, f"//span[contains(text(), '{line_text}')]").click()


def __date_selector(date, date_field, driver):
    """
    Sélectionne la date dans le calendrier pour le champ date_field
    :param date: La date au format AAAAMMJJ
    :param date_field: Le champ de date à modifier
    :param driver: Le driver selenium
    """

    # Coordonnées des mois dans le tableau (ligne, colonne)
    MONTH_COORDINATES = {
        "01": (0, 0),
        "02": (1, 0),
        "03": (2, 0),
        "04": (3, 0),
        "05": (4, 0),
        "06": (5, 0),
        "07": (0, 1),
        "08": (1, 1),
        "09": (2, 1),
        "10": (3, 1),
        "11": (4, 1),
        "12": (5, 1),
    }

    # On ouvre le calendrier
    date_field.click()

    wait30s = WebDriverWait(driver, 30)
    parent_calendar = wait30s.until(lambda driver: driver.find_element(By.CLASS_NAME, 'x-date-menu'))

    # On déroule le sélecteur mois / année
    parent_calendar.find_elements(By.TAG_NAME, 'button')[0].click()
    sleep(.5)

    # On sélectionne la table contenant tous les boutons
    child = parent_calendar.find_element(By.CLASS_NAME, 'x-date-mp-month')
    parent = child.find_element(By.XPATH, './..')
    while parent.tag_name != 'table':
        child = parent
        parent = child.find_element(By.XPATH, './..')

    # On sélectionne l'année (avec le texte)
    parent.find_element(By.XPATH, f"//a[contains(text(), '{date[0:4]}')]").click()

    # On sélectionne le mois (avec les coordonnées)
    # sélection de la ligne
    mois = str(date[4:6])
    ligne = parent.find_elements(By.TAG_NAME, 'tr')[MONTH_COORDINATES[mois][0]]
    # sélection et clic de la colonne
    ligne.find_elements(By.TAG_NAME, 'td')[MONTH_COORDINATES[mois][1]].click()

    # On valide le mois et l'année
    parent_calendar.find_element(By.CLASS_NAME, 'x-date-mp-ok').click()

    # On sélectionne le jour
    no_jour = date[6:8]
    no_jour = int(no_jour) - 1
    parent_calendar.find_elements(By.CLASS_NAME, 'x-date-active')[no_jour].click()

    # on dé sélectionne
    date_field.find_element(By.XPATH, "./..").click()


def __selenium_recupere_fichier(driver):
    MAX_ATTEMPTS = 5
    attempts = 0

    end = False

    file_list = f"http://{os.environ.get('SELENIUM_SERVICE_NAME')}:4444/session/{driver.session_id}/se/files"
    files = None
    file = ""
    while not end:
        try:
            r = requests.get(file_list)
            files = r.json()["value"]

            # on récupère le dernier fichier
            file = files["names"][-1]
            end = True
        except:
            attempts += 1
            if attempts < MAX_ATTEMPTS:
                sleep(2)
            else:
                # throw an exception
                raise Exception(f"Unable to retrieve file from selenium after {MAX_ATTEMPTS} attempts.", files)

    # On télécharge le fichier
    post_body = {"name": file}
    r = requests.post(file_list, json=post_body)

    # On récupère le contenu du fichier
    file_content_zipped_b64 = r.json()["value"]["contents"]
    file_name = r.json()["value"]["filename"]

    # on décode le contenu (base64 puis unzip)
    file_content_zipped = base64.b64decode(file_content_zipped_b64)
    file_content = zipfile.ZipFile(io.BytesIO(file_content_zipped)).read(file_name)

    # save the file
    folder_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "downloads")
    os.makedirs(folder_path, exist_ok=True)

    filename = os.path.join(folder_path, file_name)
    with open(filename, 'wb') as f:
        f.write(file_content)

    return filename


def __driver_download_ics(datedebut, datefin, driver):
    # On appuie sur le bouton pour générer l'ics
    parent = driver.find_element(By.XPATH, "//span[contains(text(), 'OPTIONS')]").find_element(By.XPATH, "./../..")
    elems = parent.find_elements(By.TAG_NAME, "button")
    elems[1].click()

    # on choppe la popup de génération (role = alertdialog) de l'ics avec attente de 30s
    wait30s = WebDriverWait(driver, 30)
    popup = wait30s.until(lambda driver: driver.find_element(By.XPATH, "//div[@role='alertdialog']"))

    # on sélectionne les dates
    inputs = popup.find_elements(By.TAG_NAME, "input")
    __date_selector(datedebut, inputs[0], driver)
    __date_selector(datefin, inputs[1], driver)

    time.sleep(.5)

    # on regarde si bouton disponible (= ressources à exporter)
    btn_ok = popup.find_element(By.CLASS_NAME, "x-toolbar-ct").find_elements(By.TAG_NAME, "button")[0]

    # On remote le bouton jusqu'a trouver l'élément table
    elem_up = btn_ok.find_element(By.XPATH, "./..")
    while elem_up.tag_name != "table":
        elem_up = elem_up.find_element(By.XPATH, "./..")

    # on vérifie si le container du bouton contient la classe x-item-disabled
    if "x-item-disabled" in elem_up.get_attribute("class"):
        # le bouton est désactivé, il n'y a pas de fichier à télécharger
        return False
    else:
        # le bouton est activé, on télécharge le fichier
        btn_ok.click()
        return True


def get_ics_file(path, start_date, end_date):
    """
    Génère l'url de l'ics de la ressource ressource_path pour la période start_date - end_date
    :param path: Chemin de la ressource dans l'arbre, séparé par des ">"
    :param start_date: date de départ de l'ics (format AAAAMMJJ)
    :param end_date: date de fin de l'ics (format AAAAMMJJ)
    :return: le lien de téléchargement de l'ics
    """

    unrolled_lines = []

    driver = open_remote_browser()

    try:
        driver.get(os.environ['ADE_URL'])

        # wait for page to load
        wait30s = WebDriverWait(driver, 30)
        wait30s.until(lambda driver: driver.find_element(By.CLASS_NAME, "x-tree3-node-joint"))

        # dérouler les ressources
        unroll = ["Trainees", "Rooms"]
        ade_unroll_line(unroll[0], driver)
        ade_unroll_line(unroll[1], driver)

        unrolled_lines.append(unroll[0])
        unrolled_lines.append(unroll[1])


        # sélectionner la ressource
        # path = "IUT Departement Informatique>BUT3 INFORMATIQUE RACDV>UBFBA3TP>B3INFOTPA2"
        nb_unroll = len(path.split(">")) - 1
        for line in path.split(">"):
            # on déroule la ligne si elle est pas déjà déroulée
            if nb_unroll > 0:
                if line not in unrolled_lines:
                    ade_unroll_line(line, driver)
                    unrolled_lines.append(line)
                nb_unroll -= 1
            else:
                # toutes les lignes on été déroulés, on sélectionne la ressource
                __select_line(line, driver)

                # wait while div with class gwt-PopupPanel is present (spinner)
                wait30s.until_not(lambda driver: driver.find_element(By.CLASS_NAME, "gwt-PopupPanel"))

                # la ressource a été sélectionnée + chargée, on génère le lien de l'ics
                if __driver_download_ics(start_date, end_date, driver):
                    # on récupère le fichier
                    sleep(2)
                    downloaded_filepath = __selenium_recupere_fichier(driver)
                else:
                    # pas de fichier à télécharger
                    downloaded_filepath = None

                # on ferme le navigateur
                driver.quit()

                return downloaded_filepath
    except Exception as e:
        print("========================================================")
        print("Erreur lors de la récupération du fichier ics pour la ressource : " + path + " entre les dates " + start_date + " et " + end_date + " :")
        print(traceback.format_exc())
        print("========================================================")
        try:
            res_name = path.split(">")[-1]
            filename = res_name + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".png"
            driver.save_screenshot("/screenshots/" + filename)
            print("Screenshot saved in /screenshots (file : " + filename + ")")
            print("========================================================")
            driver.quit()
        except:
            pass
