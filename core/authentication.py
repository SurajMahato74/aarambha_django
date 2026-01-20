from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser

class FlexibleJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that gracefully handles invalid tokens
    and falls back to session authentication
    """
    
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None
            
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
            
        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except (InvalidToken, TokenError):
            # Invalid JWT token, return None to allow other authentication methods
            return None

class UnifiedAuthentication:
    """
    Combines JWT and Session authentication with graceful fallback
    """
    
    def __init__(self):
        self.jwt_auth = FlexibleJWTAuthentication()
        self.session_auth = SessionAuthentication()
    
    def authenticate(self, request):
        # Try JWT first
        jwt_result = self.jwt_auth.authenticate(request)
        if jwt_result is not None:
            return jwt_result
            
        # Fall back to session authentication
        session_result = self.session_auth.authenticate(request)
        if session_result is not None:
            return session_result
            
        return None