"""
Custom authentication classes that bypass CSRF for API endpoints
"""
from rest_framework.authentication import SessionAuthentication

class CSRFExemptSessionAuthentication(SessionAuthentication):
    """
    Session authentication that bypasses CSRF checks
    """
    def enforce_csrf(self, request):
        return  # Skip CSRF check