from django.shortcuts import redirect
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
import json

class GoogleAuthSyncMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Check if user just logged in via Google and is being redirected to profile
        if (request.user.is_authenticated and 
            request.path == '/guest/profile/' and 
            'google' in request.session.get('socialaccount_sociallogin', {}).get('account', {}).get('provider', '')):
            
            # Generate JWT tokens for the user
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
            
            # Add JavaScript to set localStorage and ensure session consistency
            user_json = json.dumps(user_data)
            script = f"""
            <script>
                // Clear any existing auth data first
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                localStorage.removeItem('user');
                
                // Set new auth data
                localStorage.setItem('access_token', '{str(refresh.access_token)}');
                localStorage.setItem('refresh_token', '{str(refresh)}');
                localStorage.setItem('user', JSON.stringify({user_json}));
                
                // Update navbar auth state
                if (typeof updateNavbarAuth === 'function') {{
                    updateNavbarAuth();
                }}
                
                console.log('Google auth synced to localStorage and session');
                
                // Set flag for success message
                localStorage.setItem('justLoggedIn', 'true');
            </script>
            """
            
            # Insert script before closing body tag
            if b'</body>' in response.content:
                response.content = response.content.replace(
                    b'</body>', 
                    script.encode('utf-8') + b'</body>'
                )
        
        return response