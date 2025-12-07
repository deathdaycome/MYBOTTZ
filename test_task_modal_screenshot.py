#!/usr/bin/env python3
"""
Test script to take a screenshot of the compact task modal
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import base64

# Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')

# Admin credentials
ADMIN_URL = "http://147.45.215.199:8001/admin"
USERNAME = "admin"
PASSWORD = "qwerty123"

try:
    print("🚀 Starting Chrome driver...")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1920, 1080)

    print(f"📄 Navigating to login page: {ADMIN_URL}/login")
    driver.get(f"{ADMIN_URL}/login")
    time.sleep(2)

    # Login
    print("🔐 Logging in...")
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")

    username_field.send_keys(USERNAME)
    password_field.send_keys(PASSWORD)

    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()

    print("⏳ Waiting for dashboard to load...")
    time.sleep(3)

    # Navigate to tasks page
    print("📋 Navigating to tasks page...")
    driver.get(f"{ADMIN_URL}/tasks")
    time.sleep(3)

    # Find and click on the first task card to open modal
    print("🔍 Looking for task cards...")
    wait = WebDriverWait(driver, 10)

    # Wait for task cards to load
    task_cards = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='cursor-pointer'][class*='rounded']"))
    )

    print(f"✅ Found {len(task_cards)} task cards")

    if len(task_cards) > 0:
        print("👆 Clicking on first task...")
        # Click the first task
        driver.execute_script("arguments[0].click();", task_cards[0])
        time.sleep(2)

        # Wait for modal to appear
        print("⏳ Waiting for modal to open...")
        modal = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='fixed'][class*='inset-0']"))
        )

        print("📸 Taking screenshot of compact task modal...")
        screenshot_path = "/Users/ivan/Desktop/СРМ РЕАКТ/task_modal_compact_screenshot.png"
        driver.save_screenshot(screenshot_path)

        print(f"✅ Screenshot saved to: {screenshot_path}")
        print("🎉 Success! Compact task modal screenshot captured!")

    else:
        print("❌ No task cards found on the page")
        screenshot_path = "/Users/ivan/Desktop/СРМ РЕАКТ/tasks_page_no_cards.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot of tasks page saved to: {screenshot_path}")

except Exception as e:
    print(f"❌ Error: {e}")
    screenshot_path = "/Users/ivan/Desktop/СРМ РЕАКТ/error_screenshot.png"
    try:
        driver.save_screenshot(screenshot_path)
        print(f"📸 Error screenshot saved to: {screenshot_path}")
    except:
        pass

finally:
    print("🔒 Closing browser...")
    driver.quit()
    print("✅ Done!")
