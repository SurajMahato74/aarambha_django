from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models, transaction
from .models import UserNotification, Notice
from tasks.models import EmailQueue
from tasks.email_utils import queue_email

class NoticesAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_type = request.user.user_type
        
        # Get notices based on assignment mode
        notices = Notice.objects.filter(
            is_active=True,
            visibility__in=[user_type, 'both']
        ).filter(
            models.Q(assignment_mode='all') |
            models.Q(assigned_to=request.user) |
            models.Q(branch=getattr(request.user, 'branch', None))
        ).distinct().order_by('-created_at')
        
        data = []
        for notice in notices:
            data.append({
                'id': notice.id,
                'title': notice.title,
                'content': notice.content,
                'attachment': notice.attachment.url if notice.attachment else None,
                'attachment_name': notice.attachment.name.split('/')[-1] if notice.attachment else None,
                'created_at': notice.created_at.isoformat(),
                'created_by': notice.created_by.get_full_name() or notice.created_by.email
            })
        return Response(data)

class AdminNoticesAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=403)
            
        notices = Notice.objects.all().order_by('-created_at')
        data = []
        for notice in notices:
            # Get email statistics for this notice
            email_stats = EmailQueue.objects.filter(related_task_id=notice.id, email_type='notice_posted').aggregate(
                total=models.Count('id'),
                sent=models.Count('id', filter=models.Q(status='sent')),
                failed=models.Count('id', filter=models.Q(status='failed')),
                pending=models.Count('id', filter=models.Q(status='pending'))
            )
            
            email_status = "No emails"
            if email_stats['total'] > 0:
                status_parts = [f"{email_stats['sent']}/{email_stats['total']} sent"]
                if email_stats['failed'] > 0:
                    status_parts.append(f"{email_stats['failed']} failed")
                if email_stats['pending'] > 0:
                    status_parts.append(f"{email_stats['pending']} pending")
                email_status = ", ".join(status_parts)
            
            data.append({
                'id': notice.id,
                'title': notice.title,
                'content': notice.content,
                'visibility': notice.visibility,
                'attachment': notice.attachment.url if notice.attachment else None,
                'attachment_name': notice.attachment.name.split('/')[-1] if notice.attachment else None,
                'is_active': notice.is_active,
                'created_at': notice.created_at.isoformat(),
                'created_by': notice.created_by.get_full_name() or notice.created_by.email,
                'email_status': email_status
            })
        return Response(data)
    
    @transaction.atomic
    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=403)
            
        title = request.data.get('title')
        content = request.data.get('content')
        visibility = request.data.get('visibility', 'both')
        assignment_mode = request.data.get('assignment_mode', 'all')
        
        notice = Notice.objects.create(
            title=title,
            content=content,
            visibility=visibility,
            assignment_mode=assignment_mode,
            created_by=request.user
        )
        
        # Handle assignment and collect users for email
        users_to_notify = []
        
        if assignment_mode == 'all':
            from users.models import CustomUser
            if visibility == 'member':
                users_to_notify = CustomUser.objects.filter(user_type='member')
            elif visibility == 'volunteer':
                users_to_notify = CustomUser.objects.filter(user_type='volunteer')
            else:
                users_to_notify = CustomUser.objects.filter(user_type__in=['member', 'volunteer'])
                
        elif assignment_mode == 'individual':
            assigned_to_data = request.data.get('assigned_to', [])
            if isinstance(assigned_to_data, str):
                import json
                assigned_user_ids = json.loads(assigned_to_data)
            else:
                assigned_user_ids = assigned_to_data
            
            for user_id in assigned_user_ids:
                try:
                    from users.models import CustomUser
                    user = CustomUser.objects.get(id=user_id)
                    notice.assigned_to.add(user)
                    users_to_notify.append(user)
                except CustomUser.DoesNotExist:
                    continue
                    
        elif assignment_mode == 'branch':
            branch_id = request.data.get('branch_id')
            if branch_id:
                from branches.models import Branch
                try:
                    branch = Branch.objects.get(id=branch_id)
                    notice.branch = branch
                    notice.save()
                    
                    from users.models import CustomUser
                    if visibility == 'member':
                        users_to_notify = CustomUser.objects.filter(user_type='member', branch_id=branch_id)
                    elif visibility == 'volunteer':
                        users_to_notify = CustomUser.objects.filter(user_type='volunteer', branch_id=branch_id)
                    else:
                        users_to_notify = CustomUser.objects.filter(user_type__in=['member', 'volunteer'], branch_id=branch_id)
                except Branch.DoesNotExist:
                    pass
                    
        elif assignment_mode == 'branch_individual':
            branch_id = request.data.get('branch_id')
            assigned_to_data = request.data.get('assigned_to', [])
            
            if branch_id:
                from branches.models import Branch
                try:
                    branch = Branch.objects.get(id=branch_id)
                    notice.branch = branch
                    notice.save()
                except Branch.DoesNotExist:
                    pass
            
            if isinstance(assigned_to_data, str):
                import json
                assigned_user_ids = json.loads(assigned_to_data)
            else:
                assigned_user_ids = assigned_to_data
            
            for user_id in assigned_user_ids:
                try:
                    from users.models import CustomUser
                    user = CustomUser.objects.get(id=user_id)
                    notice.assigned_to.add(user)
                    users_to_notify.append(user)
                except CustomUser.DoesNotExist:
                    continue
        
        if 'attachment' in request.FILES:
            notice.attachment = request.FILES['attachment']
            notice.save()
        
        # Send emails to all targeted users
        for user in users_to_notify:
            # Create notification
            UserNotification.objects.create(
                user=user,
                title=f'New Notice: {notice.title}',
                message=f'A new notice has been posted: "{notice.title}"',
                notification_type='general'
            )
            
            # Queue email
            subject = f'New Notice: {notice.title}'
            message = f'Dear {user.get_full_name() or user.email},\n\nA new notice has been posted:\n\nTitle: {notice.title}\n\nContent: {content[:200]}...\n\nPlease log in to view the full notice.\n\nBest regards,\nAarambha Foundation Team'
            
            queue_email(
                recipient=user,
                subject=subject,
                message=message,
                email_type='notice_posted',
                task_id=notice.id
            )
        
        return Response({'message': 'Notice created successfully', 'notice_id': notice.id, 'notified_count': len(users_to_notify)})
    
    def put(self, request, notice_id):
        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=403)
            
        try:
            notice = Notice.objects.get(id=notice_id)
            notice.title = request.data.get('title', notice.title)
            notice.content = request.data.get('content', notice.content)
            notice.visibility = request.data.get('visibility', notice.visibility)
            notice.is_active = request.data.get('is_active', notice.is_active)
            
            if 'attachment' in request.FILES:
                notice.attachment = request.FILES['attachment']
            
            notice.save()
            return Response({'message': 'Notice updated successfully'})
        except Notice.DoesNotExist:
            return Response({'error': 'Notice not found'}, status=404)
    
    def delete(self, request, notice_id):
        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=403)
            
        try:
            notice = Notice.objects.get(id=notice_id)
            notice.delete()
            return Response({'message': 'Notice deleted successfully'})
        except Notice.DoesNotExist:
            return Response({'error': 'Notice not found'}, status=404)

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
    return Response({'notifications': data})

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
