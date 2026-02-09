"""
WhatsApp Message Sender via Chrome
This script sends messages to specific numbers through WhatsApp Web
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import urllib.parse

def send_whatsapp_message(phone_numbers, message):
    """
    Send WhatsApp messages to multiple phone numbers
    
    Args:
        phone_numbers: List of phone numbers (with country code, e.g., '+919876543210')
        message: The message text to send
    """
    
    # Setup Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=/tmp/whatsapp_chrome")  # Keep session logged in
    driver = webdriver.Chrome(options=options)
    
    try:
        # Open WhatsApp Web
        driver.get("https://web.whatsapp.com")
        
        # Wait for user to scan QR code (only needed first time)
        print("Please scan the QR code if prompted...")
        print("Waiting 30 seconds for WhatsApp Web to load...")
        time.sleep(30)  # Adjust this time if needed
        
        # Send message to each number
        for phone_number in phone_numbers:
            try:
                # Remove spaces and special characters except +
                clean_number = phone_number.replace(" ", "").replace("-", "")
                
                # Create WhatsApp URL with pre-filled message
                encoded_message = urllib.parse.quote(message)
                url = f"https://web.whatsapp.com/send?phone={clean_number}&text={encoded_message}"
                
                print(f"\nSending message to {phone_number}...")
                driver.get(url)
                
                # Wait for the message box to load
                time.sleep(5)
                
                # Find and click the send button
                send_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Send"]'))
                )
                send_button.click()
                
                print(f"✓ Message sent to {phone_number}")
                time.sleep(3)  # Wait between messages to avoid being blocked
                
            except Exception as e:
                print(f"✗ Failed to send message to {phone_number}: {str(e)}")
                continue
        
        print("\n✓ All messages sent!")
        time.sleep(5)
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    # YOUR PHONE NUMBERS
    # ==================
    phone_numbers = [
        "+919876543210",  # Replace with actual phone numbers
        "+919123456789",    
    ]
    
    # YOUR MESSAGE
    # ============
    # Replace this with your actual message
    message = """ All the students who have given their names to take part in dance for College Annual Day are asked to prepare any one minute dance.
    There will be auditions tomorrow and the best will be selected.
    Share in your class group"""

    
    # Send messages
    print(f"Ready to send message to {len(phone_numbers)} numbers")
    print(f"\nMessage preview:\n{message}\n")
    input("Press Enter to start sending messages...")
    
    send_whatsapp_message(phone_numbers, message)