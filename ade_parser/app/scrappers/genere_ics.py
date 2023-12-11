from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import requests
import os
import zipfile
import base64
import io
from scrappers.selenium_util import open_remote_browser, ade_unroll_line


def __select_line(line_text, driver):
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
        "02": (0, 1),
        "03": (1, 0),
        "04": (1, 1),
        "05": (2, 0),
        "06": (2, 1),
        "07": (3, 0),
        "08": (3, 1),
        "09": (4, 0),
        "10": (4, 1),
        "11": (5, 0),
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
    file_list = f"http://{os.environ['SELENIUM_HOST']}:{os.environ['SELENIUM_PORT']}/session/{driver.session_id}/se/files"
    r = requests.get(file_list)
    files = r.json()["value"]

    # on récupère le dernier fichier
    file = files["names"][-1]

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

    # on clique sur le bouton OK pour télécharger le fichier
    popup.find_element(By.CLASS_NAME, "x-toolbar-ct").find_elements(By.TAG_NAME, "button")[0].click()

    # on attend que le fichier soit téléchargé
    sleep(2)


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

    # navigate to url
    # driver.get(
    #     'https://ade-production.ut-capitole.fr/direct/index.jsp?showTree=true&showPianoDays=true&showPianoWeeks=true'
    #     '&days=0,1,2,3,4,&displayConfName=Web&login=anonymousiut&projectId=32')
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
            __driver_download_ics(start_date, end_date, driver)

            # on récupère le fichier
            downloaded_filepath = __selenium_recupere_fichier(driver)

            # on ferme le navigateur
            driver.quit()

            return downloaded_filepath

if __name__ == '__main__':
    os.environ["SELENIUM_HOST"] = "172.16.238.10"
    os.environ["SELENIUM_PORT"] = "4444"
    os.environ["ADE_URL"] = "https://ade-production.ut-capitole.fr/direct/index.jsp?showTree=true&showPianoDays=true&showPianoWeeks=true&days=0,1,2,3,4,&displayConfName=Web&login=anonymousiut&projectId=32"

    print(get_ics_file("IUT Departement Informatique>BUT3 INFORMATIQUE RACDV>UBFBA3TP>B3INFOTPA2", "20231201", "20231231"))