import threading
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def take_screenshot(driver, step):
    """Helper function to take screenshots."""
    filename = f"screenshot_{step}.png"
    driver.save_screenshot(filename)
    print(f"📸 Screenshot saved: {filename}")

def log_step(step):
    """Helper function to print progress logs."""
    print(f"✅ Step {step} completed.")

def createTasks(phone, amount, paycode, network):
    print("🔄 Starting headless Selenium process...")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode for VPS
    options.add_argument("--no-sandbox")  # Required for some VPS environments
    options.add_argument("--disable-dev-shm-usage")  # Fix memory issues
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    driver = webdriver.Chrome(options=options)

    try:
        # Step 1: Open the page
        print(f"🌐 Opening page: {network}")
        driver.get(network)
        time.sleep(2)  
        take_screenshot(driver, "01_open_page")
        log_step("01_open_page")

        # Step 2: Enter the registration number
        print("⌨ Entering registration number...")
        reg_number_input = driver.find_element(By.ID, "dynamicmodel-pc_rgnumber")
        reg_number_input.send_keys(paycode)  
        time.sleep(1)
        take_screenshot(driver, "02_enter_reg_number")
        log_step("02_enter_reg_number")

        # Step 3: Click the search button
        print("🔍 Clicking search button...")
        search_button = driver.find_element(By.CLASS_NAME, "find-student-btn")
        search_button.click()
        time.sleep(5)  
        take_screenshot(driver, "03_click_search")
        log_step("03_click_search")

        # Step 4: Scroll to amount input and enter amount
        print("📜 Scrolling to amount input field...")
        amount_input = driver.find_element(By.ID, "dynamicmodel-amount")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", amount_input)
        time.sleep(1)
        take_screenshot(driver, "04_scroll_to_amount")
        log_step("04_scroll_to_amount")

        print("💰 Entering amount...")
        amount_input.send_keys(amount)
        time.sleep(1)
        take_screenshot(driver, "05_enter_amount")
        log_step("05_enter_amount")

        # Step 5: Enter the phone number
        print("📱 Entering phone number...")
        phone_number_input = driver.find_element(By.ID, "dynamicmodel-phone_number")
        phone_number_input.send_keys(phone)  
        time.sleep(1)
        take_screenshot(driver, "06_enter_phone")
        log_step("06_enter_phone")

        # Step 6: Click "Pay Fee" button
        print("💳 Clicking Pay Fee button...")
        pay_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.col-12.btn.btn-secondary"))
        )
        pay_button.click()
        time.sleep(3)  
        take_screenshot(driver, "07_click_pay_fee")
        log_step("07_click_pay_fee")

        # Step 7: Enter OTP code
        otp_code = input("🔐 Enter the OTP code sent to your phone: ")
        print("⌨ Entering OTP code...")
        otp_input = driver.find_element(By.ID, "paymentotp")  
        otp_input.send_keys(otp_code)  
        time.sleep(1)
        take_screenshot(driver, "08_enter_otp")
        log_step("08_enter_otp")

        # Step 8: Click the "Confirm" button
        print("✅ Clicking Confirm button...")
        confirm_button = driver.find_element(By.CSS_SELECTOR, ".confirm_payment")
        confirm_button.click()
        time.sleep(5)  
        take_screenshot(driver, "09_click_confirm")
        log_step("09_click_confirm")

        print("🎉 ✅ Payment successfully processed, all screenshots saved.")

    except Exception as e:
        print(f"❌ ERROR: {e}")

    finally:
        driver.quit()
        print("🚪 Closing browser and ending process.")

@csrf_exempt
def process_school_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        amount = data.get("amount")
        paymentNumber = data.get("paymentNumber")
        network = data.get("network")
        phone = data.get("phone")

        if network == "MTN":
            network = "https://www.schoolpay.co.ug/site/get-student?chn=3"
        elif network == "AIRTEL":
            network = "https://www.schoolpay.co.ug/site/get-student?chn=2"
        else:
            network = "https://www.schoolpay.co.ug/site/get-student?chn=10"

        print(f"📢 Starting payment process for phone: {phone}, amount: {amount}, network: {network}")

        # Run createTasks in a separate thread
        task_thread = threading.Thread(target=createTasks, args=(phone, amount, "1001054592", network))
        task_thread.start()

        return JsonResponse({"message": "Payment processing started. Check logs for updates."}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=400)
