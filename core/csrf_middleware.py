"""
CSRF exemption middleware for API endpoints
"""
from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.csrf import csrf_exempt

class CSRFExemptAPIMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Exempt API endpoints from CSRF protection
        if request.path.startswith('/api/'):
            return csrf_exempt(view_func)(request, *view_args, **view_kwargs)
        return None