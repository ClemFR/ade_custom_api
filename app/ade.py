from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.window import WindowTypes
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver as webdriver
import os

import ade_utils


def get_ade_url() -> str:
    ade_url = os.environ.get('ADE_JSP_URL')
    ade_url = ade_url[:-1] if ade_url[-1] == "/" else ade_url
    return ade_url


def auth(driver: webdriver.Chrome):
    # Login
    ade_username = os.environ.get('ADE_LOGIN')
    ade_password = os.environ.get('ADE_PASSWORD')
    ade_year_id = os.environ.get('ADE_YEAR_ID')
    ade_url = get_ade_url()

    driver.get(f"{ade_url}/standard/index.jsp")
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
        driver.get(f"{ade_url}/standard/gui/tree.jsp?category=" + categ)
    driver.get(f"{ade_url}/standard/gui/interface.jsp")


def test_driver_cnx(driver: webdriver.Chrome) -> bool:
    """
    Teste si le token de connexion est toujours valide
    Si déconnecté, reconnecte le driver
    """
    ade_url = get_ade_url()
    driver.get(f"{ade_url}/standard/gui/interface.jsp")
    if driver.current_url != f"{ade_url}/standard/gui/interface.jsp":
        return False
    return True


def switch_week_date(driver: webdriver.Chrome, date):
    """
    Change la semaine séletionnée sur l'interface de l'ade
    :param date: la date au format AAAAMMJJ
    """
    ade_url = get_ade_url()
    driver.switch_to.new_window(WindowTypes.TAB)
    # reset des semaines sélectionnées
    driver.get(f"{ade_url}/custom/modules/plannings/bounds.jsp?reset=true&week=-1")
    # sélection de la semaine
    sem = ade_utils.calculate_week(date)
    driver.get(f"{ade_url}/custom/modules/plannings/bounds.jsp?week=" + str(sem))

    driver.close()
    driver.switch_to.window(driver.window_handles[0])



def switch_id(driver: webdriver.Chrome, id):
    """
    Change la ressource sélectionnée sur l'interface de l'ade
    :param id: l'identifiant de la ressource
    """
    ade_url = get_ade_url()
    driver.switch_to.new_window(WindowTypes.TAB)
    # clear de la ressource sélectionnée
    driver.get(f"{ade_url}/standard/gui/tree.jsp?selectId=-1&reset=true")
    # sélection de la ressource
    driver.get(f"{ade_url}/standard/gui/tree.jsp?selectId=" + str(id))

    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def get_edt_image(driver: webdriver.chrome, width, height):
    """
    Renvoie l'image de l'edt de la ressource sélectionnée à la semaine sélectionnée
    :return: l'image de l'edt
    """
    ade_url = get_ade_url()
    driver.switch_to.new_window(WindowTypes.TAB)
    driver.get(f"{ade_url}/custom/modules/plannings/bounds.jsp?width={width}&height={height}")

    try:
        img = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "img"))).get_attribute("src")
        img = img.replace("ade-production.ut-capitole.frjsp", "ade-production.ut-capitole.fr/jsp")
    except:
        print("Timeout")
        img = None

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return img


def switch_selected_days(driver: webdriver.chrome, days: list[int, ...] | tuple[int, ...]):
    """
    Change les jours sélectionnés sur l'interface de l'ade
    :param days: les jours à sélectionner
    """
    ade_url = get_ade_url()
    driver.switch_to.new_window(WindowTypes.TAB)
    # reset des jours sélectionnés
    driver.get(f"{ade_url}/custom/modules/plannings/pianoDays.jsp?day=-1&reset=true&forceLoad=false")
    # sélection des jours
    for day in days:
        driver.get(f"{ade_url}/custom/modules/plannings/pianoDays.jsp?day=" + str(day))

    driver.close()
    driver.switch_to.window(driver.window_handles[0])