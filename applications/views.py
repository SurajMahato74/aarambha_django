from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Application
from .serializers import ApplicationSerializer
from branches.models import Branch

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_application(request):
    country = request.data.get('country', 'Nepal')
    district = request.data.get('district', '')
    application_type = request.data.get('application_type', 'volunteer')
    branch = None
    
    # Create branch based on country and district
    if country == 'Nepal' and district:
        branch, created = Branch.objects.get_or_create(
            name=f"{district} Branch",
            defaults={
                'code': district[:3].upper(),
                'location': district,
                'is_active': True
            }
        )
    elif country and country != 'Nepal':
        branch, created = Branch.objects.get_or_create(
            name=f"{country} Branch",
            defaults={
                'code': country[:3].upper(),
                'location': country,
                'is_active': True
            }
        )
    
    serializer = ApplicationSerializer(data=request.data)
    if serializer.is_valid():
        application = serializer.save(user=request.user, branch=branch)
        
        # Set payment requirement for members (disabled until Khalti is activated)
        # TODO: Enable after Khalti merchant account activation
        # if application_type == 'member':
        #     application.payment_required = True
        #     application.payment_amount = 1000
        #     application.save()
        
        return Response({
            'message': 'Application submitted successfully',
            'application': serializer.data,
            'payment_required': application.payment_required,
            'payment_amount': float(application.payment_amount)
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_applications(request):
    applications = Application.objects.all().order_by('-applied_at')
    
    # Filters
    search = request.GET.get('search', '')
    if search:
        applications = applications.filter(full_name__icontains=search) | applications.filter(user__email__icontains=search)
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    type_filter = request.GET.get('type', '')
    if type_filter:
        applications = applications.filter(application_type=type_filter)
    
    district_filter = request.GET.get('district', '')
    if district_filter:
        applications = applications.filter(district=district_filter)
    
    paginator = PageNumberPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(applications, request)
    serializer = ApplicationSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_application(request, pk):
    try:
        application = Application.objects.get(pk=pk)
        serializer = ApplicationSerializer(application)
        return Response(serializer.data)
    except Application.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_applications(request):
    applications = Application.objects.filter(user=request.user).order_by('-applied_at')
    serializer = ApplicationSerializer(applications, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def acknowledge_interview(request, pk):
    try:
        application = Application.objects.get(pk=pk, user=request.user)
        application.interview_acknowledged = True
        application.save()
        return Response({'message': 'Interview acknowledged'})
    except Application.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_application_status(request, pk):
    from django.core.mail import send_mail
    from django.conf import settings
    from datetime import datetime
    from users.models import CustomUser
    import random
    import string
    
    try:
        application = Application.objects.get(pk=pk)
        new_status = request.data.get('status')
        old_status = application.status
        
        if new_status:
            application.status = new_status
        
        # Handle interview scheduling
        if 'interview_datetime' in request.data:
            application.interview_datetime = request.data['interview_datetime']
        if 'interview_link' in request.data:
            application.interview_link = request.data['interview_link']
        if 'interview_description' in request.data:
            application.interview_description = request.data['interview_description']
        if 'interview_attended' in request.data:
            application.interview_attended = request.data['interview_attended']
        if 'rejection_reason' in request.data:
            application.rejection_reason = request.data['rejection_reason']
        
        application.save()
        
        # Send email notifications
        user_email = application.user.email
        subject = ''
        message = ''
        
        if new_status == 'approved':
            # Generate username and password
            email_prefix = user_email.split('@')[0]
            random_suffix = ''.join(random.choices(string.digits, k=3))
            username = f"{email_prefix}{random_suffix}"
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            # Update user account
            user = application.user
            user.username = username
            user.set_password(password)
            user.user_type = application.application_type
            user.is_approved = True
            user.branch = application.branch
            user.phone = application.phone
            user.address = application.permanent_address
            user.first_name = application.full_name.split()[0] if application.full_name else ''
            user.last_name = ' '.join(application.full_name.split()[1:]) if len(application.full_name.split()) > 1 else ''
            user.save()
            
            role_name = 'Member' if application.application_type == 'member' else 'Volunteer'
            login_url = request.build_absolute_uri('/')
            
            subject = f'🎉 Congratulations! Application Approved - Aarambha Foundation'
            message = f'''Dear {application.full_name},

Congratulations! We are delighted to inform you that your application has been approved!

You have been accepted as a {role_name} at Aarambha Foundation. We are excited to have you join our team and look forward to working together to make a positive impact.

Your Login Credentials:
Username: {username}
Password: {password}

Login URL: {login_url}

Please login using the credentials above and change your password after first login for security purposes.

Welcome to the Aarambha Foundation family!

Best regards,
Aarambha Foundation Team'''
        
        elif new_status == 'rejected':
            subject = '❌ Application Status Update - Aarambha Foundation'
            message = f'''Dear {application.full_name},

Thank you for your interest in joining Aarambha Foundation as a {application.application_type}.

After careful consideration of all applications, we regret to inform you that we are unable to proceed with your application at this time.

{application.rejection_reason or 'We received many qualified applications and had to make difficult decisions.'}

We truly appreciate the time and effort you put into your application. We encourage you to stay connected with us and consider applying again in the future.

We wish you all the best in your future endeavors.

With warm regards,
Aarambha Foundation Team'''
        
        elif new_status == 'interview_scheduled' and old_status != 'interview_scheduled':
            dt = datetime.fromisoformat(application.interview_datetime.replace('Z', '+00:00')) if isinstance(application.interview_datetime, str) else application.interview_datetime
            subject = '📅 Interview Scheduled - Aarambha Foundation'
            message = f'''Dear {application.full_name},

Your interview has been scheduled for the {application.application_type} position at Aarambha Foundation.

Interview Details:
Date & Time: {dt.strftime('%B %d, %Y at %I:%M %p')}
Meeting Link: {application.interview_link or 'Will be shared soon'}

Description:
{application.interview_description or 'No additional details'}

Please be on time and prepare accordingly.

Best regards,
Aarambha Foundation Team'''
        
        elif old_status == 'interview_scheduled' and new_status == 'interview_scheduled':
            dt = datetime.fromisoformat(application.interview_datetime.replace('Z', '+00:00')) if isinstance(application.interview_datetime, str) else application.interview_datetime
            subject = '🔄 Interview Rescheduled - Aarambha Foundation'
            message = f'''Dear {application.full_name},

Your interview has been rescheduled.

Updated Interview Details:
Date & Time: {dt.strftime('%B %d, %Y at %I:%M %p')}
Meeting Link: {application.interview_link or 'Will be shared soon'}

Description:
{application.interview_description or 'No additional details'}

Please note the new schedule.

Best regards,
Aarambha Foundation Team'''
        
        if subject and message:
            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [user_email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f'Email error: {e}')
        
        serializer = ApplicationSerializer(application)
        return Response(serializer.data)
    except Application.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
