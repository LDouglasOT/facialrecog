from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import Parent
import json
from django.forms.models import model_to_dict

@csrf_exempt
def create_parent(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name',"")
            phone = data.get('phone',"")
            phone2 = data.get('phone2',"")

            parent = Parent.objects.create(
                name=name,
                phone=phone,
                phone2=phone2,
            )
            parent=Parent.objects.get(id=parent.id)
            print(parent)
            return JsonResponse({"id":parent.id}, status=200)

        except Exception as error:
            return JsonResponse({"error": str(error)}, status=500)

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Parent

@csrf_exempt
def check_parent(request, parent_id):
    try:
        parent = get_object_or_404(Parent, id=parent_id)
        # Assuming related models are linked to Parent
        parent_data = {
            'id': parent.id,
            'name': parent.name,
            'phone': parent.phone,
            'phone2': parent.phone2,
            'children': list(parent.children.values()),
            'attendances': list(parent.attendances.values()),
            'pledges': list(parent.pledges.values()),
            'codes': list(parent.codes.values()),
        }
        return JsonResponse(parent_data, safe=False)
    except Exception as error:
        return JsonResponse({"error": str(error)}, status=500)


import jwt
from django.http import JsonResponse
from .models import Attendance
from django.views.decorators.csrf import csrf_exempt

# Define JWT secret key
JWT_SECRET = "H18E15A11H18D14D14F16D14C13Wed"

@csrf_exempt
def check_visitations(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            
            if not token:
                return JsonResponse({"error": "Token is required"}, status=400)

            # Decode the JWT token
            decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            phone_number = decoded.get('phone')

            # Fetch attendances related to the student
            # attendances = Attendance.objects.filter(studentcontact=phone_number)
            attendances = Attendance.objects.all()
            
            attendances_data = [
                {
                    "id": attendance.id,
                    "time_in": attendance.time_in,
                    "time_out": attendance.time_out,
                    "checkintype": attendance.checkintype,
                    "reason": attendance.reason,
                    "studentcontact": attendance.studentcontact,
                    "parent": {
                        "id": attendance.parent.id,
                        "name": attendance.parent.name,  # Assuming the Parent model has a 'name' field
                        "phone": attendance.parent.phone,  # Assuming the Parent model has a 'phone_number' field
                        "imgurl": attendance.parent.imgurl, 
                          # Assuming the Parent model has an 'imgurl' field
                    }
                }
                for attendance in attendances
            ]

            return JsonResponse({'attendances': attendances_data}, status=200)

        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token has expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid token"}, status=401)
        except Exception as error:
            print(error)
            return JsonResponse({"error": str(error)}, status=500)

