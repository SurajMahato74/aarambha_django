from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email, user_field
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from django.contrib.auth import login as django_login
from django.urls import reverse
import uuid

User = get_user_model()

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        """
        Custom login redirect logic to prevent admin users from being redirected
        """
        # Check if there's a 'next' parameter (user was trying to access a protected page)
        next_url = request.GET.get('next') or request.POST.get('next')
        if next_url:
            return next_url
        
        # If user is superuser/admin and no specific page requested, stay on current page
        if hasattr(request.user, 'is_superuser') and request.user.is_superuser:
            # Get referer URL
            referer = request.META.get('HTTP_REFERER')
            if referer and not referer.endswith('/accounts/google/login/'):
                return referer
            
            # Default to home page for admin users
            return '/'
        
        # For regular users, use default behavior
        return super().get_login_redirect_url(request)

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
    
    def get_login_redirect_url(self, request):
        """
        Custom login redirect logic for social login to prevent admin users from being redirected
        """
        # Check if there's a 'next' parameter (user was trying to access a protected page)
        next_url = request.GET.get('next') or request.POST.get('next')
        if next_url:
            return next_url
        
        # If user is superuser/admin and no specific page requested, stay on current page
        if hasattr(request.user, 'is_superuser') and request.user.is_superuser:
            # Get referer URL
            referer = request.META.get('HTTP_REFERER')
            if referer and not referer.endswith('/accounts/google/login/'):
                return referer
            
            # Default to home page for admin users
            return '/'
        
        # For regular users, use default behavior
        return super().get_login_redirect_url(request)
    
    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        """
        Handle authentication errors gracefully
        """
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Social auth error for {provider_id}: {error} - {exception}")
        
        # Redirect to login page with error message
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, 'Authentication failed. Please try again.')
        return redirect('/accounts/login/')