from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import jwt
from .models import Parent, ClearanceCode, Form
from datetime import datetime
from django.forms.models import model_to_dict

import json

# JWT Secret
JWT_SECRET = "H18E15A11H18D14D14F16D14C13Wed"
import random


def generate_random_code():
    import random
    return str(random.randint(10000, 99999))


@csrf_exempt
def create_clearance_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            contact = data.get('contact',"")
            relationship = data.get('relationship',"")
            token = data.get('token',"")
            name = data.get('name',"")
            reason = data.get('reason',"")

            decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            print(decoded)
            phone_number = decoded.get('phone',"")
            print(phone_number)
            
            parent = Parent.objects.filter(phone=phone_number).first()
            if not parent:
                return JsonResponse({"error": "Parent not found"}, status=404)

            random_code = generate_random_code()
            
            clearance_code = ClearanceCode.objects.create(
                code=random_code,
                visitor=request.user.username,
                contact=parent.phone,
                visitor_contact=contact,
                relationship=relationship,
                parent=parent
            )
            print(clearance_code)
            clearance_code_dict = model_to_dict(clearance_code)
            return JsonResponse({"message": "Clearance code created successfully", "clearanceCode": clearance_code_dict}, status=201)
        except Exception as error:
            return JsonResponse({"error": str(error)}, status=500)


@csrf_exempt
def get_clearance_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            id = data.get('id')
            decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            clearance_code = ClearanceCode.objects.get(id=id)
            clearance_code_dict = model_to_dict(clearance_code)
            if not clearance_code_dict:
                return JsonResponse({"error": "Clearance code not found"}, status=404)
            return JsonResponse(clearance_code_dict, safe=False)
        except Exception as error:
            return JsonResponse({"error": str(error)}, status=500)



@csrf_exempt
def get_all_clearance_codes(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            print(token)
            decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            phone_number = decoded.get('phone')
            
            clearance_codes = ClearanceCode.objects.filter(contact=phone_number)
            
            return JsonResponse(list(clearance_codes.values()), safe=False, status=200)
        except Exception as error:
            return JsonResponse({"error": str(error)}, status=500)


@csrf_exempt
def update_clearance_code(request, id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            code = data.get('code')
            visitor = data.get('visitor')
            contact = data.get('contact')
            relationship = data.get('relationship')
            parent_id = data.get('parentId')
            expires_at = data.get('expiresAt')
            is_used = data.get('isUsed')

            clearance_code = get_object_or_404(ClearanceCode, id=id)

            clearance_code.code = code
            clearance_code.visitor = visitor
            clearance_code.contact = contact
            clearance_code.relationship = relationship
            clearance_code.parent_id = parent_id
            clearance_code.expires_at = expires_at
            clearance_code.is_used = is_used
            clearance_code.save()

            return JsonResponse({"message": "Clearance code updated successfully", "clearanceCode": clearance_code}, status=200)
        except Exception as error:
            return JsonResponse({"error": str(error)}, status=500)


@csrf_exempt
def delete_clearance_code(request, id):
    try:
        clearance_code = get_object_or_404(ClearanceCode, id=id)
        clearance_code.delete()
        return JsonResponse({"message": "Clearance code deleted successfully"}, status=204)
    except Exception as error:
        return JsonResponse({"error": str(error)}, status=500)


@csrf_exempt
def check_clearance(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            clearance_code_input = data.get('clearanceCode')

            if not clearance_code_input:
                return JsonResponse({"error": "Clearance code is required"}, status=400)

            attend = ClearanceCode.objects.filter(code=clearance_code_input).first()
            if not attend:
                return JsonResponse({"error": "Clearance code not found"}, status=404)

            if attend.is_used:
                return JsonResponse({"error": "Clearance code already used"}, status=400)

            form = Form.objects.filter(classteachernames=attend.classteachernames).first()

            return JsonResponse({
                'message': 'Cleared Successfully',
                'reason': attend.reason,
                'message': attend.message,
                'directions': form.classdirections,
                'phoneNumber': attend.phone_number,
                'names': attend.names,
                'contact_person': form.classteachernames,
                'visitor_names': attend.visitor,
                'visitor_phone': attend.contact,
                'time_in': attend.time_in,
                'estimated_time': 30,
                'context': attend.context
            }, status=200)
        except Exception as error:
            return JsonResponse({"error": str(error)}, status=500)


@csrf_exempt
def quick_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            relatives = data.get('relatives')
            reason = data.get('reason')

            
            return JsonResponse({"message": "Quick login processed", "data": {"relatives": relatives, "reason": reason}}, status=200)
        except Exception as error:
            return JsonResponse({"error": str(error)}, status=500)
