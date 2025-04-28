import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os

# Setup Chrome dengan profil khusus (bukan profil utama)
chrome_options = Options()
chrome_options.add_argument(r"user-data-dir=C:\WhatsAppSeleniumProfile")
# chrome_options.add_argument("profile-directory=Profile 1")  # Jika perlu

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

load_dotenv()

API_URL = os.getenv('API_URL')

def send_attendance(rfid_uid, status="masuk"):
    payload = {
        "rfid_uid": rfid_uid,
        "status": status
    }

    # Nomor WhatsApp dan pesan
    phone_number = "628975050520"  # TANPA +, tapi pakai kode negara
    message = "Halo! Ini pesan otomatis pakai Selenium"

    # Akses halaman chat langsung
    driver.get(f"https://wa.me/{phone_number}")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//a[@id="action-button"]')))

    # Klik tombol "Continue to Chat" (mungkin muncul kalau belum pernah chat)
    try:
        continue_btn = driver.find_element(By.XPATH, '//a[@id="action-button"]')
        continue_btn.click()
        time.sleep(5)
    except Exception as e:
        print("Tidak perlu klik tombol lanjut, langsung masuk WhatsApp Web.", e)

    # Tunggu dan redirect ke WhatsApp Web
    driver.get(f"https://web.whatsapp.com/send?phone={phone_number}&text={message}")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')))

    # Tekan ENTER untuk kirim pesan
    try:
        input_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
        input_box.send_keys(Keys.ENTER)
        print("✅ Pesan berhasil dikirim!")
    except Exception as e:
        print("❌ Gagal kirim pesan:", e)

    time.sleep(5)
    driver.quit()

# Contoh penggunaan
