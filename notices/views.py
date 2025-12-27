from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserNotification

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_notifications(request):
    notifications = UserNotification.objects.filter(user=request.user).order_by('-created_at')
    data = []
    for notification in notifications:
        data.append({
            'id': notification.id,
            'notification_type': notification.notification_type,
            'title': notification.title,
            'message': notification.message,
            'is_read': notification.is_read,
            'created_at': notification.created_at,
            'related_application_id': notification.related_application.id if notification.related_application else None,
            'related_application_type': notification.related_application.application_type if notification.related_application else None,
        })
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, pk):
    try:
        notification = UserNotification.objects.get(pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
    except UserNotification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
