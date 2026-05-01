import streamlit as st
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
import tempfile
import certifi

# -------------------------------
# Configuration
# -------------------------------
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_profile")

# -------------------------------
# WhatsApp Sending Function
# -------------------------------
def send_whatsapp_message(phone_numbers, message, progress_bar, status_text):
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
    
    try:
        # Open WhatsApp Web
        status_text.text("🌐 Opening WhatsApp Web...")
        driver.get("https://web.whatsapp.com")
        
        # Wait for WhatsApp to load
        try:
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//div[@id="side"]'))
            )
            status_text.text("✅ WhatsApp Web loaded!")
        except TimeoutException:
            try:
                qr_code = driver.find_element(By.XPATH, '//canvas[@aria-label="Scan me!"]')
                status_text.text("📷 QR Code detected! Please scan with your phone. Waiting for login...")
                WebDriverWait(driver, 120).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@id="side"]'))
                )
                status_text.text("✅ Login successful!")
            except NoSuchElementException:
                status_text.error("⚠ Could not load WhatsApp Web properly.")
                return
        
        success_count = 0
        fail_count = 0
        
        for i, phone_number in enumerate(phone_numbers):
            progress = (i + 1) / len(phone_numbers)
            progress_bar.progress(progress)
            status_text.text(f"[{i+1}/{len(phone_numbers)}] Sending to {phone_number}...")
            
            clean_number = phone_number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            if not clean_number.startswith("+"):
                clean_number = "+" + clean_number
            clean_number = "+" + "".join([c for c in clean_number if c.isdigit()])
            
            encoded_message = urllib.parse.quote(message)
            url = f"https://web.whatsapp.com/send?phone={clean_number}&text={encoded_message}"
            driver.get(url)
            time.sleep(5)
            
            message_sent = False
            
            # Method 1: Click send button
            try:
                send_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Send"]'))
                )
                send_button.click()
                message_sent = True
            except TimeoutException:
                pass
            
            # Method 2: Type in message box
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
                    
                    for j, line in enumerate(message.split('\n')):
                        if j > 0:
                            message_box.send_keys(Keys.SHIFT + Keys.ENTER)
                        message_box.send_keys(line)
                    
                    time.sleep(0.5)
                    message_box.send_keys(Keys.ENTER)
                    message_sent = True
                except Exception:
                    pass
            
            # Method 3: Alternative send icon
            if not message_sent:
                try:
                    send_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
                    )
                    send_button.click()
                    message_sent = True
                except Exception:
                    pass
            
            if message_sent:
                success_count += 1
                st.success(f"✅ Sent to {phone_number}")
            else:
                fail_count += 1
                st.error(f"❌ Failed to send to {phone_number}")
            
            time.sleep(3)
        
        progress_bar.empty()
        status_text.empty()
        st.success(f"🎉 Done! Sent: {success_count}, Failed: {fail_count}")
        
    except Exception as e:
        st.error(f"💥 Error: {str(e)}")
    finally:
        driver.quit()


# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="WhatsApp Bulk Sender", layout="centered")

st.title("📲 WhatsApp Bulk Message Sender")
st.markdown("Send WhatsApp messages using Selenium + Streamlit")

# Input method selection
input_method = st.radio("Choose input method:", ["Manual Entry", "Upload File"])

phone_numbers = []

if input_method == "Manual Entry":
    numbers_input = st.text_area(
        "Enter Phone Numbers (one per line with country code)",
        height=150,
        placeholder="+919876543210\n+918888888888"
    )
    if numbers_input.strip():
        phone_numbers = [num.strip() for num in numbers_input.splitlines() if num.strip()]

else:
    uploaded_file = st.file_uploader("Upload numbers file (.txt)", type=["txt"])
    if uploaded_file is not None:
        content = uploaded_file.read().decode("utf-8")
        phone_numbers = [num.strip() for num in content.splitlines() if num.strip() and not num.strip().startswith('#')]
        st.info(f"📂 Loaded {len(phone_numbers)} numbers from file.")

# Message input
message = st.text_area(
    "Enter Your Message",
    height=200,
    placeholder="Type your message here..."
)

# Validation and preview
if phone_numbers and message.strip():
    st.subheader("📋 Preview")
    st.write(f"**Recipients:** {len(phone_numbers)} numbers")
    st.write(f"**Message:**")
    st.info(message)

# Send button
if st.button("🚀 Send Messages"):
    if not phone_numbers:
        st.warning("⚠ Please enter or upload phone numbers.")
    elif message.strip() == "":
        st.warning("⚠ Please enter a message.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        send_whatsapp_message(phone_numbers, message, progress_bar, status_text)

