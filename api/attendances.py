from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status

from .models import Attendance, Parent, Child, Form
from .serializers import AttendanceSerializer

@api_view(['POST'])
def create_attendance(request):
    try:
        reason = request.data.get('reason')
        phone = request.data.get('phone')
        
        parent = Parent.objects.filter(phone=phone).first()
        if not parent:
            return Response({'message': 'Invalid Phone Number'}, status=status.HTTP_400_BAD_REQUEST)
        
        today = timezone.now().date()
        attendance_check = Attendance.objects.filter(parent=parent, date=today).first()
        
        if attendance_check:
            return Response({'message': 'Attendance already taken'}, status=status.HTTP_400_BAD_REQUEST)
        
        attendance = Attendance.objects.create(
            reason=reason,
            date=timezone.now(),
            present=True,
            parent=parent
        )
        
        response_message = ''
        class_directions = ''
        phone_number = ''
        contact_person = ''
        
        form = Form.objects.filter(name=reason.lower()).first()
        if form:
            contact_person = form.classteachernames
            phone_number = form.classteacherphone
            class_directions = form.classdirections
            response_message = reason
        
        return Response({
            'message': response_message,
            'directions': class_directions,
            'phoneNumber': phone_number,
            'contact_person': contact_person,
            'visitor_phone': phone,
            'visitor_email': 'not provided',
            'time_in': timezone.now().strftime('%H:%M'),
            'estimated_time': '29 MINUTES'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_attendance_by_id(request):
    attendance = get_object_or_404(Attendance, id=request.user.pk)
    serializer = AttendanceSerializer(attendance)
    return Response(serializer.data)


@api_view(['PUT'])
def update_attendance(request, id):
    attendance = get_object_or_404(Attendance, id=id)
    serializer = AttendanceSerializer(attendance, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_attendance(request, id):
    attendance = get_object_or_404(Attendance, id=id)
    attendance.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Attendance
from .serializers import AttendanceSerializer

@api_view(["GET", "POST"])
def get_all_attendances(request):
    if request.method == 'GET':
        attendances = Attendance.objects.all()
        serializer = AttendanceSerializer(attendances, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        serializer = AttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
