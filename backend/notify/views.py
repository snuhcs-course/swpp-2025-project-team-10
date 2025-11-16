from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import Notification
from .serializers import NotificationSerializer

@api_view(['GET'])
def notifications(request):
    # Get unread notifications for the logged-in user
    received_notifications = request.user.notifications.filter(is_read=False)
    serializer = NotificationSerializer(received_notifications, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['PATCH'])
def read_notification(request, pk):
    try:
        notification = Notification.objects.get(pk=pk, recipient=request.user)
    except Notification.DoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)

    notification.is_read = True
    notification.save(update_fields=['is_read'])
    return JsonResponse({'message': 'Notification marked as read'})
