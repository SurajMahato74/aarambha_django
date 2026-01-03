from django.db import models
from users.models import CustomUser

class ChildSponsorship(models.Model):
    SPONSORSHIP_TYPE_CHOICES = (
        ('Full Sponsorship', 'Full Sponsorship'),
        ('Partial Sponsorship', 'Partial Sponsorship'),
        ('One-time Donation', 'One-time Donation'),
    )
    
    UPDATE_FREQUENCY_CHOICES = (
        ('Quarterly', 'Quarterly'),
        ('Biannually', 'Biannually'),
        ('Annually', 'Annually'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('Bank Transfer', 'Bank Transfer'),
        ('Online Payment', 'Online Payment'),
        ('Cheque', 'Cheque'),
    )
    
    PAYMENT_FREQUENCY_CHOICES = (
        ('One-time', 'One-time'),
        ('Monthly', 'Monthly'),
        ('Quarterly', 'Quarterly'),
        ('Annually', 'Annually'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    )
    
    # User Information
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sponsorships')
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Nepal')
    city = models.CharField(max_length=100)
    address = models.TextField()
    occupation = models.CharField(max_length=200, blank=True)
    organization = models.CharField(max_length=200, blank=True)
    
    # Sponsorship Preferences
    sponsorship_type = models.CharField(max_length=50, choices=SPONSORSHIP_TYPE_CHOICES)
    child_gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], blank=True)
    child_age = models.CharField(max_length=10, choices=[('5-8', '5-8 years'), ('9-12', '9-12 years'), ('13-16', '13-16 years')], blank=True)
    special_requests = models.TextField(blank=True)
    
    # Communication Preferences
    update_frequency = models.CharField(max_length=20, choices=UPDATE_FREQUENCY_CHOICES)
    comm_method = models.JSONField(default=list)  # Store multiple communication methods
    message = models.TextField(blank=True)
    
    # Payment Information
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_frequency = models.CharField(max_length=20, choices=PAYMENT_FREQUENCY_CHOICES, default='One-time')
    tax_deductible = models.BooleanField(default=True)
    
    # Status and Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.full_name} - {self.sponsorship_type}"
    
    class Meta:
        ordering = ['-created_at']