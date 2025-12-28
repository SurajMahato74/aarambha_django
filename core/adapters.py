from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email, user_field
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
import uuid

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed.
        """
        # Check if user already exists with this email
        email = sociallogin.account.extra_data.get('email')
        if email:
            try:
                existing_user = User.objects.get(email=email)
                # Connect this social account to existing user
                sociallogin.connect(request, existing_user)
            except User.DoesNotExist:
                pass
    
    def save_user(self, request, sociallogin, form=None):
        user = sociallogin.user
        user_email(user, sociallogin.account.extra_data.get('email', ''))
        user_field(user, 'first_name', sociallogin.account.extra_data.get('given_name', ''))
        user_field(user, 'last_name', sociallogin.account.extra_data.get('family_name', ''))
        
        # Generate unique username using email or UUID
        email = sociallogin.account.extra_data.get('email', '')
        if email:
            base_username = email.split('@')[0]
        else:
            base_username = 'user'
        
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        
        user.username = username
        user.user_type = 'guest'  # Always set to guest for Google login
        user.save()
        return user