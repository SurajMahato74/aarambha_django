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

    def get_display_name(self):
        """Get the best available name for the user"""
        # Try user model first
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        
        # Try application table
        try:
            from applications.models import Application
            application = Application.objects.filter(user=self).first()
            if application and application.full_name:
                return application.full_name
        except:
            pass
        
        # Try sponsorship table
        try:
            from applications.models import ChildSponsorship
            sponsorship = ChildSponsorship.objects.filter(user=self).first()
            if sponsorship and sponsorship.full_name:
                return sponsorship.full_name
        except:
            pass
        
        # Try one rupee campaign
        try:
            from applications.models import OneRupeeCampaign
            campaign = OneRupeeCampaign.objects.filter(user=self).first()
            if campaign and campaign.full_name:
                return campaign.full_name
        except:
            pass
        
        # Try birthday campaign
        try:
            from applications.models import BirthdayCampaign
            campaign = BirthdayCampaign.objects.filter(user=self).first()
            if campaign and campaign.full_name:
                return campaign.full_name
        except:
            pass
        
        # Fallback to username or email
        return self.username or self.email

    def get_display_phone(self):
        """Get the best available phone number for the user"""
        # Try user model first
        if self.phone:
            return self.phone
        
        # Try application table
        try:
            from applications.models import Application
            application = Application.objects.filter(user=self).first()
            if application and application.phone:
                return application.phone
        except:
            pass
        
        # Try sponsorship table
        try:
            from applications.models import ChildSponsorship
            sponsorship = ChildSponsorship.objects.filter(user=self).first()
            if sponsorship and sponsorship.phone:
                return sponsorship.phone
        except:
            pass
        
        # Try one rupee campaign
        try:
            from applications.models import OneRupeeCampaign
            campaign = OneRupeeCampaign.objects.filter(user=self).first()
            if campaign and campaign.phone:
                return campaign.phone
        except:
            pass
        
        # Try birthday campaign
        try:
            from applications.models import BirthdayCampaign
            campaign = BirthdayCampaign.objects.filter(user=self).first()
            if campaign and campaign.phone:
                return campaign.phone
        except:
            pass
        
        # No phone found
        return ""

    def sync_name_and_phone_from_application(self):
        """Sync name and phone from approved application to user model"""
        try:
            from applications.models import Application
            # Get the most recent approved application
            application = Application.objects.filter(
                user=self, 
                status='approved'
            ).order_by('-applied_at').first()
            
            if application:
                # Update user name if not set
                if not self.first_name and not self.last_name and application.full_name:
                    # Split full name into first and last
                    name_parts = application.full_name.split(' ', 1)
                    self.first_name = name_parts[0]
                    if len(name_parts) > 1:
                        self.last_name = name_parts[1]
                
                # Update phone if not set
                if not self.phone and application.phone:
                    self.phone = application.phone
                
                self.save(update_fields=['first_name', 'last_name', 'phone'])
        except:
            pass

    def sync_name_and_phone_from_sponsorship(self):
        """Sync name and phone from approved sponsorship to user model"""
        try:
            from applications.models import ChildSponsorship
            # Get the most recent approved sponsorship
            sponsorship = ChildSponsorship.objects.filter(
                user=self, 
                status='approved'
            ).order_by('-created_at').first()
            
            if sponsorship:
                # Update user name if not set
                if not self.first_name and not self.last_name and sponsorship.full_name:
                    name_parts = sponsorship.full_name.split(' ', 1)
                    self.first_name = name_parts[0]
                    if len(name_parts) > 1:
                        self.last_name = name_parts[1]
                
                # Update phone if not set
                if not self.phone and sponsorship.phone:
                    self.phone = sponsorship.phone
                
                self.save(update_fields=['first_name', 'last_name', 'phone'])
        except:
            pass
