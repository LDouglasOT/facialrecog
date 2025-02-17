import threading
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up Selenium WebDriver (Ensure you have the correct driver installed)
def createTasks(phone,amount,paycode,network):
    print("headlessly")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode if you don't need to see the browser
    driver = webdriver.Chrome(options=options)

    try:
        # Step 1: Open the page
        driver.get(network)
        time.sleep(2)  # Wait for page to load

        # Step 2: Enter the registration number
        reg_number_input = driver.find_element(By.ID, "dynamicmodel-pc_rgnumber")
        reg_number_input.send_keys(paycode)  # Replace with actual reg number
        time.sleep(1)

        # Step 3: Click the search button
        search_button = driver.find_element(By.CLASS_NAME, "find-student-btn")
        search_button.click()
        time.sleep(5)  # Wait for the next page to load

        # Step 4: Wait for the amount field and scroll to the middle of the page
        amount_input = driver.find_element(By.ID, "dynamicmodel-amount")
        
        # Scroll to the middle of the page to ensure the element is visible and interactable
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", amount_input)
        time.sleep(1)  # Wait for smooth scroll

        # Enter the amount
        amount_input.send_keys(amount)  # Replace with the actual amount
        time.sleep(1)

        # Step 5: Enter the phone number
        phone_number_input = driver.find_element(By.ID, "dynamicmodel-phone_number")
        phone_number_input.send_keys(phone)  # Replace with actual phone number
        time.sleep(1)

        # Step 6: Check if "Pay Fee" button is clickable, then click
        pay_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.col-12.btn.btn-secondary"))
        )

        # Print the element details
        print("Pay Fee button element:", pay_button)

        pay_button.click()
        time.sleep(3) 
        otp_code = input("Enter the OTP code sent to your phone: ")

        # Step 7: Enter OTP code
        otp_input = driver.find_element(By.ID, "paymentotp")  # Find OTP input field
        otp_input.send_keys(otp_code)  # Enter the OTP code
        time.sleep(1)

        # Step 8: Click the "Confirm" button to submit OTP
        confirm_button = driver.find_element(By.CSS_SELECTOR, ".confirm_payment")
        confirm_button.click()
        time.sleep(5)  # Wait for submission processing

        print("✅ OTP submitted successfully, screenshots saved.")

    except Exception as e:
        print(f"❌ Error occurred: {e}")

    finally:
        driver.quit()


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
        
        # Run createTasks in a separate thread
        task_thread = threading.Thread(target=createTasks, args=(phone, amount, "1001054592", network))
        task_thread.start()
        
        return JsonResponse({"message": "Payment processing started."}, status=200)
    
    return JsonResponse({"error": "Invalid request method"}, status=400)






