#lib selenium
from selenium import webdriver
#option facultatives pour chrome
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

url_trustpilot="https://fr.trustpilot.com/"
def connexion(url):
# facultatif juste pour regler afichage en pleine ecran et desactiver les notifications
    chrome_options= Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
# garder la page  ouverte pour la demo
    

    # initialiser la connexion
    # lance chrome avec undetected_chromedriver
    driver = uc.Chrome(options=chrome_options)
    # ouvre url
    driver.get(url)
    return driver



   
# headless mode github action CI/CD

# def initialize_connection():
#     chrome_options = Options()

#     user_data_dir3 = "-window-size=1920,1080"
#     chrome_options.add_argument("--headless")                  # Chrome in headless mode
#     chrome_options.add_argument("--no-sandbox")                # Removes sandbox (useful in CI/CD)
#     chrome_options.add_argument("--disable-notifications")     # Disable web notifications
#     chrome_options.add_argument("--disable-infobars")          # Remove "Chrome is being controlled…" banner
#     chrome_options.add_argument(user_data_dir3)
#     driver = webdriver.Chrome(options=chrome_options)
#     driver.get(url)
#     return driver
