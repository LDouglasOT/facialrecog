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

            # Retrieve pledge for the parent
            pledge = Pledge.objects.filter(parent=parent).first()

            # Retrieve children for the parent
            children = Child.objects.filter(phone=phone)
            paid = 0
            expected = 0
            names = ""
            today = datetime.now()
            days_difference = (timezone.now() - pledge.created_at).days
            for child in children:
                paid += child.paid
                expected += child.fees
                names += child.name + ", "

            # Calculate the percentage of the paid amount
            percentage = (paid / expected) * 100 if expected > 0 else 0
            days = days_difference
            # Check the pledge status
            if pledge:
                if pledge.days > days:
                    return JsonResponse({
                        'message': "Pledge is active",
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
                    return JsonResponse({
                        'message': "Pledge is active",
                        'daysLeft': pledge.days - days,
                        'names': names,
                        'amount': pledge.amount,
                        'expected': expected,
                        'paid': paid,
                        'percentage': percentage,
                        'give': True,
                        'pledge': True
                    }, status=200)

            if percentage < 70:
                amount = (0.7 * expected) - paid
                return JsonResponse({
                    'message': "Pledge is active",
                    'daysLeft': 0,
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
                return JsonResponse({
                    'message': "Pledge is active",
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
