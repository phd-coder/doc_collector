import os
import time
import requests
import pandas as pd

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from metadata import getmetadata


URL = "https://www.sci.gov.in/judgements-judgement-date/"
DOWNLOAD_DIR = "supreme_court_judgments"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ---------------------------------------------------------
# 1. Start Chrome
# ---------------------------------------------------------

options = webdriver.ChromeOptions()


options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)


try:

    # -----------------------------------------------------
    # 2. Open Supreme Court judgment-date page
    # -----------------------------------------------------

    driver.get(URL)

    wait = WebDriverWait(driver, 30)

    # Wait for page to load
    time.sleep(3)

    print("Page loaded.")
    print("Please inspect the date fields if the IDs/names differ.")
    

    # -----------------------------------------------------
    # 3. Locate date fields
    # -----------------------------------------------------

    
    date_inputs = driver.find_elements(
        By.CSS_SELECTOR,
        "input"
    )

    print("\nInput fields found:")

    for i, element in enumerate(date_inputs):
        print(
            i,
            "name =", element.get_attribute("name"),
            "id =", element.get_attribute("id"),
            "type =", element.get_attribute("type"),
            "value =", element.get_attribute("value")
        )


    # -----------------------------------------------------
    # MANUALLY enter dates
    # -----------------------------------------------------

    print("\nEnter the date range manually in the browser.")

    input(
        "\nAfter entering the dates AND solving the CAPTCHA, "
        "press ENTER here..."
    )


    # -----------------------------------------------------
    # Click Search
    # -----------------------------------------------------


    buttons = driver.find_elements(
        By.XPATH,
        "//button | //input[@type='submit']"
    )

    print("\nButtons found:")

    for i, button in enumerate(buttons):
        print(
            i,
            button.text,
            button.get_attribute("value"),
            button.get_attribute("type")
        )


 


    input(
        "\nAfter clicking Search and waiting for results, "
        "press ENTER here..."
    )


    # -----------------------------------------------------
    # Get resulting HTML
    # -----------------------------------------------------

    html = driver.page_source

    soup = BeautifulSoup(html, "html.parser")


    # -----------------------------------------------------
    # Find PDF links
    # -----------------------------------------------------
    
    pdf_links = []

    for a in soup.find_all("a", href=True):

        href = a["href"]

        if ".pdf" in href.lower():

            if href.startswith("/"):
                href = "https://www.sci.gov.in" + href

            elif href.startswith("http"):
                pass

            pdf_links.append(href)


    # Remove duplicates
    pdf_links = list(dict.fromkeys(pdf_links))


    print("\nPDF links found:", len(pdf_links))

    for link in pdf_links:
        print(link)


    # -----------------------------------------------------
    # Download PDFs
    # -----------------------------------------------------

    session = requests.Session()

    # Copy cookies from Selenium browser
    for cookie in driver.get_cookies():

        session.cookies.set(
            cookie["name"],
            cookie["value"]
        )


    for i, pdf_url in enumerate(pdf_links, start=1):

        try:

            print(f"\nDownloading {i}/{len(pdf_links)}")

            response = session.get(
                pdf_url,
                timeout=60
            )

            response.raise_for_status()

            filename = os.path.join(
                DOWNLOAD_DIR,
                f"judgment_{i}_{os.path.basename(pdf_url)}"
            )

            with open(filename, "wb") as f:
                f.write(response.content)

            print("Saved:", filename)

        except Exception as e:

            print(
                f"Failed to download {pdf_url}: {e}"
            )
    
    # -----------------------------------------------------
    # Getting the meta data in a csv file
    # -----------------------------------------------------
    # Find all tables
    tables = soup.find_all("table")
    getmetadata(tables, driver)


finally:

    driver.quit()