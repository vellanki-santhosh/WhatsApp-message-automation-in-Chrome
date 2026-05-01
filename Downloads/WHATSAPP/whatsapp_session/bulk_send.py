"""
WhatsApp Bulk Sender - File Based
Reads phone numbers from 'numbers.txt' and message from 'message.txt'

Usage:
    1. Add phone numbers to numbers.txt (one per line)
    2. Add your message to message.txt
    3. Run: python bulk_send.py
    4. Scan QR code on first run (session is saved)
"""

import os
import sys

# Fix certificate issue before any other imports
import certifi
cert_path = certifi.where()
for var_name in ("REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE", "SSL_CERT_FILE"):
    var_value = os.environ.get(var_name)
    if var_value and not os.path.exists(var_value):
        os.environ[var_name] = cert_path
os.environ.setdefault("REQUESTS_CA_BUNDLE", cert_path)
os.environ.setdefault("SSL_CERT_FILE", cert_path)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import urllib.parse

# -------------------------------
# Configuration
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.path.join(BASE_DIR, "chrome_profile")
NUMBERS_FILE = os.path.join(BASE_DIR, "numbers.txt")
MESSAGE_FILE = os.path.join(BASE_DIR, "message.txt")


def validate_phone_number(number):
    """Basic validation for phone numbers."""
    clean = number.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not clean.startswith("+"):
        clean = "+" + clean
    digits_only = "+" + "".join([c for c in clean if c.isdigit()])
    if len(digits_only) < 10:
        return None, f"Invalid number (too short): {number}"
    return digits_only, None


def read_numbers(filepath):
    """Read phone numbers from file."""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        print("   Please create this file and add one phone number per line.")
        sys.exit(1)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith('#')]
    
    valid_numbers = []
    for line in lines:
        clean, error = validate_phone_number(line)
        if error:
            print(f"   ⚠ {error}")
        else:
            valid_numbers.append(clean)
    
    return valid_numbers


def read_message(filepath):
    """Read message from file."""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        print("   Please create this file with your message content.")
        sys.exit(1)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    if not content:
        print("❌ Message file is empty.")
        sys.exit(1)
    
    return content


def setup_driver():
    """Setup and return Chrome WebDriver with session persistence."""
    cert_path = certifi.where()
    for var_name in ("REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE", "SSL_CERT_FILE"):
        var_value = os.environ.get(var_name)
        if var_value and not os.path.exists(var_value):
            os.environ[var_name] = cert_path

    os.environ.setdefault("REQUESTS_CA_BUNDLE", cert_path)
    os.environ.setdefault("SSL_CERT_FILE", cert_path)

    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        # Selenium Manager path (preferred on latest Selenium builds).
        driver = webdriver.Chrome(options=options)
    except Exception:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    driver.maximize_window()
    return driver


def wait_for_whatsapp_load(driver, timeout=60):
    """Wait for WhatsApp Web to load."""
    print("\n🌐 Opening WhatsApp Web...")
    driver.get("https://web.whatsapp.com")
    
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="side"]'))
        )
        print("✅ WhatsApp Web loaded (already logged in).")
        return True
    except TimeoutException:
        try:
            qr_code = driver.find_element(By.XPATH, '//canvas[@aria-label="Scan me!"]')
            print("📷 QR Code detected! Please scan with your phone.")
            print("   Waiting for login...")
            WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.XPATH, '//div[@id="side"]'))
            )
            print("✅ Login successful! WhatsApp Web ready.")
            return True
        except NoSuchElementException:
            print("⚠ Could not detect QR code or chat list.")
            return False


def send_message_to_number(driver, phone_number, message):
    """Send a message to a single phone number."""
    encoded_message = urllib.parse.quote(message)
    url = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"
    
    print(f"\n📤 Sending to {phone_number}...")
    driver.get(url)
    time.sleep(5)
    
    message_sent = False
    
    # Method 1: Click send button (retry once for stale references)
    for _ in range(2):
        try:
            send_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Send"]'))
            )
            send_button.click()
            message_sent = True
            print(f"   ✅ Sent")
            break
        except (TimeoutException, StaleElementReferenceException):
            time.sleep(0.6)
    
    # Method 2: Type in message box and press Enter
    if not message_sent:
        try:
            message_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
            )
            message_box.click()
            time.sleep(0.5)
            message_box.send_keys(Keys.CONTROL + "a")
            message_box.send_keys(Keys.DELETE)
            time.sleep(0.3)
            
            for i, line in enumerate(message.split('\n')):
                if i > 0:
                    message_box.send_keys(Keys.SHIFT + Keys.ENTER)
                message_box.send_keys(line)
            
            time.sleep(0.5)
            message_box.send_keys(Keys.ENTER)
            message_sent = True
            print(f"   ✅ Sent")
        except Exception:
            pass
    
    # Method 3: Try alternative send icon
    if not message_sent:
        try:
            send_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
            )
            send_button.click()
            message_sent = True
            print(f"   ✅ Sent")
        except (TimeoutException, StaleElementReferenceException, NoSuchElementException):
            pass
    
    if not message_sent:
        try:
            invalid_popup = driver.find_element(By.XPATH, '//div[contains(text(), "phone number shared via url is invalid")]')
            print(f"   ❌ Invalid phone number")
            return False
        except NoSuchElementException:
            print(f"   ❌ Failed (number may not exist on WhatsApp)")
            return False
    
    time.sleep(3)
    return True


def main():
    """Main function."""
    print("=" * 60)
    print("📱 WhatsApp Bulk Sender (File-Based)")
    print("=" * 60)
    
    # Read inputs from files
    print(f"\n📂 Reading numbers from: {NUMBERS_FILE}")
    phone_numbers = read_numbers(NUMBERS_FILE)
    print(f"   ✅ {len(phone_numbers)} valid number(s) found.")
    
    print(f"\n📂 Reading message from: {MESSAGE_FILE}")
    message = read_message(MESSAGE_FILE)
    print(f"   ✅ Message loaded ({len(message)} characters).")
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    print(f"Total recipients: {len(phone_numbers)}")
    print(f"Message preview:\n{'-' * 40}\n{message}\n{'-' * 40}")
    
    confirm = input("\n🚀 Press ENTER to start sending (or type 'cancel' to abort): ").strip().lower()
    if confirm == "cancel":
        print("❌ Cancelled by user.")
        sys.exit(0)
    
    # Setup and send
    driver = setup_driver()
    
    try:
        if not wait_for_whatsapp_load(driver):
            print("❌ Failed to load WhatsApp Web.")
            return
        
        success_count = 0
        fail_count = 0
        
        for i, phone_number in enumerate(phone_numbers, 1):
            print(f"\n[{i}/{len(phone_numbers)}] Processing {phone_number}...")
            try:
                if send_message_to_number(driver, phone_number, message):
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                fail_count += 1
                print(f"   ❌ Failed due to runtime error: {e}")
        
        print("\n" + "=" * 60)
        print("📊 RESULTS")
        print("=" * 60)
        print(f"✅ Successfully sent: {success_count}")
        print(f"❌ Failed: {fail_count}")
        print(f"📱 Total: {len(phone_numbers)}")
        print("=" * 60)
        
        try:
            input("\nPress ENTER to close the browser...")
        except KeyboardInterrupt:
            print("\nℹ Exiting without waiting for ENTER.")
        
    except KeyboardInterrupt:
        print("\nℹ Run interrupted by user.")
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
    finally:
        driver.quit()
        print("👋 Browser closed.")


if __name__ == "__main__":
    main()

