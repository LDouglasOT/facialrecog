from django.http import JsonResponse
from .models import Parent, Pledge, Child
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Parent, Pledge
import json
from datetime import datetime
from django.utils import timezone

@csrf_exempt
def check_pledge(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone = data.get('phone')

            # Find the parent by phone number
            parent = Parent.objects.filter(phone=phone).first()

            if not parent:
                return JsonResponse({"message": "Invalid Phone Number"}, status=400)
            
            paid = 0
            expected = 0
            names = ""                
            percentage = (paid / expected) * 100 if expected > 0 else 0
            children = Child.objects.filter(phone=phone)
            for child in children:
                paid += child.paid
                expected += child.fees
                names += child.name + ", "

            pledge = Pledge.objects.filter(parent=parent).first()

            if pledge:
                days_difference = (timezone.now() - pledge.created_at).days

                today = datetime.now()
                days_difference = (timezone.now() - pledge.created_at).days

                days = days_difference

                if pledge.days > days:
                    print('pledge is still active')
                    return JsonResponse({
                        'message': "Pledge is active with days",
                        'daysLeft': pledge.days - days,
                        'names': names,
                        'amount': pledge.amount,
                        'expected': expected,
                        'paid': paid,
                        'percentage': percentage,
                        'give': True,
                        'pledge': True
                    }, status=200)

                else:
                    if percentage < 70:
                        pledge.delete()
                        return JsonResponse({
                        'message': "Pledge expired none paid",
                        'daysLeft': pledge.days - days,
                        'names': names,
                        'amount': pledge.amount,
                        'expected': expected,
                        'paid': paid,
                        'percentage': percentage,
                        'give': True,
                        'pledge': True
                    }, status=200)
                    else:
                        pledge.delete()
                        return JsonResponse({
                        'message': "Thanks for your pledge",
                        'daysLeft': pledge.days - days,
                        'names': names,
                        'amount': pledge.amount,
                        'expected': expected,
                        'paid': paid,
                        'percentage': percentage,
                        'give': False,
                        'pledge': True
                    }, status=200)
            else:

                if percentage < 70:
                    amount = (0.7 * expected) - paid
                    print(amount)
                    print("percentage less than 70")
                    return JsonResponse({
                        'message': "create pledge",
                        'daysLeft': 0,
                        "pay":(expected-amount)-paid,
                        'amount': amount,
                        'names': names,
                        'expected': expected,
                        'paid': paid,
                        'percentage': 70,
                        'give': False,
                        'pledge': False,
                        'phone': phone
                    }, status=200)

                else:
                    print("parent okay here")
                    return JsonResponse({
                        'message': "okay here",
                        'daysLeft': 0,
                        'amount': 0,
                        'names': names,
                        'expected': expected,
                        'paid': paid,
                        'percentage': 70,
                        'give': True,
                        'pledge': False,
                        'phone': phone
                    }, status=200)

        except Exception as error:
            print(error)
            return JsonResponse({"error": str(error)}, status=500)

def days(created_at):
    today = datetime.now()
    created_date = created_at
    diff_time = today - created_date
    diff_days = diff_time.days
    return diff_days



@csrf_exempt
def create_pledge(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = data.get('amount')
            days = data.get('days')
            phone = data.get('phone')
            print(data)
            # Find the parent by phone number
            parent = Parent.objects.filter(phone=phone).first()

            if not parent:
                return JsonResponse({"message": "Invalid Phone Number"}, status=400)

            pledge = Pledge.objects.create(
                parent=parent,
                amount=amount,
                days=days,
            )

            return JsonResponse({
                'id': pledge.id,
                'parentId': pledge.parent.id,
                'amount': pledge.amount,
                'days': pledge.days,
            }, status=200)

        except Exception as error:
            return JsonResponse({"error": str(error)}, status=500)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import FormSerializer, PledgeSerializer

class getpledges(APIView):
    def get(self, request):
        """Handles GET requests - Retrieves all pledges"""
        pledges = Pledge.objects.all()
        serializer = PledgeSerializer(pledges, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Handles POST requests - Filters pledges by date range and status"""
        try:
            data = request.data  # DRF automatically parses JSON
            startdate = data.get('startdate')
            enddate = data.get('enddate')
            status_filter = data.get('status')

            pledge_query = Pledge.objects.all()

            # Apply filters if values exist
            if startdate and enddate:
                pledge_query = pledge_query.filter(created_at__range=[startdate, enddate])
            if status_filter is not None:  # Ensure status is not empty
                pledge_query = pledge_query.filter(is_paid=status_filter)

            serializer = PledgeSerializer(pledge_query, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class getForms(APIView):
    def get(self, request):
        """Handles GET requests - Retrieves all pledges"""
        form = Form.objects.all()
        serializer = FormSerializer(form, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self,request):
        data = json.loads(request.body)
        id = data.get('id')
        forms = Form.objects.create(
            name=data.get('name'),
            classteacherphone=data.get('classteacherphone'),
            classteachernames=data.get('classteachernames'),
            classdirections=data.get('classdirections'),
        )
        return JsonResponse({"id": forms.id}, status=201)
    def put(self, request):
        data = json.loads(request.body)
        form = Form.objects.get(id=data.get('id'))
        form.delete()
        
        return JsonResponse({"message": "Form deleted successfully"}, status=200)
