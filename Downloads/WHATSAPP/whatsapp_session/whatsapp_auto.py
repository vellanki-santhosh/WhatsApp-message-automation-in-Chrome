"""
WhatsApp Message Sender - Interactive CLI
This script sends messages to multiple phone numbers through WhatsApp Web.

Usage:
    1. Run: python whatsapp_auto.py
    2. Paste phone numbers when prompted
    3. Type your message when prompted
    4. Scan QR code on first run (session will be saved)
    5. Messages are sent automatically
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import urllib.parse
import os
import sys
import certifi

# -------------------------------
# Configuration
# -------------------------------
# Use a local folder to persist WhatsApp login session
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_profile")

# -------------------------------
# Helper Functions
# -------------------------------
def validate_phone_number(number):
    """Basic validation for phone numbers."""
    clean = number.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not clean.startswith("+"):
        print(f"⚠ Warning: {number} does not start with '+'. Adding '+' prefix...")
        clean = "+" + clean
    # Remove any non-digit except leading +
    digits_only = "+" + "".join([c for c in clean if c.isdigit()])
    if len(digits_only) < 10:
        return None, f"Invalid number (too short): {number}"
    return digits_only, None


def get_user_input():
    """Get phone numbers and message from user interactively."""
    print("=" * 60)
    print("📱 WhatsApp Bulk Message Sender")
    print("=" * 60)
    print("\nEnter phone numbers (one per line, with country code)")
    print("Example: +919876543210")
    print("Press ENTER twice when done:\n")
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "" and len(lines) > 0:
                break
            if line.strip():
                lines.append(line.strip())
        except EOFError:
            break
    
    if not lines:
        print("❌ No phone numbers entered. Exiting.")
        sys.exit(1)
    
    print(f"\n✅ {len(lines)} number(s) entered.")
    print("\n" + "-" * 60)
    print("Enter your message below. Press ENTER twice when done:\n")
    
    message_lines = []
    while True:
        try:
            line = input()
            if line.strip() == "" and len(message_lines) > 0:
                break
            message_lines.append(line)
        except EOFError:
            break
    
    message = "\n".join(message_lines).strip()
    if not message:
        print("❌ No message entered. Exiting.")
        sys.exit(1)
    
    print(f"\n✅ Message captured ({len(message)} characters).")
    return lines, message


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
    # Uncomment below if you want to run headless (not recommended for QR scan)
    # options.add_argument("--headless=new")

    try:
        # Selenium Manager path (preferred on latest Selenium builds).
        driver = webdriver.Chrome(options=options)
    except Exception:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    driver.maximize_window()
    return driver


def wait_for_whatsapp_load(driver, timeout=60):
    """Wait for WhatsApp Web to load by detecting the chat list or QR code scan completion."""
    print("\n🌐 Opening WhatsApp Web...")
    driver.get("https://web.whatsapp.com")
    
    # Try to detect if already logged in (chat list appears)
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="side"]'))
        )
        print("✅ WhatsApp Web loaded (already logged in).")
        return True
    except TimeoutException:
        # Check if QR code is present
        try:
            qr_code = driver.find_element(By.XPATH, '//canvas[@aria-label="Scan me!"]')
            print("📷 QR Code detected! Please scan with your phone.")
            print("   Waiting for login...")
            
            # Wait for chat list to appear (meaning QR was scanned)
            WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.XPATH, '//div[@id="side"]'))
            )
            print("✅ Login successful! WhatsApp Web ready.")
            return True
        except NoSuchElementException:
            print("⚠ Could not detect QR code or chat list. Please check manually.")
            return False


def send_message_to_number(driver, phone_number, message):
    """Send a message to a single phone number."""
    encoded_message = urllib.parse.quote(message)
    url = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"
    
    print(f"\n📤 Sending to {phone_number}...")
    driver.get(url)
    
    # Wait for chat to load
    time.sleep(5)
    
    message_sent = False
    
    # Method 1: Click send button (for pre-filled message)
    try:
        send_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Send"]'))
        )
        send_button.click()
        message_sent = True
        print(f"   ✅ Sent (via send button)")
    except TimeoutException:
        pass
    
    # Method 2: Type in message box and press Enter
    if not message_sent:
        try:
            message_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
            )
            message_box.click()
            time.sleep(0.5)
            
            # Clear any existing text and type message
            message_box.send_keys(Keys.CONTROL + "a")
            message_box.send_keys(Keys.DELETE)
            time.sleep(0.3)
            
            # Type message line by line
            for i, line in enumerate(message.split('\n')):
                if i > 0:
                    message_box.send_keys(Keys.SHIFT + Keys.ENTER)
                message_box.send_keys(line)
            
            time.sleep(0.5)
            message_box.send_keys(Keys.ENTER)
            message_sent = True
            print(f"   ✅ Sent (via input box)")
        except Exception as e:
            pass
    
    # Method 3: Try alternative send icon
    if not message_sent:
        try:
            send_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
            )
            send_button.click()
            message_sent = True
            print(f"   ✅ Sent (via send icon)")
        except Exception:
            pass
    
    if not message_sent:
        # Check if number is invalid
        try:
            invalid_popup = driver.find_element(By.XPATH, '//div[contains(text(), "phone number shared via url is invalid")]')
            print(f"   ❌ Failed: Invalid phone number")
            return False
        except NoSuchElementException:
            print(f"   ❌ Failed: Could not send message (number may not exist on WhatsApp)")
            return False
    
    # Wait between messages to avoid rate limiting
    time.sleep(3)
    return True


def main():
    """Main function to orchestrate message sending."""
    # Get user input
    raw_numbers, message = get_user_input()
    
    # Validate numbers
    phone_numbers = []
    for num in raw_numbers:
        clean, error = validate_phone_number(num)
        if error:
            print(f"   ⚠ {error}")
        else:
            phone_numbers.append(clean)
    
    if not phone_numbers:
        print("❌ No valid phone numbers found. Exiting.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    print(f"Total recipients: {len(phone_numbers)}")
    print(f"Message preview:\n{'-' * 40}\n{message}\n{'-' * 40}")
    
    confirm = input("\n🚀 Press ENTER to start sending (or type 'cancel' to abort): ").strip().lower()
    if confirm == "cancel":
        print("❌ Cancelled by user.")
        sys.exit(0)
    
    # Setup driver
    driver = setup_driver()
    
    try:
        # Load WhatsApp Web
        if not wait_for_whatsapp_load(driver):
            print("❌ Failed to load WhatsApp Web. Exiting.")
            return
        
        # Send messages
        success_count = 0
        fail_count = 0
        
        for i, phone_number in enumerate(phone_numbers, 1):
            print(f"\n[{i}/{len(phone_numbers)}] Processing {phone_number}...")
            if send_message_to_number(driver, phone_number, message):
                success_count += 1
            else:
                fail_count += 1
        
        # Final summary
        print("\n" + "=" * 60)
        print("📊 RESULTS")
        print("=" * 60)
        print(f"✅ Successfully sent: {success_count}")
        print(f"❌ Failed: {fail_count}")
        print(f"📱 Total: {len(phone_numbers)}")
        print("=" * 60)
        
        input("\nPress ENTER to close the browser...")
        
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
    finally:
        driver.quit()
        print("👋 Browser closed.")


if __name__ == "__main__":
    main()

