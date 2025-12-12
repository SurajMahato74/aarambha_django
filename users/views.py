from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import CustomUser

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    from django.core.mail import send_mail
    from django.conf import settings
    from .otp_models import EmailOTP
    
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    otp = EmailOTP.generate_otp()
    EmailOTP.objects.create(email=email, otp=otp)
    
    try:
        subject = '🔐 Your OTP Code - Aarambha Foundation'
        message = f'''Dear User,

Thank you for choosing Aarambha Foundation!

Your One-Time Password (OTP) for email verification is:

{otp}

This OTP is valid for 10 minutes only. Please do not share this code with anyone.

If you did not request this OTP, please ignore this email.

Best regards,
Aarambha Foundation Team'''
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        return Response({'message': 'OTP sent successfully to your email'})
    except Exception as e:
        return Response({'error': 'Failed to send OTP. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    from .otp_models import EmailOTP
    
    email = request.data.get('email')
    otp = request.data.get('otp')
    
    if not email or not otp:
        return Response({'error': 'Email and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        otp_obj = EmailOTP.objects.filter(email=email, otp=otp, is_verified=False).latest('created_at')
        if not otp_obj.is_valid():
            return Response({'error': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        otp_obj.is_verified = True
        otp_obj.save()
        
        # Create or get guest user
        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0] + str(CustomUser.objects.count()),
                'user_type': 'guest',
                'is_active': True
            }
        )
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })
    except EmailOTP.DoesNotExist:
        return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response(UserSerializer(request.user).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    users = CustomUser.objects.all()
    
    # Filters
    search = request.GET.get('search', '')
    user_type = request.GET.get('user_type', '')
    branch = request.GET.get('branch', '')
    is_active = request.GET.get('is_active', '')
    
    if search:
        users = users.filter(
            Q(username__icontains=search) | 
            Q(email__icontains=search) | 
            Q(first_name__icontains=search) | 
            Q(last_name__icontains=search)
        )
    if user_type:
        users = users.filter(user_type=user_type)
    if branch:
        users = users.filter(branch_id=branch)
    if is_active:
        users = users.filter(is_active=is_active == 'true')
    
    users = users.order_by('-id')
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    start = (page - 1) * page_size
    end = start + page_size
    
    total = users.count()
    users_page = users[start:end]
    
    serializer = UserSerializer(users_page, many=True)
    return Response({
        'results': serializer.data,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    })

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        user.user_type = request.data.get('user_type', user.user_type)
        if 'branch' in request.data:
            user.branch_id = request.data['branch'] if request.data['branch'] else None
        if 'is_active' in request.data:
            user.is_active = request.data['is_active']
        user.save()
        return Response(UserSerializer(user).data)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        return Response(UserSerializer(user).data)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
