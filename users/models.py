from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .otp_models import EmailOTP

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('branchadmin', 'Branch Admin'),
        ('member', 'Member'),
        ('volunteer', 'Volunteer'),
        ('sponsor', 'Sponsor'),
        ('guest', 'Guest'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='volunteer')
    branch = models.ForeignKey('branches.Branch', null=True, blank=True, on_delete=models.SET_NULL)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    membership_paid = models.BooleanField(default=False)

    def is_superadmin(self): return self.user_type == 'superadmin'
    def is_branchadmin(self): return self.user_type == 'branchadmin'
    def is_member(self): return self.user_type == 'member'
    def is_volunteer(self): return self.user_type == 'volunteer'
    def is_sponsor(self): return self.user_type == 'sponsor'