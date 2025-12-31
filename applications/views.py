from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Application
from .serializers import ApplicationSerializer
from .parsers import CustomJSONParser
from branches.models import Branch
from notices.models import UserNotification

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_application(request):
    from django.core.mail import send_mail
    from django.conf import settings

    country = request.data.get('country', 'Nepal')
    district = request.data.get('district', '')
    application_type = request.data.get('application_type', 'volunteer')
    is_upgrade = request.data.get('is_upgrade', 'false').lower() == 'true'
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

    # Check if user already has an application
    existing_application = Application.objects.filter(user=request.user).first()
    if existing_application:
        # Update existing application instead of creating new
        serializer = ApplicationSerializer(existing_application, data=request.data, partial=True)
        if serializer.is_valid():
            # Prevent changing application type
            if 'application_type' in request.data and request.data['application_type'] != existing_application.application_type:
                return Response({'error': 'Cannot change application type. Please contact support if you need to change your application type.'}, status=status.HTTP_400_BAD_REQUEST)

            application = serializer.save(branch=branch)

            # Create notification for application update
            UserNotification.objects.create(
                user=request.user,
                notification_type='application_updated',
                title='Application Updated',
                message=f'Your {application.application_type} application has been updated successfully.',
                related_application=application
            )

            return Response({
                'message': 'Application updated successfully',
                'application': serializer.data,
                'updated': True
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer = ApplicationSerializer(data=request.data)
    if serializer.is_valid():
        application = serializer.save(user=request.user, branch=branch, is_upgrade=is_upgrade)

        # Create notification for application submission
        if is_upgrade:
            notification_message = f'Your upgrade application to become a Member has been submitted successfully. Application ID: {application.id}'
            email_subject = f'🚀 Membership Upgrade Application Submitted - Aarambha Foundation'
        else:
            role_name = 'Member' if application_type == 'member' else 'Volunteer'
            notification_message = f'Your {role_name} application has been submitted successfully. Application ID: {application.id}'
            email_subject = f'🎉 Application Submitted Successfully - Aarambha Foundation'
        
        UserNotification.objects.create(
            user=request.user,
            notification_type='application_submitted',
            title=f'Application Submitted Successfully',
            message=notification_message,
            related_application=application
        )

        # Send confirmation email
        try:
            send_mail(
                email_subject,
                f'Dear {application.full_name}, Your application has been submitted successfully.',
                settings.EMAIL_HOST_USER,
                [application.user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f'Confirmation email error: {e}')

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
    
    # For each user, if they have both volunteer and member applications, only show member
    from django.db.models import Q
    users_with_member = Application.objects.filter(application_type='member').values_list('user_id', flat=True)
    applications = applications.exclude(
        Q(application_type='volunteer') & Q(user_id__in=users_with_member)
    )
    
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
        data = serializer.data
        return Response(data)
    except Application.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_applications(request):
    applications = Application.objects.filter(user=request.user).order_by('-applied_at')
    
    # If user has both volunteer and member applications, only show member application
    has_member = applications.filter(application_type='member').exists()
    if has_member:
        applications = applications.filter(application_type='member')
    
    serializer = ApplicationSerializer(applications, many=True)
    return Response(serializer.data)

class UpdateApplicationView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, pk):
        return self.patch(request, pk)

    def patch(self, request, pk):
        try:
            application = Application.objects.get(pk=pk, user=request.user)
            if application.status not in ['pending', 'rejected']:
                return Response({'error': 'Cannot update application once it has been processed'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = ApplicationSerializer(application, data=request.data, partial=True)
            if serializer.is_valid():
                # Reset status to pending when application is updated
                updated_application = serializer.save(status='pending')
                
                # Create notification for application update
                UserNotification.objects.create(
                    user=request.user,
                    notification_type='application_updated',
                    title='Application Updated',
                    message=f'Your {updated_application.application_type} application has been updated and is now under review.',
                    related_application=updated_application
                )
                
                # Send email notification
                from django.core.mail import send_mail
                from django.conf import settings
                try:
                    send_mail(
                        'Application Updated - Aarambha Foundation',
                        f'Dear {updated_application.full_name}, Your application has been updated successfully and is now under review.',
                        settings.EMAIL_HOST_USER,
                        [updated_application.user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f'Email error: {e}')
                
                return Response({
                    'message': 'Application updated successfully',
                    'application': serializer.data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Application.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)

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
@csrf_exempt
def update_application_status(request, pk):
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        application = Application.objects.get(pk=pk)
        new_status = request.data.get('status')
        
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
        if 'rejection_type' in request.data:
            application.rejection_type = request.data['rejection_type']
        
        application.save()

        # Create notifications for status changes
        if new_status == 'approved':
            UserNotification.objects.create(
                user=application.user,
                notification_type='application_approved',
                title='Application Approved!',
                message=f'Congratulations! Your {application.application_type} application has been approved.',
                related_application=application
            )
            
            # Update user
            user = application.user
            user.user_type = application.application_type
            user.is_approved = True
            user.save()

        # Send email notifications
        email_sent = False
        if new_status == 'approved':
            try:
                send_mail(
                    'Application Approved - Aarambha Foundation',
                    f'Dear {application.full_name}, Your application has been approved!',
                    settings.EMAIL_HOST_USER,
                    [application.user.email],
                    fail_silently=False,
                )
                email_sent = True
            except Exception as e:
                email_sent = False
        elif new_status == 'rejected':
            try:
                send_mail(
                    'Application Status Update - Aarambha Foundation',
                    f'Dear {application.full_name}, Your application status has been updated.',
                    settings.EMAIL_HOST_USER,
                    [application.user.email],
                    fail_silently=False,
                )
                email_sent = True
            except Exception as e:
                email_sent = False

        serializer = ApplicationSerializer(application)
        data = serializer.data
        data['email_sent'] = email_sent
        return Response(data)
    except Application.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_upgrade(request, pk):
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        application = Application.objects.get(pk=pk)
        
        # Update application status
        application.status = 'approved'
        application.save()
        
        # Update user from volunteer to member
        user = application.user
        user.user_type = 'member'
        user.is_approved = True
        user.save()
        
        # Create notification
        UserNotification.objects.create(
            user=application.user,
            notification_type='application_approved',
            title='Membership Upgrade Approved!',
            message='Your upgrade to member status has been approved.',
            related_application=application
        )
        
        # Send email
        email_sent = False
        try:
            send_mail(
                'Membership Upgrade Approved - Aarambha Foundation',
                f'Dear {application.full_name}, Your membership upgrade has been approved!',
                settings.EMAIL_HOST_USER,
                [application.user.email],
                fail_silently=False,
            )
            email_sent = True
        except Exception as e:
            email_sent = False
        
        serializer = ApplicationSerializer(application)
        data = serializer.data
        data['email_sent'] = email_sent
        return Response(data)
        
    except Application.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auto_upgrade_to_member(request):
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        # Get user's existing volunteer application
        volunteer_app = Application.objects.filter(user=request.user, application_type='volunteer').first()
        
        if not volunteer_app:
            return Response({'error': 'No volunteer application found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user already has member application
        member_app = Application.objects.filter(user=request.user, application_type='member').first()
        if member_app:
            return Response({'error': 'Member application already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create new member application by copying volunteer data
        member_data = {
            'full_name': volunteer_app.full_name,
            'date_of_birth': volunteer_app.date_of_birth,
            'phone': volunteer_app.phone,
            'country': volunteer_app.country,
            'district': volunteer_app.district,
            'temporary_address': volunteer_app.temporary_address,
            'permanent_address': volunteer_app.permanent_address,
            'profession': volunteer_app.profession,
            'social_link': volunteer_app.social_link,
            'why_join': volunteer_app.why_join,
            'self_definition': volunteer_app.self_definition,
            'ideas': volunteer_app.ideas,
            'skills': volunteer_app.skills,
            'time_commitment': volunteer_app.time_commitment,
            'other_organizations': volunteer_app.other_organizations,
            'citizenship_front': volunteer_app.citizenship_front,
            'citizenship_back': volunteer_app.citizenship_back,
            'photo': volunteer_app.photo,
            'application_type': 'member',
            'is_upgrade': True,
            'status': 'pending'
        }
        
        # Create member application
        member_application = Application.objects.create(
            user=request.user,
            branch=volunteer_app.branch,
            **member_data
        )
        
        # Create notification
        UserNotification.objects.create(
            user=request.user,
            notification_type='application_submitted',
            title='Membership Upgrade Submitted',
            message=f'Your upgrade application to become a Member has been submitted successfully. Application ID: {member_application.id}',
            related_application=member_application
        )
        
        # Send email
        try:
            send_mail(
                '🚀 Membership Upgrade Application Submitted - Aarambha Foundation',
                f'Dear {member_application.full_name}, Your membership upgrade application has been submitted successfully.',
                settings.EMAIL_HOST_USER,
                [request.user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f'Email error: {e}')
        
        serializer = ApplicationSerializer(member_application)
        return Response({
            'message': 'Upgrade application submitted successfully',
            'application': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resend_email(request, pk):
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        application = Application.objects.get(pk=pk)
        
        # Determine email subject and content based on status
        if application.status == 'approved':
            subject = 'Application Approved - Aarambha Foundation'
            message = f'Dear {application.full_name}, Your application has been approved!'
        elif application.status == 'rejected':
            subject = 'Application Status Update - Aarambha Foundation'
            message = f'Dear {application.full_name}, Your application status has been updated.'
        elif application.status == 'interview_scheduled':
            subject = 'Interview Scheduled - Aarambha Foundation'
            message = f'Dear {application.full_name}, Your interview has been scheduled.'
        else:
            return Response({'error': 'No email template for this status'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Send email
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [application.user.email],
            fail_silently=False,
        )
        
        return Response({'message': 'Email sent successfully'}, status=status.HTTP_200_OK)
        
    except Application.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)