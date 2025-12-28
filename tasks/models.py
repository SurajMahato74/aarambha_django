from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Task(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('redo_requested', 'Redo Requested'),
    ]
    
    USER_TYPE_CHOICES = [
        ('member', 'Members Only'),
        ('volunteer', 'Volunteers Only'),
        ('both', 'Members & Volunteers'),
    ]
    
    title = models.CharField(max_length=300)
    description = models.TextField()
    assign_to_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='both')
    assigned_to = models.ManyToManyField(User, related_name='assigned_tasks')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    
    # Task links
    task_links = models.TextField(blank=True, help_text="Helpful links (one per line)")
    
    # Submission fields (deprecated - use TaskSubmission model)
    submission_text = models.TextField(blank=True, help_text="Work description/notes")
    submission_file = models.FileField(upload_to='task_submissions/', blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    # Review fields
    admin_feedback = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_tasks')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class TaskSubmission(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('redo_requested', 'Redo Requested'),
    ]
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_submissions')
    submission_text = models.TextField(blank=True, help_text="Work description/notes")
    submission_file = models.FileField(upload_to='task_submissions/', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    admin_feedback = models.TextField(blank=True)
    rating = models.IntegerField(null=True, blank=True, help_text="Rating out of 10")
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['task', 'user']
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.task.title} - {self.user.get_full_name() or self.user.email}"

class TaskMaterial(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='materials')
    file = models.FileField(upload_to='task_materials/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.task.title} - {self.filename}"

class EmailQueue(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    email_type = models.CharField(max_length=50)
    related_task_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.recipient.email} - {self.subject} ({self.status})"