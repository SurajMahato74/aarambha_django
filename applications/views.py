from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Application, ChildSponsorship, Child, ChildAssignment, PaymentInstallment, OneRupeeCampaign, CampaignPayment
from .serializers import ApplicationSerializer
from .parsers import CustomJSONParser
from branches.models import Branch
from notices.models import UserNotification
from users.models import CustomUser

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

            # Sync name and phone from application to user model
            user.sync_name_and_phone_from_application()

            user.save()

        # Send email notifications
        email_sent = False
        if new_status == 'approved':
            # Check if member application requires payment
            if application.application_type == 'member' and application.payment_required and not application.payment_completed:
                return Response({'error': 'Cannot approve member application: Payment not completed. Member must pay Rs. 1000 membership fee first.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate login credentials for the user
            import secrets
            import string
            
            # Generate a random password
            password_length = 12
            password = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*') for _ in range(password_length))
            
            # Set the password for the user
            user = application.user
            user.set_password(password)
            user.save()
            
            # Create username from email if not exists
            if not user.username:
                username = user.email.split('@')[0]
                # Ensure username is unique
                counter = 1
                original_username = username
                while CustomUser.objects.filter(username=username).exists():
                    username = f"{original_username}{counter}"
                    counter += 1
                user.username = username
                user.save()
            
            try:
                # Send email with login credentials
                email_subject = f'🎉 Application Approved - Login Credentials - Aarambha Foundation'
                email_message = f'''Dear {application.full_name},

Congratulations! Your {application.application_type} application has been approved.

Your login credentials are:
Username: {user.username}
Email: {user.email}
Password: {password}

You can now login to your dashboard at: {settings.SITE_URL}/accounts/login/

Please keep these credentials safe and change your password after first login.

Welcome to Aarambha Foundation!

Best regards,
Aarambha Foundation Team'''
                
                send_mail(
                    email_subject,
                    email_message,
                    settings.EMAIL_HOST_USER,
                    [application.user.email],
                    fail_silently=False,
                )
                email_sent = True
            except Exception as e:
                print(f'Email error: {e}')
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

# Children Management API Endpoints
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def children_api(request):
    """List all children or create a new child"""
    if request.method == 'GET':
        children = Child.objects.all().order_by('-created_at')
        
        # Filters
        search = request.GET.get('search', '')
        if search:
            children = children.filter(full_name__icontains=search)
        
        status_filter = request.GET.get('status', '')
        if status_filter:
            children = children.filter(status=status_filter)
        
        data = []
        for child in children:
            data.append({
                'id': child.id,
                'full_name': child.full_name,
                'age': child.get_age(),
                'gender': child.gender,
                'district': child.district,
                'village': child.village,
                'school_name': child.school_name,
                'grade_level': child.grade_level,
                'status': child.status,
                'monthly_sponsorship_amount': str(child.monthly_sponsorship_amount),
                'preferred_sponsorship_type': child.preferred_sponsorship_type,
                'preferred_frequency': child.preferred_frequency,
                'current_sponsor': child.current_sponsor.get_full_name() if child.current_sponsor else None,
                'photo': child.photo.url if child.photo else None,
                'created_at': child.created_at.isoformat(),
            })
        
        return Response(data)
    
    elif request.method == 'POST':
        try:
            # Handle multi-select fields - get arrays from form data
            sponsorship_types = request.data.getlist('preferred_sponsorship_type') if hasattr(request.data, 'getlist') else request.data.get('preferred_sponsorship_type', [])
            frequencies = request.data.getlist('preferred_frequency') if hasattr(request.data, 'getlist') else request.data.get('preferred_frequency', [])
            
            child = Child.objects.create(
                full_name=request.data.get('full_name'),
                date_of_birth=request.data.get('date_of_birth'),
                gender=request.data.get('gender'),
                country=request.data.get('country', 'Nepal'),
                district=request.data.get('district'),
                village=request.data.get('village'),
                address=request.data.get('address', ''),
                father_name=request.data.get('father_name', ''),
                father_occupation=request.data.get('father_occupation', ''),
                father_alive=request.data.get('father_alive', 'true').lower() == 'true',
                mother_name=request.data.get('mother_name', ''),
                mother_occupation=request.data.get('mother_occupation', ''),
                mother_alive=request.data.get('mother_alive', 'true').lower() == 'true',
                guardian_name=request.data.get('guardian_name', ''),
                guardian_relationship=request.data.get('guardian_relationship', ''),
                guardian_occupation=request.data.get('guardian_occupation', ''),
                family_situation=request.data.get('family_situation', ''),
                family_income=request.data.get('family_income') or None,
                school_name=request.data.get('school_name', ''),
                grade_level=request.data.get('grade_level', ''),
                educational_needs=request.data.get('educational_needs', ''),
                health_status=request.data.get('health_status', ''),
                special_needs=request.data.get('special_needs', ''),
                interests_hobbies=request.data.get('interests_hobbies', ''),
                personality_description=request.data.get('personality_description', ''),
                dreams_aspirations=request.data.get('dreams_aspirations', ''),
                monthly_sponsorship_amount=request.data.get('monthly_sponsorship_amount', 0),
                preferred_sponsorship_type=sponsorship_types,
                preferred_frequency=frequencies,
                story=request.data.get('story', ''),
                urgent_needs=request.data.get('urgent_needs', ''),
                admin_notes=request.data.get('admin_notes', ''),
                photo=request.FILES.get('photo') if 'photo' in request.FILES else None,
            )
            
            return Response({
                'message': 'Child created successfully',
                'child_id': child.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def child_detail_api(request, pk):
    """Get, update or delete a specific child"""
    try:
        child = Child.objects.get(pk=pk)
    except Child.DoesNotExist:
        return Response({'error': 'Child not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        data = {
            'id': child.id,
            'full_name': child.full_name,
            'date_of_birth': child.date_of_birth.isoformat(),
            'gender': child.gender,
            'country': child.country,
            'district': child.district,
            'village': child.village,
            'address': child.address,
            'father_name': child.father_name,
            'father_occupation': child.father_occupation,
            'father_alive': child.father_alive,
            'mother_name': child.mother_name,
            'mother_occupation': child.mother_occupation,
            'mother_alive': child.mother_alive,
            'guardian_name': child.guardian_name,
            'guardian_relationship': child.guardian_relationship,
            'guardian_occupation': child.guardian_occupation,
            'family_situation': child.family_situation,
            'family_income': str(child.family_income) if child.family_income else '',
            'school_name': child.school_name,
            'grade_level': child.grade_level,
            'educational_needs': child.educational_needs,
            'health_status': child.health_status,
            'special_needs': child.special_needs,
            'interests_hobbies': child.interests_hobbies,
            'personality_description': child.personality_description,
            'dreams_aspirations': child.dreams_aspirations,
            'monthly_sponsorship_amount': str(child.monthly_sponsorship_amount),
            'preferred_sponsorship_type': child.preferred_sponsorship_type,
            'preferred_frequency': child.preferred_frequency,
            'story': child.story,
            'urgent_needs': child.urgent_needs,
            'admin_notes': child.admin_notes,
            'status': child.status,
        }
        return Response(data)
    
    elif request.method == 'PUT':
        try:
            # Handle multi-select fields
            sponsorship_types = request.data.getlist('preferred_sponsorship_type') if hasattr(request.data, 'getlist') else request.data.get('preferred_sponsorship_type', [])
            frequencies = request.data.getlist('preferred_frequency') if hasattr(request.data, 'getlist') else request.data.get('preferred_frequency', [])
            
            # Update child fields
            child.full_name = request.data.get('full_name', child.full_name)
            child.date_of_birth = request.data.get('date_of_birth', child.date_of_birth)
            child.gender = request.data.get('gender', child.gender)
            child.country = request.data.get('country', child.country)
            child.district = request.data.get('district', child.district)
            child.village = request.data.get('village', child.village)
            child.address = request.data.get('address', child.address)
            child.father_name = request.data.get('father_name', child.father_name)
            child.father_occupation = request.data.get('father_occupation', child.father_occupation)
            child.father_alive = request.data.get('father_alive', 'true').lower() == 'true'
            child.mother_name = request.data.get('mother_name', child.mother_name)
            child.mother_occupation = request.data.get('mother_occupation', child.mother_occupation)
            child.mother_alive = request.data.get('mother_alive', 'true').lower() == 'true'
            child.guardian_name = request.data.get('guardian_name', child.guardian_name)
            child.guardian_relationship = request.data.get('guardian_relationship', child.guardian_relationship)
            child.guardian_occupation = request.data.get('guardian_occupation', child.guardian_occupation)
            child.family_situation = request.data.get('family_situation', child.family_situation)
            child.family_income = request.data.get('family_income') or child.family_income
            child.school_name = request.data.get('school_name', child.school_name)
            child.grade_level = request.data.get('grade_level', child.grade_level)
            child.educational_needs = request.data.get('educational_needs', child.educational_needs)
            child.health_status = request.data.get('health_status', child.health_status)
            child.special_needs = request.data.get('special_needs', child.special_needs)
            child.interests_hobbies = request.data.get('interests_hobbies', child.interests_hobbies)
            child.personality_description = request.data.get('personality_description', child.personality_description)
            child.dreams_aspirations = request.data.get('dreams_aspirations', child.dreams_aspirations)
            child.monthly_sponsorship_amount = request.data.get('monthly_sponsorship_amount', child.monthly_sponsorship_amount)
            child.preferred_sponsorship_type = sponsorship_types
            child.preferred_frequency = frequencies
            child.story = request.data.get('story', child.story)
            child.urgent_needs = request.data.get('urgent_needs', child.urgent_needs)
            child.admin_notes = request.data.get('admin_notes', child.admin_notes)
            
            # Handle photo upload
            if 'photo' in request.FILES:
                child.photo = request.FILES['photo']
            
            child.save()
            
            return Response({
                'message': 'Child updated successfully',
                'child_id': child.id
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        child_name = child.full_name
        child.delete()
        return Response({
            'message': f'Child "{child_name}" deleted successfully'
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def children_stats(request):
    """Get children statistics"""
    from django.db.models import Count, Q
    
    stats = Child.objects.aggregate(
        total=Count('id'),
        available=Count('id', filter=Q(status='available')),
        sponsored=Count('id', filter=Q(status='sponsored')),
        graduated=Count('id', filter=Q(status='graduated')),
    )
    
    return Response(stats)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_children_to_sponsor(request, pk):
    """Assign children to a sponsor"""
    from django.core.mail import send_mail
    from django.conf import settings
    from notices.models import UserNotification
    
    try:
        sponsorship = ChildSponsorship.objects.get(pk=pk)
        child_ids = request.data.get('child_ids', [])
        
        if not child_ids:
            return Response({'error': 'No children selected'}, status=status.HTTP_400_BAD_REQUEST)
        
        assignments_created = []
        
        for child_id in child_ids:
            try:
                child = Child.objects.get(id=child_id, status='available')
                
                # Check if child is already assigned to this sponsor
                existing_assignment = ChildAssignment.objects.filter(
                    child=child,
                    sponsor=sponsorship.user,
                    status__in=['pending', 'approved']
                ).first()
                
                if existing_assignment:
                    continue
                
                # Create assignment
                assignment, created = ChildAssignment.objects.get_or_create(
                    child=child,
                    sponsor=sponsorship.user,
                    sponsorship=sponsorship,
                    defaults={'status': 'pending'}
                )
                
                if created:
                    assignments_created.append(assignment)
                    
                    # Update child status to pending assignment
                    child.status = 'pending_assignment'
                    child.save()
                    
            except Child.DoesNotExist:
                continue
        
        if assignments_created:
            # Create notification for sponsor
            UserNotification.objects.create(
                user=sponsorship.user,
                notification_type='children_assigned',
                title=f'{len(assignments_created)} Children Assigned',
                message=f'You have been assigned {len(assignments_created)} children for sponsorship. Please review and approve them in your dashboard.'
            )
            
            # Send email to sponsor
            try:
                child_names = [a.child.full_name for a in assignments_created]
                send_mail(
                    subject='New Children Assigned for Sponsorship',
                    message=f'''Dear {sponsorship.full_name},

You have been assigned {len(assignments_created)} children for sponsorship:

{chr(10).join([f"- {name}" for name in child_names])}

Please log in to your sponsor dashboard to review their profiles and approve the sponsorships.

Best regards,
Aarambha Foundation Team''',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[sponsorship.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f'Email error: {e}')
            
            return Response({
                'message': f'Successfully assigned {len(assignments_created)} children',
                'assignments': len(assignments_created)
            })
        else:
            return Response({'error': 'No valid assignments created'}, status=status.HTTP_400_BAD_REQUEST)
            
    except ChildSponsorship.DoesNotExist:
        return Response({'error': 'Sponsorship not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_child_assignments(request):
    """Get sponsor's child assignments"""
    try:
        assignments = ChildAssignment.objects.filter(sponsor=request.user).select_related('child', 'sponsorship')
        
        data = []
        for assignment in assignments:
            child = assignment.child
            data.append({
                'id': assignment.id,
                'status': assignment.status,
                'assigned_at': assignment.assigned_at.isoformat(),
                'approved_at': assignment.approved_at.isoformat() if assignment.approved_at else None,
                'child': {
                    'id': child.id,
                    'full_name': child.full_name,
                    'age': child.get_age(),
                    'gender': child.gender,
                    'district': child.district,
                    'village': child.village,
                    'school_name': child.school_name,
                    'grade_level': child.grade_level,
                    'photo': child.photo.url if child.photo else None,
                    'story': child.story,
                    'interests_hobbies': child.interests_hobbies,
                    'personality_description': child.personality_description,
                    'dreams_aspirations': child.dreams_aspirations,
                    'monthly_sponsorship_amount': str(child.monthly_sponsorship_amount),
                    'family_situation': child.family_situation,
                    'health_status': child.health_status,
                    'educational_needs': child.educational_needs,
                }
            })
        
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_child_assignment(request, assignment_id):
    """Approve a child assignment"""
    from django.core.mail import send_mail
    from django.conf import settings
    from notices.models import UserNotification
    from django.utils import timezone
    
    try:
        assignment = ChildAssignment.objects.get(id=assignment_id, sponsor=request.user)
        
        if assignment.status != 'pending':
            return Response({'error': 'Assignment already processed'}, status=status.HTTP_400_BAD_REQUEST)
        
        assignment.status = 'approved'
        assignment.approved_at = timezone.now()
        assignment.save()
        
        child = assignment.child
        child.status = 'sponsored'
        child.current_sponsor = request.user
        child.sponsorship_start_date = timezone.now().date()
        child.save()
        
        # Release other pending assignments for this sponsor
        other_assignments = ChildAssignment.objects.filter(
            sponsor=request.user, 
            status='pending'
        ).exclude(id=assignment_id)
        
        for other_assignment in other_assignments:
            other_assignment.status = 'rejected'
            other_assignment.save()
            # Make other children available again
            other_child = other_assignment.child
            other_child.status = 'available'
            other_child.save()
        
        # Create notification for sponsor
        UserNotification.objects.create(
            user=request.user,
            notification_type='sponsorship_approved',
            title='Sponsorship Approved',
            message=f'You have approved the sponsorship for {child.full_name}. Welcome to your sponsorship journey!'
        )
        
        # Create notification for admin
        from users.models import CustomUser
        admin_users = CustomUser.objects.filter(is_superuser=True)
        for admin in admin_users:
            UserNotification.objects.create(
                user=admin,
                notification_type='sponsorship_confirmed',
                title='New Sponsorship Confirmed',
                message=f'{request.user.get_full_name()} has approved sponsorship for {child.full_name}'
            )
        
        try:
            send_mail(
                subject=f'Sponsorship Approved - {child.full_name}',
                message=f'''Dear {request.user.get_full_name()},

Thank you for approving the sponsorship of {child.full_name}!

Child Details:
- Name: {child.full_name}
- Age: {child.get_age()} years
- Location: {child.district}, {child.village}
- Monthly Amount: Rs. {child.monthly_sponsorship_amount}

You can view more details in your dashboard.

Best regards,
Aarambha Foundation Team''',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[request.user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f'Email error: {e}')
        
        return Response({
            'message': 'Assignment approved successfully',
            'redirect_url': '/sponsor/children/'
        })
        
    except ChildAssignment.DoesNotExist:
        return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_sponsored_children(request):
    """Get sponsor's approved children with payment info"""
    try:
        children = Child.objects.filter(current_sponsor=request.user, status='sponsored')
        
        data = []
        for child in children:
            # Get payment history
            payments = PaymentInstallment.objects.filter(child=child, sponsor=request.user)
            completed_payments = payments.filter(status='completed').count()
            
            data.append({
                'id': child.id,
                'full_name': child.full_name,
                'age': child.get_age(),
                'gender': child.gender,
                'district': child.district,
                'village': child.village,
                'school_name': child.school_name,
                'grade_level': child.grade_level,
                'photo': child.photo.url if child.photo else None,
                'story': child.story,
                'interests_hobbies': child.interests_hobbies,
                'monthly_sponsorship_amount': str(child.monthly_sponsorship_amount),
                'sponsorship_start_date': child.sponsorship_start_date.isoformat() if child.sponsorship_start_date else None,
                'completed_payments': completed_payments,
                'has_payments': payments.exists(),
            })
        
        return Response(data)
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request, pk):
    """Initiate Khalti payment for member application"""
    import requests
    import uuid
    from django.conf import settings
    
    try:
        application = Application.objects.get(pk=pk, user=request.user)
        
        if application.application_type != 'member':
            return Response({'error': 'Payment only required for member applications'}, status=status.HTTP_400_BAD_REQUEST)
        
        if application.payment_completed:
            return Response({'error': 'Payment already completed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure payment is required and amount is set
        if not application.payment_required:
            application.payment_required = True
            application.payment_amount = 1000
            application.save()
        
        # Generate unique purchase order ID
        purchase_order_id = f"AF-{application.id}-{uuid.uuid4().hex[:12].upper()}"
        
        # Use sandbox credentials for testing
        khalti_secret_key = "05bf95cc57244045b8df5fad06748dab"  # Test key from docs
        
        # Get return URL from request or use default
        base_url = request.build_absolute_uri('/').rstrip('/')
        return_url = f"{base_url}/api/applications/{pk}/verify-payment/"
        website_url = base_url
        
        # Prepare Khalti payment initiate payload
        khalti_payload = {
            "return_url": return_url,
            "website_url": website_url,
            "amount": int(application.payment_amount * 100),  # Convert to paisa
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": f"Membership Fee - {application.full_name}",
            "customer_info": {
                "name": application.full_name,
                "email": application.user.email,
                "phone": application.phone if application.phone else "9800000001"
            }
        }
        
        # Make request to Khalti SANDBOX API
        khalti_url = "https://dev.khalti.com/api/v2/epayment/initiate/"
        headers = {
            'Authorization': f'key {khalti_secret_key}',
            'Content-Type': 'application/json',
        }
        
        response = requests.post(khalti_url, json=khalti_payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            khalti_response = response.json()
            
            # Update application with Khalti response
            application.khalti_payment_token = khalti_response.get('pidx')
            application.save()
            
            return Response({
                'success': True,
                'application_id': application.id,
                'purchase_order_id': purchase_order_id,
                'pidx': khalti_response.get('pidx'),
                'payment_url': khalti_response.get('payment_url'),
                'expires_at': khalti_response.get('expires_at'),
                'expires_in': khalti_response.get('expires_in')
            }, status=status.HTTP_200_OK)
        else:
            # Khalti API error
            try:
                error_data = response.json() if response.content else {'error': 'Unknown error'}
            except:
                error_data = {'error': 'Failed to parse error response', 'content': response.text[:500]}
            return Response({
                'error': 'Failed to initiate payment with Khalti',
                'details': error_data
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Application.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request, pk):
    """Verify Khalti payment"""
    import requests
    from django.conf import settings
    from django.utils import timezone
    from decimal import Decimal
    from django.core.mail import send_mail
    from notices.models import UserNotification
    from django.shortcuts import redirect
    
    try:
        pidx = request.GET.get('pidx') or request.data.get('pidx')
        token = request.GET.get('token') or request.data.get('token')
        amount = request.GET.get('amount') or request.data.get('amount')
        status_param = request.GET.get('status') or request.data.get('status')
        
        if not pidx:
            return Response({'error': 'pidx is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find application by pidx
        try:
            application = Application.objects.get(khalti_payment_token=pidx)
        except Application.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # If already verified, redirect to profile
        if application.payment_completed:
            if request.method == 'GET':
                return redirect('/guest/profile/')
            return Response({
                'success': True,
                'application_id': application.id,
                'status': 'completed',
                'transaction_id': application.khalti_transaction_id,
                'amount': str(application.payment_amount),
                'payment_completed': True,
                'message': 'Payment already verified'
            }, status=status.HTTP_200_OK)
        
        # Get Khalti credentials from settings
        khalti_secret_key = "05bf95cc57244045b8df5fad06748dab"  # Test key from docs
        
        # Use ePayment lookup API (SANDBOX)
        khalti_url = "https://dev.khalti.com/api/v2/epayment/lookup/"
        headers = {
            'Authorization': f'key {khalti_secret_key}',
            'Content-Type': 'application/json',
        }
        
        lookup_payload = {"pidx": pidx}
        response = requests.post(khalti_url, json=lookup_payload, headers=headers)
        
        if response.status_code == 200:
            khalti_response = response.json()
            
            # Update application with lookup response
            payment_status = khalti_response.get('status', '').lower()
            
            if payment_status == 'completed':
                application.payment_completed = True
                application.payment_date = timezone.now()
                application.khalti_transaction_id = khalti_response.get('transaction_id')
                application.save()
                
                # Create notification
                UserNotification.objects.create(
                    user=application.user,
                    notification_type='payment_completed',
                    title='Payment Completed Successfully!',
                    message=f'Your membership fee payment of Rs. {application.payment_amount} has been completed successfully. Transaction ID: {application.khalti_transaction_id}',
                    related_application=application
                )
                
                # Send email
                try:
                    send_mail(
                        'Payment Completed - Aarambha Foundation',
                        f'Dear {application.full_name},\n\nYour membership fee payment of Rs. {application.payment_amount} has been completed successfully.\n\nTransaction ID: {application.khalti_transaction_id}\n\nThank you for joining Aarambha Foundation!\n\nBest regards,\nAarambha Foundation Team',
                        settings.EMAIL_HOST_USER,
                        [application.user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f'Email error: {e}')
            
            # If GET request (callback), redirect to profile
            if request.method == 'GET':
                return redirect('/guest/profile/')
            
            return Response({
                'success': True,
                'application_id': application.id,
                'status': payment_status,
                'transaction_id': khalti_response.get('transaction_id'),
                'amount': str(application.payment_amount),
                'payment_completed': application.payment_completed
            }, status=status.HTTP_200_OK)
        else:
            # Lookup failed
            error_data = response.json() if response.content else {'error': 'Unknown error'}
            if request.method == 'GET':
                return redirect('/guest/profile/?error=payment_verification_failed')
            return Response({
                'error': 'Failed to verify payment with Khalti',
                'details': error_data
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        if request.method == 'GET':
            return redirect('/guest/profile/?error=payment_error')
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_sponsorship(request):
    from django.core.mail import send_mail
    from django.conf import settings
    import json
    
    try:
        # Parse communication methods
        comm_methods = request.data.getlist('comm_method', [])
        
        # Create sponsorship application
        sponsorship = ChildSponsorship.objects.create(
            user=request.user,
            full_name=request.data.get('full_name'),
            email=request.data.get('email'),
            phone=request.data.get('phone'),
            country=request.data.get('country', 'Nepal'),
            city=request.data.get('city'),
            address=request.data.get('address'),
            occupation=request.data.get('occupation', ''),
            organization=request.data.get('organization', ''),
            sponsorship_type=request.data.get('sponsorship_type'),
            child_gender=request.data.get('child_gender', ''),
            child_age=request.data.get('child_age', ''),
            special_requests=request.data.get('special_requests', ''),
            update_frequency=request.data.get('update_frequency'),
            comm_method=comm_methods,
            message=request.data.get('message', ''),
            payment_method=request.data.get('payment_method'),
            payment_amount=request.data.get('payment_amount') or None,
            payment_frequency=request.data.get('payment_frequency', 'One-time'),
            tax_deductible=request.data.get('tax_deductible', 'Yes') == 'Yes'
        )
        
        # Create notification
        UserNotification.objects.create(
            user=request.user,
            notification_type='application_submitted',
            title='Child Sponsorship Application Submitted',
            message=f'Your child sponsorship application has been submitted successfully. Application ID: {sponsorship.id}',
        )
        
        # Send confirmation email
        try:
            send_mail(
                '🎉 Child Sponsorship Application Submitted - Aarambha Foundation',
                f'Dear {sponsorship.full_name},\n\nYour child sponsorship application has been submitted successfully.\n\nApplication ID: {sponsorship.id}\nSponsorship Type: {sponsorship.sponsorship_type}\n\nWe will review your application and get back to you within 2-3 business days.\n\nThank you for your interest in supporting children through Aarambha Foundation!\n\nBest regards,\nAarambha Foundation Team',
                settings.EMAIL_HOST_USER,
                [sponsorship.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f'Confirmation email error: {e}')
        
        return Response({
            'message': 'Sponsorship application submitted successfully',
            'sponsorship_id': sponsorship.id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_sponsorships(request):
    sponsorships = ChildSponsorship.objects.filter(user=request.user).order_by('-created_at')
    
    data = []
    for sponsorship in sponsorships:
        data.append({
            'id': sponsorship.id,
            'full_name': sponsorship.full_name,
            'sponsorship_type': sponsorship.sponsorship_type,
            'payment_amount': str(sponsorship.payment_amount) if sponsorship.payment_amount else None,
            'status': sponsorship.status,
            'created_at': sponsorship.created_at.isoformat(),
            'child_gender': sponsorship.child_gender,
            'child_age': sponsorship.child_age,
            'update_frequency': sponsorship.update_frequency,
        })
    
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_sponsorships(request):
    sponsorships = ChildSponsorship.objects.all().order_by('-created_at')
    
    # Filters
    search = request.GET.get('search', '')
    if search:
        sponsorships = sponsorships.filter(full_name__icontains=search) | sponsorships.filter(email__icontains=search)
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        sponsorships = sponsorships.filter(status=status_filter)
    
    type_filter = request.GET.get('type', '')
    if type_filter:
        sponsorships = sponsorships.filter(sponsorship_type=type_filter)
    
    paginator = PageNumberPagination()
    paginator.page_size = 20
    result_page = paginator.paginate_queryset(sponsorships, request)
    
    data = []
    for sponsorship in result_page:
        data.append({
            'id': sponsorship.id,
            'full_name': sponsorship.full_name,
            'email': sponsorship.email,
            'phone': sponsorship.phone,
            'country': sponsorship.country,
            'city': sponsorship.city,
            'sponsorship_type': sponsorship.sponsorship_type,
            'payment_amount': str(sponsorship.payment_amount) if sponsorship.payment_amount else None,
            'payment_method': sponsorship.payment_method,
            'status': sponsorship.status,
            'rejection_reason': sponsorship.rejection_reason,
            'can_reapply': sponsorship.can_reapply,
            'created_at': sponsorship.created_at.isoformat(),
            'child_gender': sponsorship.child_gender,
            'child_age': sponsorship.child_age,
            'update_frequency': sponsorship.update_frequency,
            'comm_method': sponsorship.comm_method,
        })
    
    return paginator.get_paginated_response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sponsorship(request, pk):
    try:
        sponsorship = ChildSponsorship.objects.get(pk=pk)
        data = {
            'id': sponsorship.id,
            'full_name': sponsorship.full_name,
            'email': sponsorship.email,
            'phone': sponsorship.phone,
            'country': sponsorship.country,
            'city': sponsorship.city,
            'address': sponsorship.address,
            'occupation': sponsorship.occupation,
            'organization': sponsorship.organization,
            'sponsorship_type': sponsorship.sponsorship_type,
            'child_gender': sponsorship.child_gender,
            'child_age': sponsorship.child_age,
            'special_requests': sponsorship.special_requests,
            'update_frequency': sponsorship.update_frequency,
            'comm_method': sponsorship.comm_method,
            'message': sponsorship.message,
            'payment_method': sponsorship.payment_method,
            'payment_amount': str(sponsorship.payment_amount) if sponsorship.payment_amount else None,
            'payment_frequency': sponsorship.payment_frequency,
            'tax_deductible': sponsorship.tax_deductible,
            'status': sponsorship.status,
            'rejection_reason': sponsorship.rejection_reason,
            'can_reapply': sponsorship.can_reapply,
            'admin_notes': sponsorship.admin_notes,
            'created_at': sponsorship.created_at.isoformat(),
            'updated_at': sponsorship.updated_at.isoformat(),
        }
        return Response(data)
    except ChildSponsorship.DoesNotExist:
        return Response({'error': 'Sponsorship not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_sponsorship_status(request, pk):
    from django.core.mail import send_mail
    from django.conf import settings
    import secrets
    import string
    
    try:
        sponsorship = ChildSponsorship.objects.get(pk=pk)
        new_status = request.data.get('status')
        admin_notes = request.data.get('admin_notes', '')
        rejection_reason = request.data.get('rejection_reason', '')
        allow_reapply = request.data.get('allow_reapply', False)
        
        if new_status:
            sponsorship.status = new_status
        
        if admin_notes:
            sponsorship.admin_notes = admin_notes
            
        if rejection_reason:
            sponsorship.rejection_reason = rejection_reason
            
        if new_status == 'rejected':
            sponsorship.can_reapply = allow_reapply
        
        sponsorship.save()
        
        # Handle approval - create sponsor account
        if new_status == 'approved':
            user = sponsorship.user

            # Generate login credentials
            password = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*') for _ in range(12))
            user.set_password(password)
            user.user_type = 'sponsor'
            user.is_approved = True

            # Sync name and phone from sponsorship to user model
            user.sync_name_and_phone_from_sponsorship()

            # Create username from email if not exists
            if not user.username:
                username = user.email.split('@')[0]
                counter = 1
                original_username = username
                while CustomUser.objects.filter(username=username).exists():
                    username = f"{original_username}{counter}"
                    counter += 1
                user.username = username

            user.save()
            
            # Create notification
            UserNotification.objects.create(
                user=sponsorship.user,
                notification_type='application_approved',
                title='Child Sponsorship Approved!',
                message=f'Your child sponsorship application has been approved. Login credentials have been sent to your email.',
            )
            
            # Send email with credentials
            try:
                subject = f'🎉 Child Sponsorship Approved - Login Credentials - Aarambha Foundation'
                message = f'''Dear {sponsorship.full_name},

Congratulations! Your child sponsorship application has been approved.

Your login credentials are:
Username: {user.username}
Email: {user.email}
Password: {password}
Role: Sponsor

You can now login to your sponsor dashboard at: {settings.SITE_URL}/accounts/login/

Please keep these credentials safe and change your password after first login.

We will match you with a child based on your preferences and send you their profile within the next few days.

Thank you for your generosity!

Best regards,
Aarambha Foundation Team'''
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[sponsorship.email],
                    fail_silently=False,
                )
                email_sent = True
            except Exception as e:
                print(f'Email error: {e}')
                email_sent = False
                
        elif new_status == 'rejected':
            # Create notification
            UserNotification.objects.create(
                user=sponsorship.user,
                notification_type='application_rejected',
                title='Child Sponsorship Application Update',
                message=f'Your child sponsorship application has been reviewed. {"You can edit and resubmit your application." if allow_reapply else ""}',
            )
            
            # Send rejection email
            try:
                subject = f'📋 Child Sponsorship Application Update - Aarambha Foundation'
                reapply_text = "\n\nYou can edit and resubmit your application by logging into your account." if allow_reapply else ""
                message = f'''Dear {sponsorship.full_name},

We have reviewed your child sponsorship application.

Status: Application Not Approved
{f"Reason: {rejection_reason}" if rejection_reason else ""}

{admin_notes if admin_notes else ""}{reapply_text}

If you have any questions, please feel free to contact us.

Best regards,
Aarambha Foundation Team'''
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[sponsorship.email],
                    fail_silently=False,
                )
                email_sent = True
            except Exception as e:
                print(f'Email error: {e}')
                email_sent = False
        else:
            email_sent = False
        
        return Response({
            'message': 'Sponsorship status updated successfully',
            'email_sent': email_sent
        })
    except ChildSponsorship.DoesNotExist:
        return Response({'error': 'Sponsorship not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_sponsorship(request, pk):
    from django.core.mail import send_mail
    from django.conf import settings
    
    try:
        sponsorship = ChildSponsorship.objects.get(pk=pk, user=request.user)
        
        # Only allow updates if rejected and can_reapply is True
        if sponsorship.status != 'rejected' or not sponsorship.can_reapply:
            return Response({'error': 'Cannot update this sponsorship application'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update fields
        sponsorship.full_name = request.data.get('full_name', sponsorship.full_name)
        sponsorship.phone = request.data.get('phone', sponsorship.phone)
        sponsorship.city = request.data.get('city', sponsorship.city)
        sponsorship.address = request.data.get('address', sponsorship.address)
        sponsorship.occupation = request.data.get('occupation', sponsorship.occupation)
        sponsorship.organization = request.data.get('organization', sponsorship.organization)
        sponsorship.sponsorship_type = request.data.get('sponsorship_type', sponsorship.sponsorship_type)
        sponsorship.child_gender = request.data.get('child_gender', sponsorship.child_gender)
        sponsorship.child_age = request.data.get('child_age', sponsorship.child_age)
        sponsorship.special_requests = request.data.get('special_requests', sponsorship.special_requests)
        sponsorship.update_frequency = request.data.get('update_frequency', sponsorship.update_frequency)
        sponsorship.comm_method = request.data.getlist('comm_method', sponsorship.comm_method)
        sponsorship.message = request.data.get('message', sponsorship.message)
        sponsorship.payment_method = request.data.get('payment_method', sponsorship.payment_method)
        sponsorship.payment_amount = request.data.get('payment_amount', sponsorship.payment_amount)
        sponsorship.payment_frequency = request.data.get('payment_frequency', sponsorship.payment_frequency)
        sponsorship.tax_deductible = request.data.get('tax_deductible', 'Yes') == 'Yes'
        
        # Reset status to pending and clear rejection fields
        sponsorship.status = 'pending'
        sponsorship.rejection_reason = ''
        sponsorship.can_reapply = False
        sponsorship.admin_notes = ''
        
        sponsorship.save()
        
        # Create notification
        UserNotification.objects.create(
            user=request.user,
            notification_type='application_resubmitted',
            title='Child Sponsorship Application Resubmitted',
            message=f'Your updated child sponsorship application has been resubmitted successfully. Application ID: {sponsorship.id}',
        )
        
        # Send confirmation email
        try:
            send_mail(
                '🔄 Child Sponsorship Application Resubmitted - Aarambha Foundation',
                f'Dear {sponsorship.full_name},\n\nYour updated child sponsorship application has been resubmitted successfully.\n\nApplication ID: {sponsorship.id}\n\nWe will review your application and get back to you within 2-3 business days.\n\nThank you for your continued interest in supporting children through Aarambha Foundation!\n\nBest regards,\nAarambha Foundation Team',
                settings.EMAIL_HOST_USER,
                [sponsorship.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f'Confirmation email error: {e}')
        
        return Response({
            'message': 'Sponsorship application updated and resubmitted successfully',
            'sponsorship_id': sponsorship.id
        }, status=status.HTTP_200_OK)
        
    except ChildSponsorship.DoesNotExist:
        return Response({'error': 'Sponsorship not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sponsorship_assignments(request, pk):
    """Get assignments for a specific sponsorship"""
    try:
        sponsorship = ChildSponsorship.objects.get(pk=pk)
        assignments = ChildAssignment.objects.filter(sponsorship=sponsorship).select_related('child')
        
        data = []
        for assignment in assignments:
            child = assignment.child
            data.append({
                'id': assignment.id,
                'status': assignment.status,
                'assigned_at': assignment.assigned_at.isoformat(),
                'approved_at': assignment.approved_at.isoformat() if assignment.approved_at else None,
                'child': {
                    'id': child.id,
                    'full_name': child.full_name,
                    'age': child.get_age(),
                    'gender': child.gender,
                    'district': child.district,
                    'village': child.village,
                    'photo': child.photo.url if child.photo else None,
                    'monthly_sponsorship_amount': str(child.monthly_sponsorship_amount),
                }
            })
        
        return Response(data)
    except ChildSponsorship.DoesNotExist:
        return Response({'error': 'Sponsorship not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_assignment(request, assignment_id):
    """Remove a child assignment"""
    try:
        assignment = ChildAssignment.objects.get(id=assignment_id)
        child = assignment.child
        
        # Make child available again
        child.status = 'available'
        child.current_sponsor = None
        child.sponsorship_start_date = None
        child.save()
        
        # Delete the assignment
        assignment.delete()
        
        return Response({'message': 'Assignment removed successfully'})
        
    except ChildAssignment.DoesNotExist:
        return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_test_payment(request, pk):
    """Test endpoint to confirm payment for testing purposes"""
    from django.utils import timezone
    
    try:
        application = Application.objects.get(pk=pk, user=request.user)
        
        if application.application_type != 'member':
            return Response({'error': 'Payment only required for member applications'}, status=status.HTTP_400_BAD_REQUEST)
        
        if application.payment_completed:
            return Response({'error': 'Payment already completed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark payment as completed for testing
        application.payment_completed = True
        application.payment_date = timezone.now()
        application.khalti_transaction_id = f"TEST-{pk}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        application.save()
        
        return Response({
            'message': 'Test payment confirmed successfully',
            'payment_completed': True
        })
        
    except Application.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_child_payment(request, child_id):
    """Initiate Khalti payment for child sponsorship installment"""
    import requests
    import uuid
    from django.conf import settings
    
    try:
        child = Child.objects.get(id=child_id, current_sponsor=request.user)
        amount = float(request.data.get('amount', child.monthly_sponsorship_amount))
        
        # Get next installment number
        last_installment = PaymentInstallment.objects.filter(
            child=child, sponsor=request.user
        ).order_by('-installment_number').first()
        installment_number = (last_installment.installment_number + 1) if last_installment else 1
        
        # Create payment installment record
        installment = PaymentInstallment.objects.create(
            child=child,
            sponsor=request.user,
            amount=amount,
            installment_number=installment_number,
            status='pending'
        )
        
        # Generate unique purchase order ID
        purchase_order_id = f"CHILD-{child.id}-{installment.id}-{uuid.uuid4().hex[:8].upper()}"
        
        # Use sandbox credentials
        khalti_secret_key = "05bf95cc57244045b8df5fad06748dab"
        
        # Get return URL
        base_url = request.build_absolute_uri('/').rstrip('/')
        return_url = f"{base_url}/api/applications/child-payment/{installment.id}/verify/"
        website_url = base_url
        
        # Prepare Khalti payment payload
        khalti_payload = {
            "return_url": return_url,
            "website_url": website_url,
            "amount": int(amount * 100),  # Convert to paisa
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": f"Child Sponsorship - {child.full_name} - Installment #{installment_number}",
            "customer_info": {
                "name": request.user.get_full_name() or request.user.username,
                "email": request.user.email,
                "phone": "9800000001"
            }
        }
        
        # Make request to Khalti SANDBOX API
        khalti_url = "https://dev.khalti.com/api/v2/epayment/initiate/"
        headers = {
            'Authorization': f'key {khalti_secret_key}',
            'Content-Type': 'application/json',
        }
        
        response = requests.post(khalti_url, json=khalti_payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            khalti_response = response.json()
            
            # Update installment with Khalti response
            installment.khalti_payment_token = khalti_response.get('pidx')
            installment.save()
            
            return Response({
                'success': True,
                'installment_id': installment.id,
                'purchase_order_id': purchase_order_id,
                'pidx': khalti_response.get('pidx'),
                'payment_url': khalti_response.get('payment_url'),
                'expires_at': khalti_response.get('expires_at'),
                'expires_in': khalti_response.get('expires_in')
            }, status=status.HTTP_200_OK)
        else:
            error_data = response.json() if response.content else {'error': 'Unknown error'}
            return Response({
                'error': 'Failed to initiate payment with Khalti',
                'details': error_data
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Child.DoesNotExist:
        return Response({'error': 'Child not found or not sponsored by you'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def verify_child_payment(request, installment_id):
    """Verify Khalti payment for child sponsorship"""
    import requests
    from django.conf import settings
    from django.utils import timezone
    from django.core.mail import send_mail
    from notices.models import UserNotification
    from django.shortcuts import redirect
    
    try:
        pidx = request.GET.get('pidx') or request.data.get('pidx')
        
        if not pidx:
            return Response({'error': 'pidx is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find installment by pidx
        try:
            installment = PaymentInstallment.objects.get(khalti_payment_token=pidx, sponsor=request.user)
        except PaymentInstallment.DoesNotExist:
            return Response({'error': 'Payment installment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # If already verified, redirect to children page
        if installment.status == 'completed':
            if request.method == 'GET':
                return redirect('/sponsor/children/')
            return Response({
                'success': True,
                'installment_id': installment.id,
                'status': 'completed',
                'transaction_id': installment.khalti_transaction_id,
                'amount': str(installment.amount),
                'payment_completed': True,
                'message': 'Payment already verified'
            }, status=status.HTTP_200_OK)
        
        # Use Khalti lookup API
        khalti_secret_key = "05bf95cc57244045b8df5fad06748dab"
        khalti_url = "https://dev.khalti.com/api/v2/epayment/lookup/"
        headers = {
            'Authorization': f'key {khalti_secret_key}',
            'Content-Type': 'application/json',
        }
        
        lookup_payload = {"pidx": pidx}
        response = requests.post(khalti_url, json=lookup_payload, headers=headers)
        
        if response.status_code == 200:
            khalti_response = response.json()
            payment_status = khalti_response.get('status', '').lower()
            
            if payment_status == 'completed':
                installment.status = 'completed'
                installment.payment_date = timezone.now()
                installment.khalti_transaction_id = khalti_response.get('transaction_id')
                installment.save()
                
                # Create notification
                UserNotification.objects.create(
                    user=request.user,
                    notification_type='payment_completed',
                    title='Payment Completed Successfully!',
                    message=f'Your payment of Rs. {installment.amount} for {installment.child.full_name} has been completed successfully. Transaction ID: {installment.khalti_transaction_id}',
                )
                
                # Send email
                try:
                    send_mail(
                        'Child Sponsorship Payment Completed - Aarambha Foundation',
                        f'Dear {request.user.get_full_name() or request.user.username},\n\nYour sponsorship payment of Rs. {installment.amount} for {installment.child.full_name} has been completed successfully.\n\nTransaction ID: {installment.khalti_transaction_id}\nInstallment: #{installment.installment_number}\n\nThank you for your continued support!\n\nBest regards,\nAarambha Foundation Team',
                        settings.EMAIL_HOST_USER,
                        [request.user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f'Email error: {e}')
            
            # If GET request (callback), redirect to children page
            if request.method == 'GET':
                return redirect('/sponsor/children/')
            
            return Response({
                'success': True,
                'installment_id': installment.id,
                'status': payment_status,
                'transaction_id': khalti_response.get('transaction_id'),
                'amount': str(installment.amount),
                'payment_completed': installment.status == 'completed'
            }, status=status.HTTP_200_OK)
        else:
            error_data = response.json() if response.content else {'error': 'Unknown error'}
            if request.method == 'GET':
                return redirect('/sponsor/children/?error=payment_verification_failed')
            return Response({
                'error': 'Failed to verify payment with Khalti',
                'details': error_data
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        if request.method == 'GET':
            return redirect('/sponsor/children/?error=payment_error')
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_child_payments(request, child_id):
    """Get payment history for a child"""
    try:
        # Check if user has approved assignment for this child (allows access even after cancellation)
        assignment = ChildAssignment.objects.filter(
            child_id=child_id, 
            sponsor=request.user, 
            status='approved'
        ).first()

        if not assignment:
            return Response({'error': 'Child not found or not sponsored by you'}, status=status.HTTP_404_NOT_FOUND)

        child = assignment.child
        payments = PaymentInstallment.objects.filter(child=child, sponsor=request.user).order_by('-created_at')
        
        data = []
        for payment in payments:
            data.append({
                'id': payment.id,
                'amount': str(payment.amount),
                'status': payment.status,
                'installment_number': payment.installment_number,
                'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
                'transaction_id': payment.khalti_transaction_id,
                'created_at': payment.created_at.isoformat(),
            })
        
        return Response(data)
    except Child.DoesNotExist:
        return Response({'error': 'Child not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_sponsorship(request, child_id):
    """Cancel sponsorship for a child"""
    from django.core.mail import send_mail
    from django.conf import settings
    from notices.models import UserNotification
    
    try:
        child = Child.objects.get(id=child_id, current_sponsor=request.user)
        
        # Update child status
        child.status = 'available'
        child.current_sponsor = None
        child.sponsorship_start_date = None
        child.save()
        
        # Create notification for sponsor
        UserNotification.objects.create(
            user=request.user,
            notification_type='sponsorship_cancelled',
            title='Sponsorship Cancelled',
            message=f'You have cancelled the sponsorship for {child.full_name}. The child is now available for other sponsors.'
        )
        
        # Create notification for admin
        admin_users = CustomUser.objects.filter(is_superuser=True)
        for admin in admin_users:
            UserNotification.objects.create(
                user=admin,
                notification_type='sponsorship_cancelled',
                title='Sponsorship Cancelled',
                message=f'{request.user.get_full_name() or request.user.username} has cancelled sponsorship for {child.full_name}'
            )
        
        # Send email
        try:
            send_mail(
                'Sponsorship Cancelled - Aarambha Foundation',
                f'Dear {request.user.get_full_name() or request.user.username},\n\nYou have successfully cancelled the sponsorship for {child.full_name}.\n\nThe child is now available for other sponsors.\n\nThank you for your past support.\n\nBest regards,\nAarambha Foundation Team',
                settings.EMAIL_HOST_USER,
                [request.user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f'Email error: {e}')
        
        return Response({'message': 'Sponsorship cancelled successfully'})
        
    except Child.DoesNotExist:
        return Response({'error': 'Child not found or not sponsored by you'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_sponsorship_history(request):
    """Get sponsor's complete sponsorship history including cancelled ones"""
    try:
        # Get all children that were ever sponsored by this user
        assignments = ChildAssignment.objects.filter(
            sponsor=request.user, 
            status='approved'
        ).select_related('child')
        
        data = []
        for assignment in assignments:
            child = assignment.child
            # Get payment history
            payments = PaymentInstallment.objects.filter(child=child, sponsor=request.user)
            completed_payments = payments.filter(status='completed').count()
            
            # Determine current status
            is_active = child.current_sponsor == request.user and child.status == 'sponsored'
            
            data.append({
                'id': child.id,
                'full_name': child.full_name,
                'age': child.get_age(),
                'district': child.district,
                'photo': child.photo.url if child.photo else None,
                'monthly_amount': str(child.monthly_sponsorship_amount),
                'is_active': is_active,
                'sponsorship_start_date': child.sponsorship_start_date.isoformat() if child.sponsorship_start_date else None,
                'total_payments': payments.count(),
                'completed_payments': completed_payments,
                'total_amount_paid': str(sum(p.amount for p in payments.filter(status='completed'))),
                'last_payment_date': payments.filter(status='completed').order_by('-payment_date').first().payment_date.isoformat() if payments.filter(status='completed').exists() else None
            })
        
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_payment_stats(request):
    """Get payment statistics for admin dashboard"""
    if not request.user.is_superuser:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from django.db.models import Sum, Count
        
        all_payments = PaymentInstallment.objects.all()
        
        stats = {
            'total_payments': all_payments.count(),
            'completed_payments': all_payments.filter(status='completed').count(),
            'pending_payments': all_payments.filter(status='pending').count(),
            'failed_payments': all_payments.filter(status='failed').count(),
            'total_amount': str(all_payments.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0)
        }
        
        return Response(stats)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_payment_list(request):
    """Get paginated list of all payments for admin"""
    if not request.user.is_superuser:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from django.core.paginator import Paginator
        from django.db.models import Q
        
        payments = PaymentInstallment.objects.select_related('child', 'sponsor').order_by('-created_at')
        
        # Apply filters
        search = request.GET.get('search', '')
        status_filter = request.GET.get('status', '')
        child_filter = request.GET.get('child', '')
        sponsor_filter = request.GET.get('sponsor', '')
        
        if search:
            payments = payments.filter(
                Q(sponsor__first_name__icontains=search) |
                Q(sponsor__last_name__icontains=search) |
                Q(sponsor__email__icontains=search) |
                Q(child__full_name__icontains=search) |
                Q(khalti_transaction_id__icontains=search)
            )
        
        if status_filter:
            payments = payments.filter(status=status_filter)
        
        if child_filter:
            payments = payments.filter(child_id=child_filter)
        
        if sponsor_filter:
            payments = payments.filter(sponsor__email=sponsor_filter)
        
        # Paginate
        paginator = Paginator(payments, 20)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        data = []
        for payment in page_obj:
            data.append({
                'id': payment.id,
                'installment_number': payment.installment_number,
                'amount': str(payment.amount),
                'status': payment.status,
                'khalti_transaction_id': payment.khalti_transaction_id,
                'khalti_payment_token': payment.khalti_payment_token,
                'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
                'created_at': payment.created_at.isoformat(),
                'notes': payment.notes,
                'sponsor_name': payment.sponsor.get_full_name() or payment.sponsor.email,
                'sponsor_email': payment.sponsor.email,
                'child_id': payment.child.id,
                'child_name': payment.child.full_name,
                'child_age': payment.child.get_age(),
                'child_district': payment.child.district,
                'child_photo': payment.child.photo.url if payment.child.photo else None
            })
        
        return Response({
            'results': data,
            'count': paginator.count,
            'next': page_obj.has_next(),
            'previous': page_obj.has_previous()
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_payment_detail(request, payment_id):
    """Get detailed payment information for admin"""
    if not request.user.is_superuser:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        payment = PaymentInstallment.objects.select_related('child', 'sponsor').get(id=payment_id)
        
        data = {
            'id': payment.id,
            'installment_number': payment.installment_number,
            'amount': str(payment.amount),
            'status': payment.status,
            'khalti_transaction_id': payment.khalti_transaction_id,
            'khalti_payment_token': payment.khalti_payment_token,
            'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
            'created_at': payment.created_at.isoformat(),
            'updated_at': payment.updated_at.isoformat(),
            'notes': payment.notes,
            'sponsor_name': payment.sponsor.get_full_name() or payment.sponsor.email,
            'sponsor_email': payment.sponsor.email,
            'child_id': payment.child.id,
            'child_name': payment.child.full_name,
            'child_age': payment.child.get_age(),
            'child_district': payment.child.district,
            'child_photo': payment.child.photo.url if payment.child.photo else None
        }
        
        return Response(data)
    except PaymentInstallment.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_mark_payment_completed(request, payment_id):
    """Mark a payment as completed (admin only)"""
    if not request.user.is_superuser:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from django.utils import timezone
        from notices.models import UserNotification
        from django.core.mail import send_mail
        from django.conf import settings
        
        payment = PaymentInstallment.objects.select_related('child', 'sponsor').get(id=payment_id)
        
        if payment.status == 'completed':
            return Response({'error': 'Payment is already completed'}, status=status.HTTP_400_BAD_REQUEST)
        
        payment.status = 'completed'
        payment.payment_date = timezone.now()
        payment.save()
        
        # Create notification
        UserNotification.objects.create(
            user=payment.sponsor,
            notification_type='payment_completed',
            title='Payment Completed by Admin',
            message=f'Your payment of Rs. {payment.amount} for {payment.child.full_name} has been marked as completed by admin.'
        )
        
        # Send email
        try:
            send_mail(
                'Payment Completed - Aarambha Foundation',
                f'Dear {payment.sponsor.get_full_name() or payment.sponsor.email},\n\nYour sponsorship payment of Rs. {payment.amount} for {payment.child.full_name} has been completed.\n\nInstallment: #{payment.installment_number}\n\nThank you for your continued support!\n\nBest regards,\nAarambha Foundation Team',
                settings.EMAIL_HOST_USER,
                [payment.sponsor.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f'Email error: {e}')
        
        return Response({'message': 'Payment marked as completed successfully'})
    except PaymentInstallment.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_one_rupee_campaign(request):
    """Enroll user in One Rupee Day Campaign"""
    from django.core.mail import send_mail
    from django.conf import settings
    from notices.models import UserNotification
    from datetime import date, timedelta
    
    try:
        # Check if user already enrolled
        existing_campaign = OneRupeeCampaign.objects.filter(user=request.user, status='active').first()
        if existing_campaign:
            return Response({'error': 'You are already enrolled in the One Rupee Campaign'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user profile info if available
        user_profile = None
        try:
            from applications.models import Application
            user_profile = Application.objects.filter(user=request.user).first()
        except:
            pass
        
        # Create campaign enrollment
        campaign = OneRupeeCampaign.objects.create(
            user=request.user,
            full_name=request.data.get('full_name') or (user_profile.full_name if user_profile else request.user.get_full_name()),
            email=request.data.get('email') or request.user.email,
            phone=request.data.get('phone') or (user_profile.phone if user_profile else ''),
            country=request.data.get('country', 'Nepal'),
            city=request.data.get('city', ''),
            address=request.data.get('address', ''),
            occupation=request.data.get('occupation', ''),
            organization=request.data.get('organization', ''),
            next_payment_date=date.today() + timedelta(days=365)
        )
        
        # Create notification
        UserNotification.objects.create(
            user=request.user,
            notification_type='campaign_enrolled',
            title='One Rupee Campaign Enrollment',
            message='You have successfully enrolled in the One Rupee a Day Campaign. Please complete your first year payment to activate your participation.'
        )
        
        # Send email
        try:
            send_mail(
                'Welcome to One Rupee a Day Campaign - Aarambha Foundation',
                f'Dear {campaign.full_name},\n\nThank you for enrolling in our One Rupee a Day Campaign!\n\nYour contribution of Rs. 365 per year will help provide education support to underprivileged children.\n\nPlease complete your first year payment to activate your participation.\n\nBest regards,\nAarambha Foundation Team',
                settings.EMAIL_HOST_USER,
                [campaign.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f'Email error: {e}')
        
        return Response({
            'message': 'Successfully enrolled in One Rupee Campaign',
            'campaign_id': campaign.id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_campaign_payment(request, campaign_id):
    """Initiate Khalti payment for One Rupee Campaign"""
    import requests
    import uuid
    from django.conf import settings
    
    try:
        campaign = OneRupeeCampaign.objects.get(id=campaign_id, user=request.user)
        
        # Get current year
        from datetime import date
        current_year = date.today().year
        
        # Check if payment already exists for this year
        existing_payment = CampaignPayment.objects.filter(
            campaign=campaign, 
            payment_year=current_year,
            status='completed'
        ).first()
        
        if existing_payment:
            return Response({'error': 'Payment already completed for this year'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or get payment record
        payment, created = CampaignPayment.objects.get_or_create(
            campaign=campaign,
            payment_year=current_year,
            defaults={'amount': campaign.annual_amount}
        )
        
        # Generate unique purchase order ID
        purchase_order_id = f"CAMPAIGN-{campaign.id}-{payment.id}-{uuid.uuid4().hex[:8].upper()}"
        
        # Use sandbox credentials
        khalti_secret_key = "05bf95cc57244045b8df5fad06748dab"
        
        # Get return URL
        base_url = request.build_absolute_uri('/').rstrip('/')
        return_url = f"{base_url}/api/applications/campaign-payment/{payment.id}/verify/"
        website_url = base_url
        
        # Prepare Khalti payment payload
        khalti_payload = {
            "return_url": return_url,
            "website_url": website_url,
            "amount": int(campaign.annual_amount * 100),  # Convert to paisa
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": f"One Rupee Campaign - Year {current_year} - {campaign.full_name}",
            "customer_info": {
                "name": campaign.full_name,
                "email": campaign.email,
                "phone": campaign.phone if campaign.phone else "9800000001"
            }
        }
        
        # Make request to Khalti SANDBOX API
        khalti_url = "https://dev.khalti.com/api/v2/epayment/initiate/"
        headers = {
            'Authorization': f'key {khalti_secret_key}',
            'Content-Type': 'application/json',
        }
        
        response = requests.post(khalti_url, json=khalti_payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            khalti_response = response.json()
            
            # Update payment with Khalti response
            payment.khalti_payment_token = khalti_response.get('pidx')
            payment.save()
            
            return Response({
                'success': True,
                'payment_id': payment.id,
                'purchase_order_id': purchase_order_id,
                'pidx': khalti_response.get('pidx'),
                'payment_url': khalti_response.get('payment_url'),
                'expires_at': khalti_response.get('expires_at'),
                'expires_in': khalti_response.get('expires_in')
            }, status=status.HTTP_200_OK)
        else:
            error_data = response.json() if response.content else {'error': 'Unknown error'}
            return Response({
                'error': 'Failed to initiate payment with Khalti',
                'details': error_data
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except OneRupeeCampaign.DoesNotExist:
        return Response({'error': 'Campaign not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def verify_campaign_payment(request, payment_id):
    """Verify Khalti payment for One Rupee Campaign"""
    import requests
    from django.conf import settings
    from django.utils import timezone
    from django.core.mail import send_mail
    from notices.models import UserNotification
    from django.shortcuts import redirect
    
    try:
        pidx = request.GET.get('pidx') or request.data.get('pidx')
        
        if not pidx:
            return Response({'error': 'pidx is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Find payment by pidx
        try:
            payment = CampaignPayment.objects.get(khalti_payment_token=pidx, campaign__user=request.user)
        except CampaignPayment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # If already verified, redirect to campaign page
        if payment.status == 'completed':
            if request.method == 'GET':
                return redirect('/enroll-one-rupee-day-campaign/')
            return Response({
                'success': True,
                'payment_id': payment.id,
                'status': 'completed',
                'transaction_id': payment.khalti_transaction_id,
                'amount': str(payment.amount),
                'payment_completed': True,
                'message': 'Payment already verified'
            }, status=status.HTTP_200_OK)
        
        # Use Khalti lookup API
        khalti_secret_key = "05bf95cc57244045b8df5fad06748dab"
        khalti_url = "https://dev.khalti.com/api/v2/epayment/lookup/"
        headers = {
            'Authorization': f'key {khalti_secret_key}',
            'Content-Type': 'application/json',
        }
        
        lookup_payload = {"pidx": pidx}
        response = requests.post(khalti_url, json=lookup_payload, headers=headers)
        
        if response.status_code == 200:
            khalti_response = response.json()
            payment_status = khalti_response.get('status', '').lower()
            
            if payment_status == 'completed':
                payment.status = 'completed'
                payment.payment_date = timezone.now()
                payment.khalti_transaction_id = khalti_response.get('transaction_id')
                payment.save()
                
                # Update campaign
                campaign = payment.campaign
                campaign.total_paid += payment.amount
                campaign.payments_count += 1
                campaign.last_payment_date = timezone.now().date()
                campaign.save()
                
                # Create notification
                UserNotification.objects.create(
                    user=request.user,
                    notification_type='payment_completed',
                    title='One Rupee Campaign Payment Completed!',
                    message=f'Your payment of Rs. {payment.amount} for One Rupee Campaign (Year {payment.payment_year}) has been completed successfully. Transaction ID: {payment.khalti_transaction_id}'
                )
                
                # Send email
                try:
                    send_mail(
                        'One Rupee Campaign Payment Completed - Aarambha Foundation',
                        f'Dear {campaign.full_name},\n\nYour One Rupee Campaign payment of Rs. {payment.amount} for year {payment.payment_year} has been completed successfully.\n\nTransaction ID: {payment.khalti_transaction_id}\n\nThank you for your continued support in transforming children\'s lives through education!\n\nBest regards,\nAarambha Foundation Team',
                        settings.EMAIL_HOST_USER,
                        [campaign.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f'Email error: {e}')
            
            # If GET request (callback), redirect to campaign page
            if request.method == 'GET':
                return redirect('/enroll-one-rupee-day-campaign/')
            
            return Response({
                'success': True,
                'payment_id': payment.id,
                'status': payment_status,
                'transaction_id': khalti_response.get('transaction_id'),
                'amount': str(payment.amount),
                'payment_completed': payment.status == 'completed'
            }, status=status.HTTP_200_OK)
        else:
            error_data = response.json() if response.content else {'error': 'Unknown error'}
            if request.method == 'GET':
                return redirect('/enroll-one-rupee-day-campaign/?error=payment_verification_failed')
            return Response({
                'error': 'Failed to verify payment with Khalti',
                'details': error_data
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        if request.method == 'GET':
            return redirect('/enroll-one-rupee-day-campaign/?error=payment_error')
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_campaign_status(request):
    """Get user's One Rupee Campaign status"""
    try:
        campaign = OneRupeeCampaign.objects.filter(user=request.user).first()
        
        if not campaign:
            return Response({'enrolled': False})
        
        # Get payment history
        payments = CampaignPayment.objects.filter(campaign=campaign).order_by('-payment_year')
        
        payment_data = []
        for payment in payments:
            payment_data.append({
                'id': payment.id,
                'year': payment.payment_year,
                'amount': str(payment.amount),
                'status': payment.status,
                'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
                'transaction_id': payment.khalti_transaction_id
            })
        
        return Response({
            'enrolled': True,
            'campaign': {
                'id': campaign.id,
                'status': campaign.status,
                'start_date': campaign.start_date.isoformat(),
                'total_paid': str(campaign.total_paid),
                'payments_count': campaign.payments_count,
                'last_payment_date': campaign.last_payment_date.isoformat() if campaign.last_payment_date else None
            },
            'payments': payment_data
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_campaign_stats(request):
    """Get campaign statistics for admin dashboard"""
    if not request.user.is_superuser:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from django.db.models import Sum
        from datetime import date
        
        current_year = date.today().year
        all_campaigns = OneRupeeCampaign.objects.all()
        
        stats = {
            'total_participants': all_campaigns.count(),
            'active_campaigns': all_campaigns.filter(status='active').count(),
            'total_collected': float(all_campaigns.aggregate(total=Sum('total_paid'))['total'] or 0),
            'this_year_payments': CampaignPayment.objects.filter(payment_year=current_year, status='completed').count()
        }
        
        return Response(stats)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_campaign_list(request):
    """Get paginated list of all campaigns for admin"""
    if not request.user.is_superuser:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from django.core.paginator import Paginator
        from django.db.models import Q
        
        campaigns = OneRupeeCampaign.objects.order_by('-created_at')
        
        search = request.GET.get('search', '')
        status_filter = request.GET.get('status', '')
        
        if search:
            campaigns = campaigns.filter(
                Q(full_name__icontains=search) | Q(email__icontains=search)
            )
        
        if status_filter:
            campaigns = campaigns.filter(status=status_filter)
        
        paginator = Paginator(campaigns, 20)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        data = []
        for campaign in page_obj:
            data.append({
                'id': campaign.id,
                'full_name': campaign.full_name,
                'email': campaign.email,
                'phone': campaign.phone,
                'country': campaign.country,
                'city': campaign.city,
                'occupation': campaign.occupation,
                'status': campaign.status,
                'total_paid': str(campaign.total_paid),
                'payments_count': campaign.payments_count,
                'last_payment_date': campaign.last_payment_date.isoformat() if campaign.last_payment_date else None
            })
        
        return Response({
            'results': data,
            'count': paginator.count,
            'next': page_obj.has_next(),
            'previous': page_obj.has_previous()
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_campaign_detail(request, campaign_id):
    """Get detailed campaign information for admin"""
    if not request.user.is_superuser:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        campaign = OneRupeeCampaign.objects.get(id=campaign_id)
        payments = CampaignPayment.objects.filter(campaign=campaign).order_by('-payment_year')
        
        payment_data = []
        for payment in payments:
            payment_data.append({
                'year': payment.payment_year,
                'amount': str(payment.amount),
                'status': payment.status,
                'payment_date': payment.payment_date.isoformat() if payment.payment_date else None
            })
        
        data = {
            'id': campaign.id,
            'full_name': campaign.full_name,
            'email': campaign.email,
            'phone': campaign.phone,
            'country': campaign.country,
            'city': campaign.city,
            'occupation': campaign.occupation,
            'organization': campaign.organization,
            'status': campaign.status,
            'total_paid': str(campaign.total_paid),
            'payments_count': campaign.payments_count,
            'last_payment_date': campaign.last_payment_date.isoformat() if campaign.last_payment_date else None,
            'start_date': campaign.start_date.isoformat(),
            'payments': payment_data
        }
        
        return Response(data)
    except OneRupeeCampaign.DoesNotExist:
        return Response({'error': 'Campaign not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_birthday_campaign(request):
    """Create a new birthday campaign"""
    try:
        from .models import BirthdayCampaign
        from notices.models import UserNotification
        from django.core.mail import send_mail
        from django.conf import settings

        data = request.data

        # Create campaign
        campaign = BirthdayCampaign.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=data.get('full_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            birthday_date=data.get('birthday_date'),
            target_amount=data.get('target_amount'),
            title=data.get('title'),
            description=data.get('description')
        )

        # Handle file uploads
        if request.FILES.get('profile_photo'):
            campaign.profile_photo = request.FILES['profile_photo']

        if request.FILES.get('photo'):
            campaign.photo = request.FILES['photo']

        campaign.save()

        # Create notification if user is authenticated
        if request.user.is_authenticated:
            UserNotification.objects.create(
                user=request.user,
                notification_type='campaign_created',
                title='Birthday Campaign Created!',
                message=f'Your birthday campaign "{campaign.title}" has been created successfully.'
            )

        # Send email
        try:
            send_mail(
                'Birthday Campaign Created - Aarambha Foundation',
                f'Dear {campaign.full_name},\n\nYour birthday campaign "{campaign.title}" has been created successfully!\n\nTarget Amount: Rs. {campaign.target_amount}\nBirthday Date: {campaign.birthday_date}\n\nShare your campaign with friends and family to start collecting donations.\n\nBest regards,\nAarambha Foundation Team',
                settings.EMAIL_HOST_USER,
                [campaign.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f'Email error: {e}')

        return Response({
            'success': True,
            'campaign_id': campaign.id,
            'message': 'Birthday campaign created successfully!'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_birthday_campaign(request, campaign_id):
    """Get birthday campaign details"""
    try:
        from .models import BirthdayCampaign, BirthdayDonation
        
        campaign = BirthdayCampaign.objects.get(id=campaign_id)
        donations = BirthdayDonation.objects.filter(campaign=campaign, status='completed').order_by('-created_at')
        
        donation_data = []
        for donation in donations:
            donation_data.append({
                'donor_name': 'Anonymous' if donation.is_anonymous else donation.donor_name,
                'amount': str(donation.amount),
                'message': donation.message,
                'date': donation.payment_date.isoformat() if donation.payment_date else donation.created_at.isoformat()
            })
        
        data = {
            'id': campaign.id,
            'full_name': campaign.full_name,
            'title': campaign.title,
            'description': campaign.description,
            'birthday_date': campaign.birthday_date.isoformat(),
            'target_amount': str(campaign.target_amount),
            'current_amount': str(campaign.current_amount),
            'progress_percentage': campaign.get_progress_percentage(),
            'donors_count': campaign.donors_count,
            'status': campaign.status,
            'photo': campaign.photo.url if campaign.photo else None,
            'donations': donation_data
        }
        
        return Response(data)
        
    except BirthdayCampaign.DoesNotExist:
        return Response({'error': 'Campaign not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def donate_to_birthday_campaign(request, campaign_id):
    """Make a donation to birthday campaign"""
    try:
        from .models import BirthdayCampaign, BirthdayDonation
        import requests
        from django.conf import settings
        
        campaign = BirthdayCampaign.objects.get(id=campaign_id)
        data = request.data
        
        # Create donation record
        donation = BirthdayDonation.objects.create(
            campaign=campaign,
            donor_name=data.get('donor_name'),
            donor_email=data.get('donor_email'),
            donor_phone=data.get('donor_phone', ''),
            amount=data.get('amount'),
            message=data.get('message', ''),
            is_anonymous=data.get('is_anonymous', False)
        )
        
        # Initiate Khalti payment
        khalti_data = {
            'return_url': f'{getattr(settings, "FRONTEND_URL", "http://127.0.0.1:8000")}/birthday-campaign/{campaign_id}/',
            'website_url': getattr(settings, 'FRONTEND_URL', 'http://127.0.0.1:8000'),
            'amount': int(float(donation.amount) * 100),
            'purchase_order_id': f'BD_{donation.id}_{timezone.now().strftime("%Y%m%d%H%M%S")}',
            'purchase_order_name': f'Birthday Donation - {campaign.title}',
            'customer_info': {
                'name': donation.donor_name,
                'email': donation.donor_email,
                'phone': donation.donor_phone or '9800000000'
            }
        }
        
        # Use sandbox credentials for testing
        khalti_secret_key = "05bf95cc57244045b8df5fad06748dab"  # Test key from docs
        
        response = requests.post(
            'https://dev.khalti.com/api/v2/epayment/initiate/',
            json=khalti_data,
            headers={
                'Authorization': f'key {khalti_secret_key}',
                'Content-Type': 'application/json',
            },
            timeout=30
        )
        
        if response.status_code == 200:
            khalti_response = response.json()
            donation.khalti_payment_token = khalti_response.get('pidx')
            donation.save()
            
            return Response({
                'success': True,
                'payment_url': khalti_response.get('payment_url'),
                'donation_id': donation.id
            })
        else:
            return Response({'error': 'Failed to initiate payment'}, status=status.HTTP_400_BAD_REQUEST)
            
    except BirthdayCampaign.DoesNotExist:
        return Response({'error': 'Campaign not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def verify_birthday_donation(request):
    """Verify birthday donation payment with Khalti"""
    try:
        from .models import BirthdayDonation
        from notices.models import UserNotification
        from django.core.mail import send_mail
        from django.conf import settings
        import requests
        
        pidx = request.GET.get('pidx') or request.data.get('pidx')
        
        if not pidx:
            return Response({'error': 'Payment token not provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        donation = BirthdayDonation.objects.get(khalti_payment_token=pidx)
        
        # If already completed, return success
        if donation.status == 'completed':
            return Response({
                'success': True,
                'donation_id': donation.id,
                'status': 'completed',
                'transaction_id': donation.khalti_transaction_id,
                'amount': str(donation.amount),
                'message': 'Payment already verified'
            })
        
        # Verify with Khalti using sandbox API
        khalti_secret_key = "05bf95cc57244045b8df5fad06748dab"  # Test key from docs
        
        response = requests.post(
            'https://dev.khalti.com/api/v2/epayment/lookup/',
            json={'pidx': pidx},
            headers={
                'Authorization': f'key {khalti_secret_key}',
                'Content-Type': 'application/json',
            },
            timeout=30
        )
        
        if response.status_code == 200:
            khalti_response = response.json()
            payment_status = khalti_response.get('status', '')
            
            print(f"Khalti response status: {khalti_response.get('status')}")
            print(f"Payment status: {payment_status}")
            
            if payment_status == 'Completed':
                donation.status = 'completed'
                donation.khalti_transaction_id = khalti_response.get('transaction_id')
                donation.payment_date = timezone.now()
                donation.save()
                
                # Update campaign totals
                campaign = donation.campaign
                campaign.current_amount += donation.amount
                campaign.donors_count += 1

                # Check if campaign target is reached
                if campaign.current_amount >= campaign.target_amount and campaign.status == 'active':
                    campaign.status = 'completed'

                campaign.save()
                
                # Send emails
                try:
                    # Email to donor
                    send_mail(
                        f'Thank You for Your Birthday Donation - {campaign.title}',
                        f'Dear {donation.donor_name},\n\nThank you for your generous donation of Rs. {donation.amount} to {campaign.full_name}\'s birthday campaign "{campaign.title}".\n\nYour contribution will make a real difference in children\'s lives!\n\nTransaction ID: {donation.khalti_transaction_id}\n\nBest regards,\nAarambha Foundation Team',
                        settings.EMAIL_HOST_USER,
                        [donation.donor_email],
                        fail_silently=True,
                    )
                    
                    # Email to campaign owner
                    send_mail(
                        f'New Donation Received - {campaign.title}',
                        f'Dear {campaign.full_name},\n\nGreat news! You received a new donation for your birthday campaign.\n\nDonor: {"Anonymous" if donation.is_anonymous else donation.donor_name}\nAmount: Rs. {donation.amount}\nMessage: {donation.message}\n\nCurrent Progress: Rs. {campaign.current_amount} / Rs. {campaign.target_amount}\n\nBest regards,\nAarambha Foundation Team',
                        settings.EMAIL_HOST_USER,
                        [campaign.email],
                        fail_silently=True,
                    )
                except Exception as e:
                    print(f'Email error: {e}')
            
            if request.method == 'GET':
                return redirect(f'/birthday-campaign/{donation.campaign.id}/')
            
            return Response({
                'success': True,
                'donation_id': donation.id,
                'status': 'completed' if payment_status == 'Completed' else 'pending',
                'transaction_id': khalti_response.get('transaction_id'),
                'amount': str(donation.amount)
            })
        else:
            if request.method == 'GET':
                return redirect(f'/birthday-campaign/{donation.campaign.id}/?error=payment_failed')
            return Response({'error': 'Payment verification failed'}, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        if request.method == 'GET':
            return redirect('/celebrate-birthday/?error=payment_error')
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def admin_birthday_campaign_stats(request):
    """Get birthday campaign statistics for admin dashboard"""
    if not request.user.is_superuser:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from .models import BirthdayCampaign, BirthdayDonation
        from django.db.models import Sum, Count
        
        all_campaigns = BirthdayCampaign.objects.all()
        all_donations = BirthdayDonation.objects.filter(status='completed')
        
        stats = {
            'total_campaigns': all_campaigns.count(),
            'active_campaigns': all_campaigns.filter(status='active').count(),
            'total_raised': float(all_donations.aggregate(total=Sum('amount'))['total'] or 0),
            'total_donors': all_donations.count()
        }
        
        return Response(stats)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_active_birthday_campaigns(request):
    """Get list of active birthday campaigns for public display"""
    try:
        from .models import BirthdayCampaign
        from django.core.paginator import Paginator

        # Get only active campaigns, ordered by creation date (newest first)
        campaigns = BirthdayCampaign.objects.filter(status='active').order_by('-created_at')

        # Optional: limit to recent campaigns or those with some donations
        # campaigns = campaigns.filter(current_amount__gt=0)  # Uncomment to show only campaigns with donations

        # Limit to first 20 for performance
        campaigns = campaigns[:20]

        data = []
        for campaign in campaigns:
            data.append({
                'id': campaign.id,
                'full_name': campaign.full_name,
                'title': campaign.title,
                'description': campaign.description,
                'birthday_date': campaign.birthday_date.isoformat(),
                'target_amount': str(campaign.target_amount),
                'current_amount': str(campaign.current_amount),
                'progress_percentage': campaign.get_progress_percentage(),
                'donors_count': campaign.donors_count,
                'photo': campaign.photo.url if campaign.photo else None,
                'profile_photo': campaign.profile_photo.url if campaign.profile_photo else None
            })

        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def admin_birthday_campaign_list(request):
    """Get paginated list of all birthday campaigns for admin"""
    if not request.user.is_superuser:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from .models import BirthdayCampaign
        from django.core.paginator import Paginator
        from django.db.models import Q
        
        campaigns = BirthdayCampaign.objects.order_by('-created_at')
        
        search = request.GET.get('search', '')
        status_filter = request.GET.get('status', '')
        
        if search:
            campaigns = campaigns.filter(
                Q(full_name__icontains=search) | Q(title__icontains=search)
            )
        
        if status_filter:
            campaigns = campaigns.filter(status=status_filter)
        
        paginator = Paginator(campaigns, 20)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        data = []
        for campaign in page_obj:
            data.append({
                'id': campaign.id,
                'full_name': campaign.full_name,
                'email': campaign.email,
                'phone': campaign.phone,
                'title': campaign.title,
                'birthday_date': campaign.birthday_date.isoformat(),
                'target_amount': str(campaign.target_amount),
                'current_amount': str(campaign.current_amount),
                'progress_percentage': campaign.get_progress_percentage(),
                'donors_count': campaign.donors_count,
                'status': campaign.status,
                'created_at': campaign.created_at.isoformat()
            })
        
        return Response({
            'results': data,
            'count': paginator.count,
            'next': page_obj.has_next(),
            'previous': page_obj.has_previous()
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
