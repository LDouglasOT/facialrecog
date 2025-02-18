import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

NODEJS_ENDPOINT = "http://127.0.0.1:3000/process-school-payment"  # Replace with your actual Node.js endpoint

@csrf_exempt
def process_school_payment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            response = requests.post(NODEJS_ENDPOINT, json=data)
            
            return JsonResponse(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": "Failed to connect to Node.js service", "details": str(e)}, status=500)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)
    
    return JsonResponse({"error": "Invalid request method"}, status=400)