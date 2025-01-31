from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Parent, Transaction  # Assuming these models exist
import json
import jwt
import datetime
import requests
from .models import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import hmac
import hashlib

def generate_otp(key: str) -> str:
    """Generate a 5-digit OTP using HMAC SHA256"""
    hmac_digest = hmac.new(key.encode(), digestmod=hashlib.sha256).hexdigest()
    
    # Extract only digits and take the first 5
    numeric_otp = ''.join(filter(str.isdigit, hmac_digest))[:5]
    
    # Ensure it's always 5 digits by padding with leading zeros if needed
    return numeric_otp.zfill(5)


# JWT Secret
JWT_SECRET = 'H18E15A11H18D14D14F16D14C13Wed'


def generate_decoder(phone_number):
    alphabet = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]  # Define the mapping for digits
    letters = []

    for digit in phone_number:
        if digit.isdigit():
            index = int(digit)
            if 0 <= index <= 9:
                letters.insert(0, alphabet[index])  # Insert at the beginning (similar to unshift)
            else:
                letters.append("Invalid Digit")
        else:
            letters.append(digit)

    return "".join(reversed(letters))  # Reverse the list and join as a string

import requests

def send_sms(phone, otp_values):
    obj = {
        "phone": phone,
        "sms": f"Your Twinbrook temporary security code is {otp_values}"
    }
    remote_api_url = "https://facerecognition-django.onrender.com/api/sms/"

    try:
        response = requests.post(remote_api_url, json=obj)
        
        if response.status_code == 200:
            print(response.json())
            print("done")
        else:
            print(f"Failed to send SMS, status code: {response.status_code}")
    except requests.RequestException as error:
        print("Error sending SMS:", error)
        print("done")

    # Simulate saving the OTP
    try:
        # Assuming you have a model TempOtp to store OTPs
        # TempOtp.objects.create(phone=phone, otp=otp_values)
        pass  # Replace with actual saving logic
    except Exception as error:
        print("Failed to save OTP:", error)

# Generate OTP
@api_view(['GET', 'POST'])
def generate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_number = data.get("PhoneNumber", "")

        if not phone_number or len(phone_number) < 8 or len(phone_number) > 10:
            return JsonResponse({"message": "Check phone number and try again", "head": "Wrong Phone number"}, status=400)

        parent = Parent.objects.filter(phone=phone_number).first()

        if parent:
            # Generate the OTP
            decoder = generate_decoder(phone_number)
            token = generate_otp(decoder)
            send_sms(phone_number, token)  # Send OTP via SMS
            return JsonResponse({"message": "OTP message successfully sent", "head": "Success", "decorder": decoder})
        
        student = Child.objects.filter(phone=phone_number).first()
        if student:
            decoder = generate_decoder(phone_number)
            token = generate_otp(decoder)
            send_sms(phone_number, token)  
            return JsonResponse({"message": "OTP message successfully sent", "head": "Success", "decorder": decoder})
        
        return JsonResponse({"message": "User not found", "head": "User not found"}, status=404)


# Verify OTP
@csrf_exempt
def verify(request):

    if request.method == 'POST':
        print(request.body)
        data = json.loads(request.body)
        phone_number = data.get("PhoneNumber", "")
        token = data.get("token", "")
        decoder = data.get("decorder", "")
        
        if not phone_number or not token or not decoder:
            return JsonResponse({"message": "All fields are required", "head": "Missing Data"}, status=400)

        if verify_otp(decoder, token):
            auth_token = jwt.encode({"phone": phone_number}, JWT_SECRET, algorithm="HS256")
            return JsonResponse({"message": "OTP code successfully verified", "head": "Success", "authToken": auth_token})
        else:
            print('wrong otp code')
            return JsonResponse({"message": "The provided OTP code is wrong", "head": "OTP not correct"}, status=400)


# Verify OTP (Alternative method)
import hashlib
import hmac

def generate_otp(key: str) -> str:
    """Generate a 5-digit numeric OTP using HMAC SHA-256."""
    # Convert key to bytes
    key_bytes = key.encode()
    
    # Generate HMAC SHA-256 hash
    hmac_digest = hmac.new(key_bytes, b'', hashlib.sha256).hexdigest()
    
    # Extract first 10 characters of hex digest
    otp_hex = hmac_digest[:10]
    
    # Remove non-numeric characters and take first 5 digits
    numeric_otp = ''.join(filter(str.isdigit, otp_hex))[:5]
    
    # Ensure the OTP is always 5 digits (pad with zeros if needed)
    padded_otp = numeric_otp.zfill(5)
    
    return padded_otp

def verify_otp(key: str, entered_otp: str) -> bool:
    """Verify if the entered OTP matches the generated one."""
    generated_otp = generate_otp(key)
    
    # Debugging logs (optional)
    print(f"Generated OTP: {generated_otp}")
    print(f"Entered OTP: {entered_otp}")
    
    return generated_otp == entered_otp




# Generate Phone Number OTP
@csrf_exempt
def generate_phone_number(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_number = data.get("PhoneNumber", "")

        if len(phone_number) < 8 or len(phone_number) > 10:
            return JsonResponse({"message": "Check phone number and try again", "head": "Wrong Phone number"}, status=400)

        parent = Parent.objects.filter(phone=phone_number).first()
        student = Child.objects.filter(phone=phone_number).first()

        if parent or student:
            decoder = generate_decoder(phone_number)
            token = generate_otp(decoder)
            send_sms(phone_number, token)  # Send OTP via SMS
            return JsonResponse({"message": "OTP message successfully sent", "head": "Success", "decorder": decoder})

        return JsonResponse({"message": "No user exists connected to this phone number", "head": "User not found"}, status=404)


# Handle Payments (PayNow)
@csrf_exempt
def pay_now(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = data.get("amount", 0)
        payment_number = data.get("paymentNumber", "")
        phone = data.get("phone", "")

        if not phone or not amount or not payment_number:
            return JsonResponse({"message": "All fields are required", "head": "Missing Data"}, status=400)

        parent = Parent.objects.filter(phone=phone).first()
        if not parent:
            return JsonResponse({"message": "Invalid Phone Number", "head": "Error"}, status=400)

        students = Child.objects.filter(phone=phone)
        if not students:
            return JsonResponse({"message": "No student linked to this phone number", "head": "User not found"}, status=404)

        # Simulate payment processing (integration with payment API would go here)
        payment_data = {
            "username": "your_username",
            "password": "your_password",
            "amount": amount,
            "account": phone,
            "payment_reference": payment_number,
        }
        response = requests.post("https://payment.api.url", data=payment_data)  # Replace with actual payment API URL

        if response.status_code == 200:
            # Payment success, record transaction
            Transaction.objects.create(
                amount=amount,
                phone=phone,
                transaction_reference=response.json().get("transaction_reference"),
                status="SUCCEEDED"
            )
            return JsonResponse({"message": "Payment successful", "head": "Success"})
        else:
            return JsonResponse({"message": "Payment failed", "head": "Failure"}, status=500)

