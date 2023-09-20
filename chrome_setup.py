import chromedriver_autoinstaller as cdai
import selenium.webdriver as webdriver
from selenium_stealth import stealth


def check_driver():
    print("Checking for chrome driver...")
    cdai.install()
    return cdai.get_chrome_version()


def setup_browser():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)

    stealth(driver,
            languages=["en-EN", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    return driver
