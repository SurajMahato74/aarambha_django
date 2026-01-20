from django.shortcuts import redirect
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
import json

class GoogleAuthSyncMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Check if user is authenticated and this is the profile page
        if (request.user.is_authenticated and 
            request.path == '/guest/profile/' and
            response.status_code == 200):
            
            # Generate JWT tokens for consistency
            refresh = RefreshToken.for_user(request.user)
            user_data = {
                'id': request.user.id,
                'email': request.user.email,
                'user_type': getattr(request.user, 'user_type', 'guest'),
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'is_superuser': request.user.is_superuser,
                'is_approved': getattr(request.user, 'is_approved', False),
                'branch': request.user.branch.id if hasattr(request.user, 'branch') and request.user.branch else None,
            }
            
            # Add script to sync localStorage with Django session
            access_token = str(refresh.access_token).replace("'", "\\'")
            refresh_token = str(refresh).replace("'", "\\'")
            script = f"""
            <script>
                console.log('Syncing Google auth tokens...');
                localStorage.setItem('access_token', '{access_token}');
                localStorage.setItem('refresh_token', '{refresh_token}');
                console.log('Google auth tokens synced successfully');
            </script>
            """
            
            # Insert script before closing body tag
            if b'</body>' in response.content:
                response.content = response.content.replace(
                    b'</body>', 
                    script.encode('utf-8') + b'</body>'
                )
        
        return response