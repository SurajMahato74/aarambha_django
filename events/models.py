from django.db import models
from django.contrib.auth import get_user_model
from branches.models import Branch

User = get_user_model()

class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('meeting', 'Meeting'),
        ('training', 'Training'),
        ('workshop', 'Workshop'),
        ('conference', 'Conference'),
        ('social', 'Social Event'),
        ('other', 'Other'),
    ]
    
    VENUE_TYPE_CHOICES = [
        ('physical', 'Physical Location'),
        ('online', 'Online (Zoom/Meet)'),
        ('hybrid', 'Hybrid'),
    ]
    
    ASSIGNMENT_MODE_CHOICES = [
        ('all', 'All Users'),
        ('individual', 'Individual Users'),
        ('branch', 'By Branch'),
        ('branch_individual', 'Branch + Individual'),
    ]
    
    USER_TYPE_CHOICES = [
        ('member', 'Members Only'),
        ('volunteer', 'Volunteers Only'),
        ('both', 'Members & Volunteers'),
    ]
    
    title = models.CharField(max_length=300)
    description = models.TextField()
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='meeting')
    venue_type = models.CharField(max_length=20, choices=VENUE_TYPE_CHOICES, default='physical')
    
    # Physical venue details
    venue_name = models.CharField(max_length=200, blank=True, null=True)
    venue_address = models.TextField(blank=True, null=True)
    
    # Online venue details
    meeting_link = models.URLField(blank=True, null=True)
    meeting_id = models.CharField(max_length=100, blank=True, null=True)
    meeting_password = models.CharField(max_length=100, blank=True, null=True)
    
    # Contact person details
    contact_person = models.CharField(max_length=200, blank=True, null=True, help_text="Contact person name")
    contact_phone = models.CharField(max_length=20, blank=True, null=True, help_text="Contact person phone number")
    contact_email = models.EmailField(blank=True, null=True, help_text="Contact person email")
    
    # Event timing
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    
    # Assignment settings
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='both')
    assignment_mode = models.CharField(max_length=20, choices=ASSIGNMENT_MODE_CHOICES, default='all')
    assigned_to = models.ManyToManyField(User, related_name='assigned_events', blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Participation settings
    requires_application = models.BooleanField(default=False, help_text="Users need to apply to participate")
    max_participants = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum number of participants")
    
    # Event management
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-start_datetime']
    
    def __str__(self):
        return self.title

class EventParticipation(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('attended', 'Attended'),
        ('absent', 'Absent'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_participations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    application_message = models.TextField(blank=True, help_text="User's application message")
    admin_notes = models.TextField(blank=True, help_text="Admin notes about this participation")
    
    # Attendance tracking
    attended = models.BooleanField(default=False)
    attendance_marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='marked_attendances')
    attendance_marked_at = models.DateTimeField(null=True, blank=True)
    
    # Review system
    review = models.TextField(blank=True, help_text="User's review of the event")
    rating = models.PositiveIntegerField(null=True, blank=True, help_text="Rating out of 5")
    
    # Certificate
    certificate_id = models.CharField(max_length=20, blank=True, null=True, help_text="Unique certificate ID")
    
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['event', 'user']
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.event.title} - {self.user.get_full_name() or self.user.email}"

class EventCertificate(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='certificates')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_certificates')
    participation = models.OneToOneField(EventParticipation, on_delete=models.CASCADE, related_name='certificate')
    
    certificate_template = models.TextField(help_text="Certificate template with placeholders")
    certificate_file = models.FileField(upload_to='event_certificates/', blank=True, null=True)
    
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issued_certificates')
    issued_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['event', 'user']
    
    def __str__(self):
        return f"Certificate - {self.event.title} - {self.user.get_full_name() or self.user.email}"