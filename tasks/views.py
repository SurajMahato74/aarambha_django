from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db import models, transaction
from datetime import datetime
from .models import Task, TaskMaterial, EmailQueue, TaskSubmission
from .email_utils import queue_email, create_task_assignment_email
from users.models import CustomUser
from notices.models import UserNotification

class MyTasksAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        tasks = Task.objects.filter(assigned_to=request.user)
        data = []
        for task in tasks:
            materials = [{'id': m.id, 'filename': m.filename, 'url': m.file.url} for m in task.materials.all()]
            
            # Check if user has submitted this task
            submission = TaskSubmission.objects.filter(task=task, user=request.user).first()
            
            # Determine task status for this user
            if submission:
                user_status = submission.status
                submission_text = submission.submission_text
                submission_file = submission.submission_file.url if submission.submission_file else None
                admin_feedback = submission.admin_feedback
            else:
                user_status = 'assigned'
                submission_text = None
                submission_file = None
                admin_feedback = None
            
            data.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'deadline': task.deadline.isoformat(),
                'status': user_status,
                'task_materials': materials,
                'task_links': task.task_links,
                'submission_text': submission_text,
                'submission_file': submission_file,
                'admin_feedback': admin_feedback,
                'rating': submission.rating if submission else None,
                'created_at': task.created_at.isoformat(),
            })
        return Response(data)

class SubmitTaskAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id, assigned_to=request.user)
            
            # Create or update task submission
            submission, created = TaskSubmission.objects.get_or_create(
                task=task,
                user=request.user,
                defaults={
                    'submission_text': request.data.get('submission_text', ''),
                    'status': 'submitted'
                }
            )
            
            if not created:
                submission.submission_text = request.data.get('submission_text', '')
                submission.status = 'submitted'
                submission.submitted_at = timezone.now()
            
            if 'submission_file' in request.FILES:
                submission.submission_file = request.FILES['submission_file']
            
            submission.save()
            
            # Create notification for admin
            UserNotification.objects.create(
                user=task.assigned_by,
                title=f'Task Submitted: {task.title}',
                message=f'{request.user.get_full_name() or request.user.email} has submitted the task "{task.title}".',
                notification_type='task_submitted'
            )
            
            # Create notification for user (confirmation)
            UserNotification.objects.create(
                user=request.user,
                title=f'Task Submitted: {task.title}',
                message=f'Your task "{task.title}" has been submitted successfully and is now under review.',
                notification_type='task_submitted_confirmation'
            )
            
            # Send email confirmation to user
            from django.core.mail import send_mail
            try:
                send_mail(
                    subject=f'Task Submitted: {task.title}',
                    message=f'Dear {request.user.get_full_name() or request.user.email},\n\nYour task "{task.title}" has been submitted successfully and is now under review.\n\nThank you for your contribution!\n\nBest regards,\nAarambha Foundation Team',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                pass  # Don't fail submission if email fails
            
            return Response({'message': 'Task submitted successfully'})
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=404)

class AdminTasksAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=403)
            
        tasks = Task.objects.all()
        data = []
        for task in tasks:
            assigned_users = [{'id': u.id, 'name': u.get_full_name() or u.email} for u in task.assigned_to.all()]
            materials = [{'id': m.id, 'filename': m.filename, 'url': m.file.url} for m in task.materials.all()]
            
            # Get email status for this task
            email_stats = EmailQueue.objects.filter(related_task_id=task.id).aggregate(
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
            
            # Get submission count for this task
            submission_count = TaskSubmission.objects.filter(task=task, status__in=['submitted', 'approved']).count()
            
            data.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'assign_to_type': task.assign_to_type,
                'deadline': task.deadline.isoformat(),
                'status': task.status,
                'assigned_to': assigned_users,
                'submission_count': submission_count,
                'task_materials': materials,
                'task_links': task.task_links,
                'submission_text': task.submission_text,
                'submission_file': task.submission_file.url if task.submission_file else None,
                'admin_feedback': task.admin_feedback,
                'submitted_at': task.submitted_at.isoformat() if task.submitted_at else None,
                'created_at': task.created_at.isoformat(),
                'email_status': email_status
            })
        return Response(data)

class ReviewTaskAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, task_id):
        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=403)
            
        try:
            task = Task.objects.get(id=task_id)
            action = request.data.get('action')  # 'approve' or 'redo'
            feedback = request.data.get('feedback', '')
            
            task.admin_feedback = feedback
            task.reviewed_by = request.user
            task.reviewed_at = timezone.now()
            
            if action == 'approve':
                task.status = 'approved'
                notification_title = f'Task Approved: {task.title}'
                notification_message = f'Your task "{task.title}" has been approved.'
            else:
                task.status = 'redo_requested'
                notification_title = f'Task Needs Revision: {task.title}'
                notification_message = f'Your task "{task.title}" needs revision. Please check the feedback.'
            
            task.save()
            
            # Create notifications for assigned users
            for user in task.assigned_to.all():
                UserNotification.objects.create(
                    user=user,
                    title=notification_title,
                    message=notification_message + (f' Feedback: {feedback}' if feedback else ''),
                    notification_type='task_reviewed'
                )
            
            return Response({'message': 'Task reviewed successfully'})
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=404)

class CreateTaskAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=403)
            
        title = request.data.get('title')
        description = request.data.get('description')
        deadline = request.data.get('deadline')
        assign_to_type = request.data.get('assign_to_type', 'both')
        assignment_mode = request.data.get('assignment_mode', 'individual')
        task_links = request.data.get('task_links', '')
        
        # Parse deadline string to datetime with timezone
        deadline_dt = timezone.make_aware(datetime.fromisoformat(deadline.replace('Z', '+00:00').replace('+00:00', '')))
        
        task = Task.objects.create(
            title=title,
            description=description,
            deadline=deadline_dt,
            assign_to_type=assign_to_type,
            task_links=task_links,
            assigned_by=request.user
        )
        
        # Handle multiple file uploads
        if 'task_materials' in request.FILES:
            files = request.FILES.getlist('task_materials')
            for file in files:
                TaskMaterial.objects.create(
                    task=task,
                    file=file,
                    filename=file.name
                )
        
        # Handle different assignment modes
        users_to_assign = []
        
        if assignment_mode == 'individual':
            # Handle assigned users
            assigned_to_data = request.data.get('assigned_to')
            if isinstance(assigned_to_data, str):
                import json
                assigned_user_ids = json.loads(assigned_to_data)
            else:
                assigned_user_ids = assigned_to_data or []
            
            for user_id in assigned_user_ids:
                try:
                    user = CustomUser.objects.get(id=user_id)
                    users_to_assign.append(user)
                except CustomUser.DoesNotExist:
                    continue
                    
        elif assignment_mode == 'branch_individual':
            # Handle specific users from a branch
            assigned_to_data = request.data.get('assigned_to')
            if isinstance(assigned_to_data, str):
                import json
                assigned_user_ids = json.loads(assigned_to_data)
            else:
                assigned_user_ids = assigned_to_data or []
            
            for user_id in assigned_user_ids:
                try:
                    user = CustomUser.objects.get(id=user_id)
                    users_to_assign.append(user)
                except CustomUser.DoesNotExist:
                    continue
                    
        elif assignment_mode == 'all':
            # Assign to all users of specified type
            if assign_to_type == 'member':
                users_to_assign = CustomUser.objects.filter(user_type='member')
            elif assign_to_type == 'volunteer':
                users_to_assign = CustomUser.objects.filter(user_type='volunteer')
            else:
                users_to_assign = CustomUser.objects.filter(user_type__in=['member', 'volunteer'])
                
        elif assignment_mode == 'branch':
            # Assign to users in specific branch
            branch_id = request.data.get('branch_id')
            if branch_id:
                if assign_to_type == 'member':
                    users_to_assign = CustomUser.objects.filter(user_type='member', branch_id=branch_id)
                elif assign_to_type == 'volunteer':
                    users_to_assign = CustomUser.objects.filter(user_type='volunteer', branch_id=branch_id)
                else:
                    users_to_assign = CustomUser.objects.filter(user_type__in=['member', 'volunteer'], branch_id=branch_id)
        
        # Assign users and create notifications + queue emails
        for user in users_to_assign:
            task.assigned_to.add(user)
            
            # Create individual notification
            UserNotification.objects.create(
                user=user,
                title=f'New Task Assigned: {task.title}',
                message=f'You have been assigned a new task: "{task.title}". Deadline: {task.deadline.strftime("%Y-%m-%d %H:%M")}',
                notification_type='task_assigned'
            )
            
            # Queue individual email
            subject, message = create_task_assignment_email(user, task)
            queue_email(
                recipient=user,
                subject=subject,
                message=message,
                email_type='task_assigned',
                task_id=task.id
            )
        
        return Response({'message': 'Task created successfully', 'task_id': task.id, 'assigned_count': len(users_to_assign)})

class TaskDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, task_id):
        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=403)
            
        try:
            task = Task.objects.get(id=task_id)
            
            # Get assigned users with their email and submission status
            assigned_users = []
            for user in task.assigned_to.all():
                # Check email status
                email = EmailQueue.objects.filter(related_task_id=task.id, recipient=user).first()
                email_status = email.status if email else 'no_email'
                
                # Check if overdue
                is_overdue = timezone.now() > task.deadline
                
                # Check individual user submission status
                submission = TaskSubmission.objects.filter(task=task, user=user).first()
                submission_status = submission.status if submission else 'not_submitted'
                
                assigned_users.append({
                    'id': user.id,
                    'name': user.get_full_name() or user.email,
                    'email': user.email,
                    'email_status': email_status,
                    'submission_status': submission_status,
                    'is_overdue': is_overdue and not submission,
                    'submitted_at': submission.submitted_at.isoformat() if submission else None,
                    'submission_text': submission.submission_text if submission else None,
                    'submission_file': submission.submission_file.url if submission and submission.submission_file else None,
                    'admin_feedback': submission.admin_feedback if submission else None,
                    'rating': submission.rating if submission else None
                })
            
            # Get email statistics
            email_stats = EmailQueue.objects.filter(related_task_id=task.id).aggregate(
                total=models.Count('id'),
                sent=models.Count('id', filter=models.Q(status='sent')),
                failed=models.Count('id', filter=models.Q(status='failed')),
                pending=models.Count('id', filter=models.Q(status='pending'))
            )
            
            # Get task materials
            materials = [{'id': m.id, 'filename': m.filename, 'url': m.file.url} for m in task.materials.all()]
            
            return Response({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'deadline': task.deadline.isoformat(),
                'status': task.status,
                'task_links': task.task_links,
                'materials': materials,
                'assigned_users': assigned_users,
                'email_stats': email_stats,
                'submission_text': task.submission_text,
                'submission_file': task.submission_file.url if task.submission_file else None,
                'admin_feedback': task.admin_feedback,
                'created_at': task.created_at.isoformat(),
                'is_overdue': timezone.now() > task.deadline
            })
            
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=404)

class SubmissionDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, task_id, user_id):
        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=403)
            
        try:
            task = Task.objects.get(id=task_id)
            user = CustomUser.objects.get(id=user_id)
            submission = TaskSubmission.objects.get(task=task, user=user)
            
            return Response({
                'id': submission.id,
                'task_id': task.id,
                'user_id': user.id,
                'status': submission.status,
                'submission_text': submission.submission_text,
                'submission_file': submission.submission_file.url if submission.submission_file else None,
                'admin_feedback': submission.admin_feedback,
                'rating': submission.rating,
                'submitted_at': submission.submitted_at.isoformat() if submission.submitted_at else None,
                'reviewed_at': submission.reviewed_at.isoformat() if submission.reviewed_at else None,
                'reviewed_by': submission.reviewed_by.get_full_name() if submission.reviewed_by else None
            })
            
        except (Task.DoesNotExist, CustomUser.DoesNotExist, TaskSubmission.DoesNotExist):
            return Response({'error': 'Submission not found'}, status=404)

class ReviewSubmissionAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, task_id, user_id):
        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=403)
            
        try:
            task = Task.objects.get(id=task_id)
            user = CustomUser.objects.get(id=user_id)
            submission = TaskSubmission.objects.get(task=task, user=user)
            
            action = request.data.get('action')  # 'approve' or 'redo'
            feedback = request.data.get('feedback', '')
            rating = request.data.get('rating')
            
            submission.admin_feedback = feedback
            if rating and action == 'approve':
                submission.rating = int(rating)
            submission.reviewed_by = request.user
            submission.reviewed_at = timezone.now()
            
            if action == 'approve':
                submission.status = 'approved'
                notification_title = f'Task Approved: {task.title}'
                notification_message = f'Your task "{task.title}" has been approved.'
                email_subject = f'Task Approved: {task.title}'
                email_message = f'Dear {user.get_full_name() or user.email},\n\nYour task "{task.title}" has been approved.\n\n{"Feedback: " + feedback if feedback else ""}\n\nCongratulations!\n\nBest regards,\nAarambha Foundation Team'
            else:
                submission.status = 'redo_requested'
                notification_title = f'Task Needs Revision: {task.title}'
                notification_message = f'Your task "{task.title}" needs revision. Please check the feedback.'
                email_subject = f'Task Needs Revision: {task.title}'
                email_message = f'Dear {user.get_full_name() or user.email},\n\nYour task "{task.title}" needs revision. Please review the feedback and resubmit.\n\nFeedback: {feedback}\n\nBest regards,\nAarambha Foundation Team'
            
            submission.save()
            
            # Create notification for user
            UserNotification.objects.create(
                user=user,
                title=notification_title,
                message=notification_message + (f' Feedback: {feedback}' if feedback else ''),
                notification_type='task_reviewed'
            )
            
            # Send email to user
            try:
                send_mail(
                    subject=email_subject,
                    message=email_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception as e:
                pass  # Don't fail review if email fails
            
            return Response({'message': 'Submission reviewed successfully'})
        except (Task.DoesNotExist, CustomUser.DoesNotExist, TaskSubmission.DoesNotExist):
            return Response({'error': 'Submission not found'}, status=404)

class EmailStatusAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=403)
            
        from django.db.models import Count
        stats = EmailQueue.objects.aggregate(
            pending=Count('id', filter=models.Q(status='pending')),
            sending=Count('id', filter=models.Q(status='sending')),
            sent=Count('id', filter=models.Q(status='sent')),
            failed=Count('id', filter=models.Q(status='failed'))
        )
        
        recent_emails = EmailQueue.objects.order_by('-created_at')[:10]
        recent_data = []
        for email in recent_emails:
            recent_data.append({
                'recipient': email.recipient.email,
                'subject': email.subject,
                'status': email.status,
                'created_at': email.created_at.isoformat(),
                'sent_at': email.sent_at.isoformat() if email.sent_at else None,
                'error': email.error_message if email.status == 'failed' else None
            })
        
        return Response({
            'stats': stats,
            'recent_emails': recent_data
        })
