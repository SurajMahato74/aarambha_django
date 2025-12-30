from django.db import models
from users.models import CustomUser
from applications.models import Application

class Notice(models.Model):
    VISIBILITY_CHOICES = [
        ('member', 'Members Only'),
        ('volunteer', 'Volunteers Only'),
        ('both', 'Members & Volunteers'),
    ]
    
    ASSIGNMENT_MODE_CHOICES = [
        ('all', 'All Users'),
        ('individual', 'Individual Users'),
        ('branch', 'By Branch'),
        ('branch_individual', 'Branch + Individual'),
    ]
    
    title = models.CharField(max_length=300)
    content = models.TextField()
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='both')
    assignment_mode = models.CharField(max_length=20, choices=ASSIGNMENT_MODE_CHOICES, default='all')
    assigned_to = models.ManyToManyField('users.CustomUser', related_name='assigned_notices', blank=True)
    branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    attachment = models.FileField(upload_to='notice_attachments/', blank=True, null=True)
    created_by = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='created_notices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class UserNotification(models.Model):
    NOTIFICATION_TYPES = (
        ('application_submitted', 'Application Submitted'),
        ('application_resubmitted', 'Application Resubmitted'),
        ('application_updated', 'Application Updated'),
        ('application_approved', 'Application Approved'),
        ('application_rejected', 'Application Rejected'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('interview_rescheduled', 'Interview Rescheduled'),
        ('task_assigned', 'Task Assigned'),
        ('task_submitted', 'Task Submitted'),
        ('task_reviewed', 'Task Reviewed'),
        ('event_applied', 'Event Application Submitted'),
        ('event_approved', 'Event Application Approved'),
        ('event_rejected', 'Event Application Rejected'),
        ('event_attended', 'Event Attendance Marked'),
        ('general', 'General'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_application = models.ForeignKey(Application, null=True, blank=True, on_delete=models.SET_NULL)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"
