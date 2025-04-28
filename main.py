import time
import requests
import serial
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

# Setup koneksi serial ke ESP32
API_URL = "http://192.168.0.104:8000/api/attendance"
SERIAL_PORT = 'COM3'
BAUDRATE = 115200
TIMEOUT = 5

# Fungsi buat setup Chrome baru
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument(r"user-data-dir=C:\WhatsAppSeleniumProfile")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://web.whatsapp.com")
    arduino.write(b"READY\n")



    print("🌐 Browser Chrome dibuka ulang...")
    return driver

# Buka koneksi serial sekali saja
arduino = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=TIMEOUT)

# Inisialisasi driver di awal
driver = create_driver()


def is_driver_alive(driver):
    try:
        driver.title
        return True
    except:
        return False

def wait_for_rfid_scan_serial(arduino):
    print(f"📡 Menunggu kartu RFID dari ESP32 di port {arduino.port}...")
    while True:
        if arduino.in_waiting:
            line = arduino.readline().decode('utf-8').strip()
            if "UID Tag" in line:
                uid = line.split(":")[-1].strip().replace(" ", "").upper()
                print(f"✅ UID RFID terbaca: {uid}")
                return uid

def send_whatsapp_message(phone_number, message):
    global driver  # 🔥 penting supaya driver global bisa diubah

    try:
        # Cek kalau browser mati, buka ulang
        if not is_driver_alive(driver):
            print("⚠️ Driver mati! Membuka browser baru...")
            driver.quit()
            driver = create_driver()

        driver.get(f"https://web.whatsapp.com/send?phone={phone_number}&text={message}")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')))
        input_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
        input_box.send_keys(Keys.ENTER)
        print("✅ Pesan berhasil dikirim!")
        return True

    except Exception as e:
        print("❌ Gagal kirim pesan:", e)

        # Kalau error parah, misal no such window, buka driver baru
        try:
            driver.quit()
        except:
            pass
        driver = create_driver()
        return False

def main():
    global driver

    current_time = time.strftime("%H:%M:%S", time.localtime())  # Format jam:menit:detik
    arduino.write(f"{current_time}\n".encode())  # Kirim waktu ke Arduino
    
    while True:
        uid = wait_for_rfid_scan_serial(arduino)
        try:
            now = datetime.now()
            formatted_time = now.strftime("%d %B %Y, %H:%M WIB")

            arduino.write(b"SENDING_WHATSAPP\n")  # 🔴 Kasih sinyal ke ESP32
            response = requests.post(API_URL, data={'rfid_uid': uid})
            data = response.json()

            print(f"📋 Server: {data['message']}")

           
            lcd_message = data['message']
            if data.get('nama'):
                lcd_message += f" ({data['nama']})"
            arduino.write(f"{''}\n".encode())  
            arduino.write(f"{lcd_message}\n".encode())  

            if data['status'] == "success" or data['status'] == "info":
                success = send_whatsapp_message(data["phone"], 'nama ' f"{data['nama']}', mapel:' {data['mapel']} ', keterangan:' {data['message']} ', guru:' {data['guru']} ({formatted_time})")
                if success:
                    arduino.write(b"DONE\n")
                else:
                    arduino.write(b"FAILED\n")
                    print(f"⚠️ {data['message']}")

            elif data['status'] == "error":
                print(f"⚠️ {data['message']}")
                arduino.write(b"FAILED\n")

            else:
                print("⚠️ Status tidak dikenal dari server.")
                arduino.write(b"FAILED\n")

            arduino.flush()
            time.sleep(0.1)

        except Exception as e:
            print("❌ Error:", e)
            arduino.write(b"READY\n")
            arduino.flush()
            time.sleep(0.1)

if __name__ == "__main__":
    main()
