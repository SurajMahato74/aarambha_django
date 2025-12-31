"""
Authentication consistency middleware to prevent anonymous authentication errors
and ensure session synchronization across all login methods
"""
from django.contrib.auth import login as django_login
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import logging

logger = logging.getLogger(__name__)

class AuthConsistencyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check for authentication inconsistencies before processing request
        self.ensure_auth_consistency(request)
        
        response = self.get_response(request)
        
        # Add auth status headers for frontend
        if hasattr(request, 'user') and request.user.is_authenticated:
            response['X-Auth-Status'] = 'authenticated'
            response['X-User-Type'] = getattr(request.user, 'user_type', 'guest')
        else:
            response['X-Auth-Status'] = 'anonymous'
        
        return response

    def ensure_auth_consistency(self, request):
        """
        Ensure Django session and JWT token are consistent
        """
        try:
            # Get Django session user
            django_user = request.user if request.user.is_authenticated else None
            
            # Get JWT token user
            jwt_user = None
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            
            if auth_header.startswith('Bearer '):
                try:
                    jwt_auth = JWTAuthentication()
                    validated_token = jwt_auth.get_validated_token(auth_header.split(' ')[1])
                    jwt_user = jwt_auth.get_user(validated_token)
                except (InvalidToken, TokenError):
                    # Invalid JWT token, ignore
                    pass
            
            # Handle inconsistencies
            if jwt_user and not django_user:
                # JWT user exists but no Django session - create session
                django_login(request, jwt_user, backend='django.contrib.auth.backends.ModelBackend')
                logger.info(f"Synced JWT user {jwt_user.id} to Django session")
                
            elif django_user and jwt_user and django_user.id != jwt_user.id:
                # Different users in session and JWT - prioritize Django session
                logger.warning(f"Auth inconsistency: Django user {django_user.id} vs JWT user {jwt_user.id}")
                # Keep Django session, JWT will be refreshed by frontend
                
        except Exception as e:
            logger.error(f"Auth consistency check failed: {e}")
            # Don't break the request, just log the error

    def process_exception(self, request, exception):
        """
        Handle authentication-related exceptions gracefully
        """
        if 'AnonymousUser' in str(exception) or 'authentication' in str(exception).lower():
            logger.error(f"Authentication error: {exception}")
            
            # For API requests, return JSON error
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': 'Authentication required',
                    'detail': 'Please log in to access this resource'
                }, status=401)
        
        return None