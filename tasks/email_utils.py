from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import EmailQueue
import logging

logger = logging.getLogger(__name__)

def queue_email(recipient, subject, message, email_type, task_id=None):
    """Queue an email for background processing"""
    EmailQueue.objects.create(
        recipient=recipient,
        subject=subject,
        message=message,
        email_type=email_type,
        related_task_id=task_id
    )

def process_email_queue():
    """Process pending emails in queue"""
    pending_emails = EmailQueue.objects.filter(status='pending')[:10]  # Process 10 at a time
    
    for email in pending_emails:
        try:
            email.status = 'sending'
            email.save()
            
            send_mail(
                subject=email.subject,
                message=email.message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email.recipient.email],
                fail_silently=False,
            )
            
            email.status = 'sent'
            email.sent_at = timezone.now()
            email.save()
            
            logger.info(f"Email sent to {email.recipient.email}: {email.subject}")
            
        except Exception as e:
            email.status = 'failed'
            email.error_message = str(e)
            email.save()
            
            logger.error(f"Failed to send email to {email.recipient.email}: {str(e)}")

def create_task_assignment_email(user, task):
    """Create personalized task assignment email"""
    subject = f'🎯 New Task Assigned: {task.title}'
    message = f'''Dear {user.first_name or user.email},

You have been assigned a new task:

📋 Task: {task.title}
📝 Description: {task.description}
⏰ Deadline: {task.deadline.strftime("%B %d, %Y at %I:%M %p")}

Please log in to your dashboard to view the complete task details and any attached materials.

Dashboard: {settings.SITE_URL}/guest/profile/

Best regards,
Aarambha Foundation Team'''
    
    return subject, message