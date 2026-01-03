"""
Test script to verify unified authentication system
Run this with: python manage.py shell < test_auth.py
"""

from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from users.models import CustomUser
from users.otp_models import EmailOTP
import json

User = get_user_model()

def test_unified_auth():
    print("Testing Unified Authentication System...")
    
    # Create test client
    client = Client()
    
    # Test 1: Password Login
    print("\n1. Testing Password Login...")
    
    # Create test user
    test_user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        user_type='guest'
    )
    
    # Test password login
    response = client.post('/api/users/login/', {
        'username': 'testuser',
        'password': 'testpass123'
    }, content_type='application/json')
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Password login successful: {data.get('success', False)}")
        print(f"✓ Session created: {data.get('session_created', False)}")
        print(f"✓ User type: {data.get('user', {}).get('user_type')}")
    else:
        print(f"✗ Password login failed: {response.status_code}")
    
    # Test 2: OTP Login
    print("\n2. Testing OTP Login...")
    
    # Send OTP
    response = client.post('/api/users/send-otp/', {
        'email': 'otp@example.com'
    }, content_type='application/json')
    
    if response.status_code == 200:
        print("✓ OTP sent successfully")
        
        # Get the OTP from database
        otp_obj = EmailOTP.objects.filter(email='otp@example.com').latest('created_at')
        
        # Verify OTP
        response = client.post('/api/users/verify-otp/', {
            'email': 'otp@example.com',
            'otp': otp_obj.otp
        }, content_type='application/json')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ OTP login successful: {data.get('success', False)}")
            print(f"✓ Session created: {data.get('session_created', False)}")
        else:
            print(f"✗ OTP verification failed: {response.status_code}")
    else:
        print(f"✗ OTP send failed: {response.status_code}")
    
    # Test 3: Auth Status Check
    print("\n3. Testing Auth Status...")
    
    response = client.get('/api/users/auth-status/')
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Auth status check: {data.get('authenticated', False)}")
        print(f"✓ Session active: {data.get('session_active', False)}")
    else:
        print(f"✗ Auth status check failed: {response.status_code}")
    
    # Test 4: Logout
    print("\n4. Testing Logout...")
    
    # First login
    client.post('/api/users/login/', {
        'username': 'testuser',
        'password': 'testpass123'
    }, content_type='application/json')
    
    # Then logout
    response = client.post('/api/users/logout/')
    if response.status_code == 200:
        print("✓ Logout successful")
        
        # Check auth status after logout
        response = client.get('/api/users/auth-status/')
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Auth status after logout: {not data.get('authenticated', True)}")
    else:
        print(f"✗ Logout failed: {response.status_code}")
    
    print("\n✓ Authentication system test completed!")

if __name__ == "__main__":
    test_unified_auth()