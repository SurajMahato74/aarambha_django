# Quick test for authentication system
from django.test import Client
from django.contrib.auth import get_user_model
from users.otp_models import EmailOTP

User = get_user_model()
client = Client()

# Test 1: Create user and password login
print("Testing password login...")
user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
response = client.post('/api/users/login/', {'username': 'testuser', 'password': 'testpass123'}, content_type='application/json')
print(f"Password login: {response.status_code} - {response.json() if response.status_code == 200 else 'Failed'}")

# Test 2: Auth status
response = client.get('/api/users/auth-status/')
print(f"Auth status: {response.status_code} - {response.json() if response.status_code == 200 else 'Failed'}")

# Test 3: OTP login
print("Testing OTP login...")
response = client.post('/api/users/send-otp/', {'email': 'otp@test.com'}, content_type='application/json')
if response.status_code == 200:
    otp = EmailOTP.objects.filter(email='otp@test.com').latest('created_at').otp
    response = client.post('/api/users/verify-otp/', {'email': 'otp@test.com', 'otp': otp}, content_type='application/json')
    print(f"OTP login: {response.status_code} - {response.json() if response.status_code == 200 else 'Failed'}")

print("Test completed!")