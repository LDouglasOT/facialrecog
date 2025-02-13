from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Child
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

@csrf_exempt
def process_school_payment(request):
    if request.method == 'POST':
        try:
            print("hit the route now")
            data = json.loads(request.body)
            print(data)
            phone_number = data.get('paymentNumber')
            phone = data.get("phone")

            amount = data.get('amount')
            child = Child.objects.filter(phone=phone)
            network = data.get("network")

            api_url = "https://www.schoolpay.co.ug/site/get-student?chn=2"
            if network == "MTN":
                api_url="https://www.schoolpay.co.ug/site/get-student?chn=3"
            elif network == "M-Sente":
                api_url="https://www.schoolpay.co.ug/site/get-student?chn=10"
            print(phone_number)
            print(phone)
            if not phone_number and not phone:
                print("no number here")
                return JsonResponse({'error': 'Phone number required'}, status=400)

            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            driver = webdriver.Chrome(options=options)
            print("headlessly")
            driver.get(api_url)
            print("geturl now")
            time.sleep(2)
            print(child.paycode)
            reg_number_input = driver.find_element(By.ID, "dynamicmodel-pc_rgnumber")
            reg_number_input.send_keys(child.paycode)
            time.sleep(1)

            search_button = driver.find_element(By.CLASS_NAME, "find-student-btn")

            search_button.click()
            time.sleep(5)
            print("student search in progress")
            amount_input = driver.find_element(By.ID, "dynamicmodel-amount")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", amount_input)
            time.sleep(1)

            amount_input.send_keys(amount) 
            time.sleep(1)

            phone_number_input = driver.find_element(By.ID, "dynamicmodel-phone_number")
            phone_number_input.send_keys(phone_number)
            time.sleep(1)

            pay_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.col-12.btn.btn-secondary"))
            )
            print("pay button click in progress")
            pay_button.click()
            time.sleep(3)
            print("otp code entry in progress")
            otp_code = data.get('otp_code')
            if not otp_code:
                driver.quit()
                print("something went wrong")
                return JsonResponse({'error': 'OTP code is required'}, status=400)

            otp_input = driver.find_element(By.ID, "paymentotp")
            otp_input.send_keys(otp_code)
            time.sleep(1)

            confirm_button = driver.find_element(By.CSS_SELECTOR, ".confirm_payment")
            confirm_button.click()
            time.sleep(5)

            driver.quit()
            return JsonResponse({'message': 'Payment processed successfully'})
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)