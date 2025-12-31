"""
Unified authentication utilities to ensure consistent session management
across all login methods (Google, Password, Email OTP)
"""
from django.contrib.auth import login as django_login
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
import json


def create_unified_auth_response(request, user):
    """
    Create a unified authentication response that works with both
    Django sessions and JWT tokens for consistent authentication
    """
    # Create Django session with backend specified
    django_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    # User data for frontend
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'user_type': user.user_type,
        'is_superuser': user.is_superuser,
        'is_approved': user.is_approved,
        'branch': user.branch.id if user.branch else None,
    }
    
    return {
        'success': True,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': user_data,
        'session_created': True
    }


def logout_user_completely(request):
    """
    Completely logout user from both Django session and JWT
    """
    from django.contrib.auth import logout as django_logout
    
    # Clear Django session
    django_logout(request)
    
    # Clear session data
    request.session.flush()
    
    return True


def check_auth_consistency(request):
    """
    Check if Django session and JWT token are consistent
    """
    django_user = request.user if request.user.is_authenticated else None
    
    # Get JWT token from headers
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    jwt_user = None
    
    if auth_header.startswith('Bearer '):
        try:
            from rest_framework_simplejwt.authentication import JWTAuthentication
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(auth_header.split(' ')[1])
            jwt_user = jwt_auth.get_user(validated_token)
        except:
            pass
    
    # Check consistency
    if django_user and jwt_user:
        return django_user.id == jwt_user.id
    elif django_user or jwt_user:
        return False  # One is authenticated, other is not
    else:
        return True  # Both are None/unauthenticated


def sync_auth_state(request, user):
    """
    Synchronize authentication state between Django session and JWT
    """
    # Ensure Django session is created
    if not request.user.is_authenticated or request.user.id != user.id:
        django_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    
    # Generate fresh JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'session_synced': True
    }