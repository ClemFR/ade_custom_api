from selenium import webdriver
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


def open_remote_browser():
    # options = webdriver.ChromeOptions()
    # options.add_argument("--disable-gpu")
    # options.add_argument("--no-sandbox")
    # options.add_experimental_option("prefs",{
    #     "download.default_directory": "/home/seluser/Downloads/",
    #     "download.prompt_for_download": False,
    #     "download.directory_upgrade": True
    # })

    # options.add_experimental_option("localState", {
    #     "browser.enabled_labs_experiments": [
    #         "download-bubble@2",
    #         "download-bubble-v2@2"
    #     ]
    # })

    # options.add_argument("disable-features=DownloadBubble,DownloadBubbleV2")

    options = webdriver.FirefoxOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.set_capability("se:downloadsEnabled", True)

    profile = webdriver.FirefoxProfile()

    profile.set_preference("browser.download.dir", "/home/seluser/Downloads/")
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
                          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.helperApps.neverAsk.openFile",
                          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    profile.set_preference("browser.download.manager.useWindow", False)
    profile.set_preference("browser.download.manager.focusWhenStarting", False)
    profile.set_preference("browser.download.manager.showAlertOnComplete", False)
    profile.set_preference("browser.download.manager.closeWhenDone", True)

    remote_address = f"http://{os.environ['SELENIUM_HOST']}:{os.environ['SELENIUM_PORT']}"

    driver = webdriver.Remote(command_executor=remote_address, options=options)
    return driver


def ade_unroll_line(line_text, driver):
    wait30s = WebDriverWait(driver, 30)
    elem_nb = len(driver.find_elements(By.CLASS_NAME, 'x-tree3-node-joint'))

    ligne = driver.find_element(By.XPATH, f"//span[contains(text(), '{line_text}')]")
    up = ligne.find_element(By.XPATH, "./..")
    up.find_element(By.CLASS_NAME, 'x-tree3-node-joint').click()

    # wait while the number of x-tree3-node-joint is the same
    wait30s.until(lambda driver: len(driver.find_elements(By.CLASS_NAME, 'x-tree3-node-joint')) != elem_nb)