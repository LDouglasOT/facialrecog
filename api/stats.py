
from django.http import JsonResponse
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
import json
from datetime import datetime
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from django.forms.models import model_to_dict
from django.db.models import Sum, Count, Value
from django.db.models.functions import Coalesce



@api_view(["GET"])
def get_stats(request):
    if request.method == 'GET':
        stats = {}
        stats['total_children'] = Child.objects.all().count()
        stats['total_parents'] = Parent.objects.all().count()
        stats['total_attendances'] = Attendance.objects.all().count()
        stats['total_clearance_codes'] = ClearanceCode.objects.all().count()
        stats['total_notifications'] = Notification.objects.all().count()
        stats['total_pledges'] = Pledge.objects.all().count()
        stats['total_transactions'] = Transaction.objects.all().count()
        stats['total_staff'] = Form.objects.all().count()
        stats['amount'] = Transaction.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        stats['pledges'] = Pledge.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        return JsonResponse(stats, status=200)
    
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    

def getFaces(request):
    if request.method == 'GET':
        faces = Face.objects.all()

        return JsonResponse({"faces": list(faces.values())}, status=200)
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        parent = Parent.objects.filter(id=id)
        if not parent:
            parent = Staff.objects.filter(id=id)
        if not parent:
            return JsonResponse({"error": "Parent not found"}, status=404)

        return JsonResponse({"face": model_to_dict(parent)}, status=201)  
    
@api_view(["GET"])
def get_parents_with_active_pledge(request):
    if request.method == "GET":
        parents_data = Parent.objects.annotate(
            active_pledged=Coalesce(
                Sum('pledges__amount', filter=models.Q(pledges__is_paid=False)), 
                Value(0)
            ),
            attendance_count=Coalesce(
                Count('attendances'), 
                Value(0)
            )
        )

        parent_list = [
            {
                "id": parent.id,
                "name": parent.name,
                "phone": parent.phone,
                'img':parent.imgurl,
                "active_pledged": parent.active_pledged,  # Only unpaid pledges are counted
                "attendance_count": parent.attendance_count  # Number of times the parent attended
            }
            for parent in parents_data
        ]

        # Return the list directly as JSON
        return JsonResponse(parent_list, safe=False, status=200)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        parent = Parent.objects.filter(id=id)
        if not parent:
            parent = Staff.objects.filter(id=id)
        if not parent:
            return JsonResponse({"error": "Parent not found"}, status=404)

        return JsonResponse({"parent": model_to_dict(parent)}, status=201)
    
def fetchStudents(request):
    if request.method=="GET":

        students = Child.objects.all()
        return JsonResponse(list(students.values()), status=200)
    if request.method=="POST":
        data = json.loads(request.body)
        id = data.get('id')
        student = Child.objects.filter(id=id)
        if not student:
            return JsonResponse({"error": "Student not found"}, status=404)

        return JsonResponse({"student": model_to_dict(student)}, status=201)
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *

class getProducts(APIView):
    def get(self, request):
        try:
            product = Product.objects.all()
            # serializer = ProductSerializer(data = product, many=True)
            # print(serializer.is_valid())

            # if serializer.is_valid():
            #     return JsonResponse(serializer.data,status=200)
            # else:
            #     print(serializer.is_valid())
            #     return JsonResponse(status=500)
            prods = list(product.values("id","ProductName","price","quantity","itemDescription","Type","imgurl","venue"))
            return JsonResponse(prods,status=200,safe=False)
        except Exception as e:
            print(e)
            return Response(status=500)

    def post(self, request):
        try:
            data = json.load(request.body)
            prod = Product.objects.create(
                ProductName = data.get('name'),
                price = data.get("price"),
                quantity = data.get("quantity"),
                itemDescription = data.get("itemDescription"),
                images = data.get("images"),
                Type=data.get("Type"),
                imgurl = data.get("imgurl"),
                venue = data.get("venue")
            )
            return JsonResponse(status=201)
        except:
            return JsonResponse(status=500)