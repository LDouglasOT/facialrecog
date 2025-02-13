import json
from django.http import JsonResponse
from .models import Notification
from django.views.decorators.csrf import csrf_exempt
from django.views import View

# View to create a new notification
@csrf_exempt
def create_notification(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        notification = Notification.objects.create(
            title=data.get('title'),
            message=data.get('message'),
            creator = data.get('creator'),
        )
        return JsonResponse({'message': 'Notification created', 'notification': notification.id}, status=201)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

# View to get all notifications
def get_all_notifications(request):
    if request.method == 'GET':
        notifications = Notification.objects.all().values()
        return JsonResponse(list(notifications), safe=False, status=200)

# View to get notifications by recipient
def get_notifications_by_recipient(request, recipient_id):
    if request.method == 'GET':
        notifications = Notification.objects.filter(recipient_id=recipient_id).values()
        return JsonResponse(list(notifications), safe=False, status=200)

# View to get a notification by ID
def get_notification_by_id(request, notification_id):
    if request.method == 'GET':
        try:
            notification = Notification.objects.get(id=notification_id)
            return JsonResponse({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'recipientId': notification.recipient_id,
                'type': notification.type,
                'metadata': notification.metadata,
                'isRead': notification.is_read
            })
        except Notification.DoesNotExist:
            return JsonResponse({'error': 'Notification not found'}, status=404)

# View to update a notification
@csrf_exempt
def update_notification(request, notification_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            notification = Notification.objects.get(id=notification_id)
            notification.title = data.get('title', notification.title)
            notification.message = data.get('message', notification.message)
            notification.type = data.get('type', notification.type)
            notification.is_read = data.get('isRead', notification.is_read)
            notification.metadata = data.get('metadata', notification.metadata)
            notification.save()
            return JsonResponse({'message': 'Notification updated', 'notificationId': notification.id}, status=200)
        except Notification.DoesNotExist:
            return JsonResponse({'error': 'Notification not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

# View to delete a notification
@csrf_exempt
def delete_notification(request, notification_id):
    if request.method == 'DELETE':
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.delete()
            return JsonResponse({'message': 'Notification deleted'}, status=200)
        except Notification.DoesNotExist:
            return JsonResponse({'error': 'Notification not found'}, status=404)

# View to mark a notification as read
@csrf_exempt
def mark_notification_as_read(request, notification_id):
    if request.method == 'PUT':
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.is_read = True
            notification.save()
            return JsonResponse({'message': 'Notification marked as read'}, status=200)
        except Notification.DoesNotExist:
            return JsonResponse({'error': 'Notification not found'}, status=404)
