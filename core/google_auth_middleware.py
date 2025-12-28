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
            }
            
            # Add JavaScript to set localStorage
            script = f"""
            <script>
                localStorage.setItem('access_token', '{str(refresh.access_token)}');
                localStorage.setItem('refresh_token', '{str(refresh)}');
                localStorage.setItem('user', '{json.dumps(user_data).replace("'", "\\'")}');
                console.log('Google auth synced to localStorage');
            </script>
            """
            
            # Insert script before closing body tag
            if b'</body>' in response.content:
                response.content = response.content.replace(
                    b'</body>', 
                    script.encode('utf-8') + b'</body>'
                )
        
        return response