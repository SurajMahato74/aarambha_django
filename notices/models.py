from django.db import models
from users.models import CustomUser
from applications.models import Application

class UserNotification(models.Model):
    NOTIFICATION_TYPES = (
        ('application_submitted', 'Application Submitted'),
        ('application_resubmitted', 'Application Resubmitted'),
        ('application_updated', 'Application Updated'),
        ('application_approved', 'Application Approved'),
        ('application_rejected', 'Application Rejected'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('interview_rescheduled', 'Interview Rescheduled'),
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
