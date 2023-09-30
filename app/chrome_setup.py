import selenium.webdriver as webdriver
import os
import requests
from time import sleep


def setup_browser():
    wait_grid_started()

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    remote_address = f"http://{os.environ.get('SELENIUM_HOST')}:{os.environ.get('SELENIUM_PORT')}"

    driver = webdriver.Remote(command_executor=remote_address, options=options)
    return driver


def wait_grid_started():
    url = f"http://{os.environ.get('SELENIUM_HOST')}:{os.environ.get('SELENIUM_PORT')}/status"
    print("Checking selenium grid status...")
    while True:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                content = r.json()
                if content['value']['ready']:
                    break
            sleep(1)
        except:
            pass
        sleep(1)
    print("Selenium grid ready !")
