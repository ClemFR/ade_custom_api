from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from selenium_util import open_remote_browser, ade_unroll_line
import os

from datetime import datetime


def __compter_espaces_debut(texte):
    for c in texte:
        if c != ' ':
            return texte.index(c)


def scrap_liste_ressource():
    driver = open_remote_browser()

    ade_url = os.environ["ADE_URL"]
    driver.get(ade_url)

    # On se connecte
    username = driver.find_element(By.NAME, 'login')
    username.send_keys(os.environ["ADE_USERNAME"])

    password = driver.find_element(By.NAME, 'password')
    password.send_keys(os.environ["ADE_PASSWORD"])

    driver.find_element(By.CLASS_NAME, 'footer').find_element(By.TAG_NAME, 'input').click()

    # Sélection de l'année
    select = driver.find_element(By.NAME, 'projectId')
    select = Select(select)
    select.select_by_value(os.environ["ADE_ANNEE_ID"])

    driver.find_element(By.CLASS_NAME, 'footer').find_element(By.TAG_NAME, 'input').click()

    # On va sur l'arbre
    driver.get(os.environ["ADE_TREE_URL"])

    # On déroule les lignes
    # Recherche des balises images ayant comme fin de lien "/jsp/img/plus.gif"
    # On y clique dessus
    end = False

    while not end:
        try:
            img = driver.find_element(By.XPATH, "//img[contains(@src, '/jsp/img/plus')]")
            img.click()
        except:
            end = True

    lines = driver.find_elements(By.CLASS_NAME, 'treeline')

    # On veut compter le nombre d'espace avant la balise <a> pour savoir le niveau de la ligne
    # On enregistre les lignes dans un dictionnaire
    # key: nom de la ressource
    # value: niveau de la ressource

    ressources_to_level = {}
    ressource_order = []
    for line in lines:
        nb_space = __compter_espaces_debut(line.text)
        ressources_to_level[line.text.strip()] = nb_space
        ressource_order.append(line.text.strip())

    driver.quit()

    groupes_tp = []
    for ressource in ressource_order:
        if "CM" in ressource or "TD" in ressource:
            continue
        else:
            if ressources_to_level[ressource] == 15:
                groupes_tp.append(ressource)

    # Pour chaque groupe de tp, on va chercher l'emplacement dans le dictionnaire, et on remonte le dictionnaire
    # jusqu'à trouver la ressource "Trainees"

    format = "%Y-%m-%d_%H:%M:%S"
    current_date = datetime.now().strftime(format)

    f = open("ressources" + current_date + ".txt", "w")

    for groupe_tp in groupes_tp:
        path = groupe_tp

        # on cherche la position de la ressource dans la liste
        position = ressource_order.index(groupe_tp)

        # On regarde son index dans l'arbre
        current_tree_index = ressources_to_level[groupe_tp]

        while ressource_order[position] != "Trainees":
            # On remonte l'arbre jusqu'a trouver une ressource d'un index inférieur
            found = False
            while not found:
                position -= 1
                if ressources_to_level[ressource_order[position]] < current_tree_index:
                    found = True

            path = ressource_order[position] + ">" + path

            # On met à jour l'index
            current_tree_index = ressources_to_level[ressource_order[position]]

        print(path)
        f.write(path + "\n")

    f.close()


if __name__ == '__main__':
    os.environ["ADE_URL"] = "https://ade-production.ut-capitole.fr/jsp/standard/index.jsp"
    os.environ["SELENIUM_HOST"] = "172.16.238.10"
    os.environ["SELENIUM_PORT"] = "4444"
    os.environ["ADE_USERNAME"] = "anonymousiut"
    os.environ["ADE_PASSWORD"] = ""
    os.environ["ADE_ANNEE_ID"] = "32"
    os.environ["ADE_TREE_URL"] = "https://ade-production.ut-capitole.fr/jsp/standard/gui/tree.jsp?noLoad=true"

    scrap_liste_ressource()
