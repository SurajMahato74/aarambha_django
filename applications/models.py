from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

User = get_user_model()

class Application(models.Model):
    APPLICATION_TYPES = [
        ('volunteer', 'Volunteer'),
        ('member', 'Member'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('interview_scheduled', 'Interview Scheduled'),
    ]
    
    REJECTION_TYPES = [
        ('temporary', 'Temporary'),
        ('permanent', 'Permanent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    application_type = models.CharField(max_length=20, choices=APPLICATION_TYPES)
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Nepal')
    district = models.CharField(max_length=100)
    temporary_address = models.TextField()
    permanent_address = models.TextField()
    profession = models.CharField(max_length=255)
    social_link = models.URLField(blank=True, null=True)
    why_join = models.TextField()
    self_definition = models.TextField()
    ideas = models.TextField()
    skills = models.TextField()
    time_commitment = models.CharField(max_length=255)
    other_organizations = models.TextField(blank=True, null=True)
    citizenship_front = models.ImageField(upload_to='applications/citizenship/', blank=True, null=True)
    citizenship_back = models.ImageField(upload_to='applications/citizenship/', blank=True, null=True)
    photo = models.ImageField(upload_to='applications/photos/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_upgrade = models.BooleanField(default=False)
    
    # Interview fields
    interview_datetime = models.DateTimeField(blank=True, null=True)
    interview_link = models.URLField(blank=True, null=True)
    interview_description = models.TextField(blank=True, null=True)
    interview_acknowledged = models.BooleanField(default=False)
    interview_attended = models.BooleanField(default=False)
    
    # Rejection fields
    rejection_reason = models.TextField(blank=True, null=True)
    rejection_type = models.CharField(max_length=20, choices=REJECTION_TYPES, blank=True, null=True)
    
    # Payment fields for member applications
    payment_required = models.BooleanField(default=False)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1000.00'))
    payment_completed = models.BooleanField(default=False)
    payment_date = models.DateTimeField(blank=True, null=True)
    khalti_payment_token = models.CharField(max_length=255, blank=True, null=True)
    khalti_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.full_name} - {self.application_type} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Don't automatically set payment_required for member applications
        # Payment will be required only after approval
        super().save(*args, **kwargs)

class ChildSponsorship(models.Model):
    SPONSORSHIP_TYPES = [
        ('Full Sponsorship', 'Full Sponsorship'),
        ('Partial Sponsorship', 'Partial Sponsorship'),
        ('One-time Donation', 'One-time Donation'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    PAYMENT_METHODS = [
        ('khalti', 'Khalti'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
    ]
    
    UPDATE_FREQUENCIES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    COMMUNICATION_METHODS = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('whatsapp', 'WhatsApp'),
        ('letter', 'Letter'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sponsorships')
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Nepal')
    city = models.CharField(max_length=100)
    address = models.TextField()
    occupation = models.CharField(max_length=255, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    sponsorship_type = models.CharField(max_length=50, choices=SPONSORSHIP_TYPES)
    child_gender = models.CharField(max_length=20, blank=True)
    child_age = models.CharField(max_length=20, blank=True)
    special_requests = models.TextField(blank=True)
    update_frequency = models.CharField(max_length=20, choices=UPDATE_FREQUENCIES)
    comm_method = models.JSONField(default=list)
    message = models.TextField(blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_frequency = models.CharField(max_length=20, default='Monthly')
    tax_deductible = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    can_reapply = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.full_name} - {self.sponsorship_type} ({self.status})"

class Child(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('pending_assignment', 'Pending Assignment'),
        ('sponsored', 'Sponsored'),
        ('graduated', 'Graduated'),
        ('inactive', 'Inactive'),
    ]
    
    SPONSORSHIP_TYPES = [
        ('Full Sponsorship', 'Full Sponsorship'),
        ('Partial Sponsorship', 'Partial Sponsorship'),
        ('Educational Support', 'Educational Support'),
    ]
    
    FREQUENCIES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    # Basic Information
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    country = models.CharField(max_length=100, default='Nepal')
    district = models.CharField(max_length=100)
    village = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    
    # Family Information
    father_name = models.CharField(max_length=255, blank=True)
    father_occupation = models.CharField(max_length=255, blank=True)
    father_alive = models.BooleanField(default=True)
    mother_name = models.CharField(max_length=255, blank=True)
    mother_occupation = models.CharField(max_length=255, blank=True)
    mother_alive = models.BooleanField(default=True)
    guardian_name = models.CharField(max_length=255, blank=True)
    guardian_relationship = models.CharField(max_length=100, blank=True)
    guardian_occupation = models.CharField(max_length=255, blank=True)
    family_situation = models.TextField(blank=True)
    family_income = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Education Information
    school_name = models.CharField(max_length=255, blank=True)
    grade_level = models.CharField(max_length=50, blank=True)
    educational_needs = models.TextField(blank=True)
    
    # Health Information
    health_status = models.TextField(blank=True)
    special_needs = models.TextField(blank=True)
    
    # Personal Information
    interests_hobbies = models.TextField(blank=True)
    personality_description = models.TextField(blank=True)
    dreams_aspirations = models.TextField(blank=True)
    
    # Sponsorship Information
    monthly_sponsorship_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    preferred_sponsorship_type = models.JSONField(default=list)
    preferred_frequency = models.JSONField(default=list)
    
    # Story and Additional Info
    story = models.TextField(blank=True)
    urgent_needs = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    # Status and Sponsorship
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    current_sponsor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sponsored_children')
    sponsorship_start_date = models.DateField(blank=True, null=True)
    
    # Media
    photo = models.ImageField(upload_to='children/photos/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.full_name} ({self.district})"
    
    def get_age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

class ChildAssignment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='assignments')
    sponsor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='child_assignments')
    sponsorship = models.ForeignKey(ChildSponsorship, on_delete=models.CASCADE, related_name='assignments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ['child', 'sponsor', 'sponsorship']
    
    def __str__(self):
        return f"{self.child.full_name} -> {self.sponsor.get_full_name() or self.sponsor.email} ({self.status})"

class PaymentInstallment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='payment_installments')
    sponsor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_installments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    installment_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    khalti_payment_token = models.CharField(max_length=255, blank=True, null=True)
    khalti_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['child', 'sponsor', 'installment_number']
    
    def __str__(self):
        return f"{self.child.full_name} - Installment #{self.installment_number} - Rs. {self.amount}"

class OneRupeeCampaign(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rupee_campaigns')
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Nepal')
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    occupation = models.CharField(max_length=255, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    
    # Campaign details
    annual_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('365.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateField(auto_now_add=True)
    next_payment_date = models.DateField(null=True, blank=True)
    
    # Payment tracking
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    payments_count = models.PositiveIntegerField(default=0)
    last_payment_date = models.DateField(blank=True, null=True)
    
    # Khalti payment info
    khalti_payment_token = models.CharField(max_length=255, blank=True, null=True)
    khalti_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.full_name} - One Rupee Campaign ({self.status})"

class CampaignPayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    campaign = models.ForeignKey(OneRupeeCampaign, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_year = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    khalti_payment_token = models.CharField(max_length=255, blank=True, null=True)
    khalti_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['campaign', 'payment_year']
    
    def __str__(self):
        return f"{self.campaign.full_name} - Year {self.payment_year} - Rs. {self.amount}"

class BirthdayCampaign(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='birthday_campaigns')
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    birthday_date = models.DateField()
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    title = models.CharField(max_length=255)
    description = models.TextField()
    profile_photo = models.ImageField(upload_to='birthday_campaigns/profiles/', blank=True, null=True)
    photo = models.ImageField(upload_to='birthday_campaigns/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    donors_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.full_name}'s Birthday Campaign - {self.title}"
    
    def get_progress_percentage(self):
        if self.target_amount > 0:
            return min(100, (float(self.current_amount) / float(self.target_amount)) * 100)
        return 0

class BirthdayDonationRecord(models.Model):
    campaign = models.ForeignKey(BirthdayCampaign, on_delete=models.CASCADE, related_name='donation_records')
    participant_name = models.CharField(max_length=255)
    donation_amount = models.DecimalField(max_digits=10, decimal_places=2)
    donation_description = models.TextField()
    donation_photo = models.ImageField(upload_to='birthday_donations/', blank=True, null=True)
    donation_date = models.DateField()
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='added_donation_records', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.participant_name} - Rs. {self.donation_amount} ({self.campaign.title})"

class BirthdayDonation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    campaign = models.ForeignKey(BirthdayCampaign, on_delete=models.CASCADE, related_name='donations')
    donor_name = models.CharField(max_length=255)
    donor_email = models.EmailField()
    donor_phone = models.CharField(max_length=20, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    khalti_payment_token = models.CharField(max_length=255, blank=True, null=True)
    khalti_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.donor_name} - Rs. {self.amount} to {self.campaign.title}"
