"""
WhatsApp Message Sender via Chrome
This script sends messages to specific numbers through WhatsApp Web
Handles both saved contacts and unsaved numbers
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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
    options.add_argument("--disable-blink-features=AutomationControlled")
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
                
                # Wait for the page to load
                time.sleep(5)
                
                # Try multiple methods to send the message
                message_sent = False
                
                # Method 1: Try to find and click the send button (works for both saved and unsaved)
                try:
                    send_button = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Send"]'))
                    )
                    send_button.click()
                    message_sent = True
                    print(f"✓ Message sent to {phone_number}")
                except TimeoutException:
                    pass
                
                # Method 2: If Method 1 fails, try finding the message input box and pressing Enter
                if not message_sent:
                    try:
                        # Find the message input box
                        message_box = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                        )
                        message_box.click()
                        time.sleep(1)
                        
                        # Type the message
                        message_box.clear()
                        message_box.send_keys(message)
                        time.sleep(1)
                        
                        # Press Enter to send
                        message_box.send_keys(Keys.ENTER)
                        message_sent = True
                        print(f"✓ Message sent to {phone_number} (via input method)")
                    except Exception as e:
                        pass
                
                # Method 3: Alternative send button XPath
                if not message_sent:
                    try:
                        send_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
                        )
                        send_button.click()
                        message_sent = True
                        print(f"✓ Message sent to {phone_number} (via icon method)")
                    except Exception as e:
                        pass
                
                # Method 4: Try finding button by class
                if not message_sent:
                    try:
                        send_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Send"]')
                        send_button.click()
                        message_sent = True
                        print(f"✓ Message sent to {phone_number} (via CSS method)")
                    except Exception as e:
                        pass
                
                if not message_sent:
                    print(f"✗ Could not send message to {phone_number} - please check if the number exists on WhatsApp")
                
                time.sleep(3)  # Wait between messages to avoid being blocked
                
            except Exception as e:
                print(f"✗ Failed to send message to {phone_number}: {str(e)}")
                continue
        
        print("\n✓ Process completed!")
        time.sleep(5)
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    # YOUR PHONE NUMBERS
    # ==================
    phone_numbers = [
        '+917904411858',
        '+918247438497',
        '+918019858570'
        
    ]
    
    # YOUR MESSAGE
    # ============
    # Replace this with your actual message
    message = """Hello! This is an automated message.

Replace this text with your actual message."""
    
    # Send messages
    print(f"Ready to send message to {len(phone_numbers)} numbers")
    print(f"\nMessage preview:\n{message}\n")
    input("Press Enter to start sending messages...")
    
    send_whatsapp_message(phone_numbers, message)
