from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.window import WindowTypes
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver as webdriver

import ade_utils

ade_username = "anonymousiut"
ade_password = ""
ade_year_id = "32"


def auth(driver: webdriver.Chrome):
    # Login
    driver.get("https://ade-production.ut-capitole.fr/jsp/standard/index.jsp")
    form_login = driver.find_element(By.CLASS_NAME, "content")
    form_login.find_elements(By.TAG_NAME, "label")[0].find_element(By.TAG_NAME, "input").send_keys(ade_username)
    form_login.find_elements(By.TAG_NAME, "label")[1].find_element(By.TAG_NAME, "input").send_keys(ade_password)
    driver.find_element(By.CLASS_NAME, "footer").find_element(By.TAG_NAME, "input").click()

    # Sélection de l'année a scrapper
    sel = Select(driver.find_element(By.NAME, "projectId"))
    sel.select_by_value(ade_year_id)
    driver.find_element(By.CLASS_NAME, "footer").find_element(By.TAG_NAME, "input").click()

    # Ouverture des premières catégories pour activer la génération des edt
    categs = ("trainee", "instructor", "room",)
    for categ in categs:
        driver.get("https://ade-production.ut-capitole.fr/jsp/standard/gui/tree.jsp?category=" + categ)
    driver.get("https://ade-production.ut-capitole.fr/jsp/standard/gui/interface.jsp")


def switch_week_date(driver: webdriver.Chrome, date):
    """
    Change la semaine séletionnée sur l'interface de l'ade
    :param date: la date au format AAAAMMJJ
    """
    driver.switch_to.new_window(WindowTypes.TAB)
    # reset des semaines sélectionnées
    driver.get("https://ade-production.ut-capitole.fr/jsp/custom/modules/plannings/bounds.jsp?reset=true&week=-1")
    # sélection de la semaine
    sem = ade_utils.calculate_week(date)
    driver.get("https://ade-production.ut-capitole.fr/jsp/custom/modules/plannings/bounds.jsp?week=" + str(sem))

    driver.close()
    driver.switch_to.window(driver.window_handles[0])



def switch_id(driver: webdriver.Chrome, id):
    """
    Change la ressource sélectionnée sur l'interface de l'ade
    :param id: l'identifiant de la ressource
    """
    driver.switch_to.new_window(WindowTypes.TAB)
    # clear de la ressource sélectionnée
    driver.get("https://ade-production.ut-capitole.fr/jsp/standard/gui/tree.jsp?selectId=-1&reset=true")
    # sélection de la ressource
    driver.get("https://ade-production.ut-capitole.fr/jsp/standard/gui/tree.jsp?selectId=" + str(id))

    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def get_edt_image(driver: webdriver.chrome, width, height):
    """
    Renvoie l'image de l'edt de la ressource sélectionnée à la semaine sélectionnée
    :return: l'image de l'edt
    """
    driver.switch_to.new_window(WindowTypes.TAB)
    driver.get(f"https://ade-production.ut-capitole.fr/jsp/custom/modules/plannings/bounds.jsp?width={width}&height={height}")

    try:
        img = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "img"))).get_attribute("src")
        img = img.replace("ade-production.ut-capitole.frjsp", "ade-production.ut-capitole.fr/jsp")
    except:
        print("Timeout")
        img = None

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return img
