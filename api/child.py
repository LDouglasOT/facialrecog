from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import Child, Parent

@api_view(['POST'])
def create_child(request):
    try:
        data = request.data
        parent = Parent.objects.get(id=data['parentId'])
        
        child = Child.objects.create(
            name=data['name'],
            parent=parent,
            fees=data.get('fees', 0)
        )
        
        return JsonResponse({'id': child.id, 'name': child.name, 'parentId': child.parent.id, 'fees': str(child.fees)}, status=201)
    except Parent.DoesNotExist:
        return JsonResponse({'error': 'Parent not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


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
