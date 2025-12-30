# applications/models.py
from django.db import models
from users.models import CustomUser

class Application(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
        ('approved', 'Approved'),
    )
    TYPE_CHOICES = (('member', 'Member'), ('volunteer', 'Volunteer'))
    REJECTION_TYPE_CHOICES = (
        ('correction', 'Correction Required'),
        ('final', 'Final Rejection'),
    )


    # Personal Information
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='applications')
    full_name = models.CharField(max_length=200)
    date_of_birth = models.DateField(null=True, blank=True)
    temporary_address = models.TextField(blank=True)
    permanent_address = models.TextField(blank=True)
    phone = models.CharField(max_length=15)
    country = models.CharField(max_length=100, default='Nepal')
    district = models.CharField(max_length=100, blank=True)
    profession = models.TextField(blank=True)
    social_link = models.URLField(blank=True)
    
    # Application Questions
    why_join = models.TextField(blank=True)
    self_definition = models.TextField(blank=True)
    hobbies_interests = models.TextField(blank=True)
    ideas = models.TextField(blank=True)
    skills = models.JSONField(default=list)
    time_commitment = models.CharField(max_length=50, blank=True)
    other_organizations = models.TextField(blank=True)
    
    # Documents
    citizenship_front = models.FileField(upload_to='applications/citizenship/', null=True, blank=True)
    citizenship_back = models.FileField(upload_to='applications/citizenship/', null=True, blank=True)
    photo = models.ImageField(upload_to='applications/photos/', null=True, blank=True)
    
    # Meta
    application_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    is_upgrade = models.BooleanField(default=False)  # Track if this is an upgrade application
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    interview_datetime = models.DateTimeField(null=True, blank=True)
    interview_link = models.URLField(blank=True)
    interview_description = models.TextField(blank=True)
    interview_attended = models.BooleanField(null=True, blank=True)
    interview_acknowledged = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    branch = models.ForeignKey('branches.Branch', null=True, blank=True, on_delete=models.SET_NULL)
    created_user = models.OneToOneField(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_from_application')
    
    # Payment fields
    payment_required = models.BooleanField(default=False)
    payment_completed = models.BooleanField(default=False)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    khalti_transaction_id = models.CharField(max_length=100, blank=True)
    khalti_payment_token = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)

    
    rejection_type = models.CharField(
        max_length=20,
        choices=REJECTION_TYPE_CHOICES,
        blank=True,
        null=True
    )
    
    def __str__(self):
        return f"{self.full_name} - {self.application_type}"