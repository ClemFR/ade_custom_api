import selenium.webdriver as webdriver
from selenium_stealth import stealth
import settings


def setup_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    if settings.env.get("CHROME_HEADLESS") == "true":
        options.add_argument("--headless")

    if settings.env.get("CHROME_BINARY") is not None and settings.env.get("CHROME_BINARY") != "":
        options.binary_location = settings.env["CHROME_BINARY"]

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
