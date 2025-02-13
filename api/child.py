import json
from django.http import JsonResponse
from .serializers import ChildSerializer
from rest_framework.decorators import api_view
from .models import *
from django.forms.models import model_to_dict


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
import json
from .models import Child, Form

@csrf_exempt
@api_view(['POST'])
def create_child(request):
    try:
        # Parse JSON data properly
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        # Extract fields
        name = data.get('name')
        form_id = data.get('form')
        fees = data.get('expected_fees')
        paycode = data.get('paycode')
        paid = data.get('paid')
        phone = data.get('phone')

        # Validate required fields
        if not all([name, form_id, fees, paycode, paid, phone]):
            return JsonResponse({'error': 'All fields are required'}, status=400)

        # Fetch form object
        form = get_object_or_404(Form, id=form_id)

        # Create the child record
        child = Child.objects.create(
            name=name,
            phone=phone,
            fees=fees,
            paycode=paycode,
            form=form,
            paid=paid,
        )

        return JsonResponse({'message': 'Child created successfully', 'child_id': child.id}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)



def getChildren(request):
    if request.method == 'GET':
        children = Child.objects.all()
        serializer = ChildSerializer(children, many=True)
        print(serializer.data)
        return JsonResponse(serializer.data, safe=False, status=200)

    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        parent = Parent.objects.filter(id=id)
        if not parent:
            parent = Staff.objects.filter(id=id)
        if not parent:
            return JsonResponse({"error": "Parent not found"}, status=404)

        return JsonResponse({"child": model_to_dict(parent)}, status=201)

@api_view(['GET'])
def get_child_by_id(request, id):
    try:
        child = Child.objects.get(id=id)
        return JsonResponse({
            'id': child.id,
            'name': child.name,
            'parentId': child.parent.id,
            'fees': str(child.fees)
        })
    except Child.DoesNotExist:
        return JsonResponse({'error': 'Child not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@api_view(['PUT'])
def update_child(request, id):
    try:
        data = request.data
        child = Child.objects.get(id=id)
        
        if 'name' in data:
            child.name = data['name']
        if 'parentId' in data:
            child.parent = Parent.objects.get(id=data['parentId'])
        if 'fees' in data:
            child.fees = data['fees']
        
        child.save()
        
        return JsonResponse({
            'id': child.id,
            'name': child.name,
            'parentId': child.parent.id,
            'fees': str(child.fees)
        })
    except Child.DoesNotExist:
        return JsonResponse({'error': 'Child not found'}, status=404)
    except Parent.DoesNotExist:
        return JsonResponse({'error': 'Parent not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['DELETE'])
def delete_child(request, id):
    try:
        child = Child.objects.get(id=id)
        child.delete()
        return JsonResponse({'message': 'Child deleted successfully'}, status=204)
    except Child.DoesNotExist:
        return JsonResponse({'error': 'Child not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
