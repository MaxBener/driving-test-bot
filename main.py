import time
import json
import logging
import telegram
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Загрузка конфигурации
with open("config.json") as f:
    config = json.load(f)

TELEGRAM_BOT_TOKEN = config["telegram_token"]
CHAT_ID = config["chat_id"]
BOOKING_ID = config["booking_id"]
SURNAME = config["surname"]
LOCATION_NAME = config["location"]
CHECK_INTERVAL = config["check_interval_minutes"] * 60
DATE_CUTOFF = config["date_cutoff"]  # "2025-05-15"

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
logging.basicConfig(level=logging.INFO)

def notify_user(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

def check_for_earlier_date():
    logging.info("Проверка доступных дат...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get("https://www.myrta.com/wps/portal/extvp/myrta/licence/tbs/tbs-change/")
        time.sleep(5)
        
        driver.find_element(By.ID, "booking-reference").send_keys(BOOKING_ID)
        driver.find_element(By.ID, "surname").send_keys(SURNAME)
        driver.find_element(By.ID, "next-button").click()
        
        time.sleep(5)
        
        # Проверка Castle Hill и сравнение дат (упрощено)
        page_text = driver.page_source
        if LOCATION_NAME.lower() in page_text.lower() and "15 May 2025" not in page_text:
notify_user(f'‼️ Обнаружена более ранняя дата в {LOCATION_NAME}!\nПроверь на сайте вручную:\nhttps://www.myrta.com/...')
        else:
            logging.info("Более ранних дат нет.")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    while True:
        check_for_earlier_date()
        time.sleep(CHECK_INTERVAL)
