from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .models import Event, EventParticipation, EventCertificate
from users.models import CustomUser
from branches.models import Branch
import json

@login_required
def admin_events(request):
    """Admin events management page"""
    if not (request.user.is_superuser or request.user.user_type == 'superadmin'):
        return redirect('login')
    
    events = Event.objects.all().order_by('-created_at')
    branches = Branch.objects.all()
    users = CustomUser.objects.filter(user_type__in=['member', 'volunteer'])
    
    # Add attended count to events
    for event in events:
        event.attended_count = EventParticipation.objects.filter(event=event, attended=True).count()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_event':
            try:
                # Create new event
                event = Event.objects.create(
                    title=request.POST.get('title'),
                    description=request.POST.get('description'),
                    event_type=request.POST.get('event_type'),
                    venue_type=request.POST.get('venue_type'),
                    venue_name=request.POST.get('venue_name', ''),
                    venue_address=request.POST.get('venue_address', ''),
                    meeting_link=request.POST.get('meeting_link', ''),
                    meeting_id=request.POST.get('meeting_id', ''),
                    meeting_password=request.POST.get('meeting_password', ''),
                    contact_person=request.POST.get('contact_person', ''),
                    contact_phone=request.POST.get('contact_phone', ''),
                    contact_email=request.POST.get('contact_email', ''),
                    start_datetime=request.POST.get('start_datetime'),
                    end_datetime=request.POST.get('end_datetime'),
                    user_type=request.POST.get('user_type'),
                    assignment_mode=request.POST.get('assignment_mode'),
                    requires_application=request.POST.get('requires_application') == 'on',
                    max_participants=request.POST.get('max_participants') or None,
                    created_by=request.user
                )
                
                # Handle assignments
                if event.assignment_mode == 'branch':
                    branch_id = request.POST.get('branch')
                    if branch_id:
                        event.branch_id = branch_id
                        event.save()
                elif event.assignment_mode in ['individual', 'branch_individual']:
                    assigned_users = request.POST.getlist('assigned_to')
                    event.assigned_to.set(assigned_users)
                    if event.assignment_mode == 'branch_individual':
                        branch_id = request.POST.get('branch')
                        if branch_id:
                            event.branch_id = branch_id
                            event.save()
                
                messages.success(request, 'Event created successfully!')
                
            except Exception as e:
                messages.error(request, f'Error creating event: {str(e)}')
        
        elif action == 'update_event':
            try:
                event_id = request.POST.get('event_id')
                event = get_object_or_404(Event, id=event_id)
                
                # Update event fields
                event.title = request.POST.get('title')
                event.description = request.POST.get('description')
                event.event_type = request.POST.get('event_type')
                event.venue_type = request.POST.get('venue_type')
                event.venue_name = request.POST.get('venue_name', '')
                event.venue_address = request.POST.get('venue_address', '')
                event.meeting_link = request.POST.get('meeting_link', '')
                event.meeting_id = request.POST.get('meeting_id', '')
                event.meeting_password = request.POST.get('meeting_password', '')
                event.contact_person = request.POST.get('contact_person', '')
                event.contact_phone = request.POST.get('contact_phone', '')
                event.contact_email = request.POST.get('contact_email', '')
                event.start_datetime = request.POST.get('start_datetime')
                event.end_datetime = request.POST.get('end_datetime')
                event.user_type = request.POST.get('user_type')
                event.assignment_mode = request.POST.get('assignment_mode')
                event.requires_application = request.POST.get('requires_application') == 'on'
                event.max_participants = request.POST.get('max_participants') or None
                event.is_active = request.POST.get('is_active') == 'on'
                
                # Clear previous assignments
                event.assigned_to.clear()
                event.branch = None
                
                # Handle new assignments
                if event.assignment_mode == 'branch':
                    branch_id = request.POST.get('branch')
                    if branch_id:
                        event.branch_id = branch_id
                elif event.assignment_mode in ['individual', 'branch_individual']:
                    assigned_users = request.POST.getlist('assigned_to')
                    event.assigned_to.set(assigned_users)
                    if event.assignment_mode == 'branch_individual':
                        branch_id = request.POST.get('branch')
                        if branch_id:
                            event.branch_id = branch_id
                
                event.save()
                messages.success(request, 'Event updated successfully!')
                
            except Exception as e:
                messages.error(request, f'Error updating event: {str(e)}')
        
        elif action == 'delete_event':
            try:
                event_id = request.POST.get('event_id')
                event = get_object_or_404(Event, id=event_id)
                event.delete()
                messages.success(request, 'Event deleted successfully!')
            except Exception as e:
                messages.error(request, f'Error deleting event: {str(e)}')
    
    context = {
        'events': events,
        'branches': branches,
        'users': users,
    }
    return render(request, 'admin/event_management.html', context)

@login_required
def admin_event_participations(request, event_id):
    """Admin view for managing event participations"""
    if not (request.user.is_superuser or request.user.user_type == 'superadmin'):
        return redirect('login')
    
    event = get_object_or_404(Event, id=event_id)
    participations = EventParticipation.objects.filter(event=event).order_by('-applied_at')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_participation':
            participation_id = request.POST.get('participation_id')
            participation = get_object_or_404(EventParticipation, id=participation_id)
            old_status = participation.status
            
            participation.status = request.POST.get('status')
            participation.admin_notes = request.POST.get('admin_notes', '')
            participation.save()
            
            # Send notification and email if status changed
            if old_status != participation.status and participation.status in ['approved', 'rejected']:
                from notices.models import UserNotification
                
                if participation.status == 'approved':
                    UserNotification.objects.create(
                        user=participation.user,
                        notification_type='event_approved',
                        title=f'Event Approved: {participation.event.title}',
                        message=f'Your application for "{participation.event.title}" has been approved!'
                    )
                    
                    # Send approval email
                    from django.core.mail import send_mail
                    try:
                        subject = f'🎉 Event Approved: {participation.event.title}'
                        message = f'''Dear {participation.user.first_name or participation.user.email},

Great news! Your application for "{participation.event.title}" has been approved.

📅 Event: {participation.event.title}
📍 Date: {participation.event.start_datetime.strftime("%B %d, %Y at %I:%M %p")}

Please mark your calendar.

Best regards,
Aarambha Foundation Team'''
                        
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[participation.user.email],
                            fail_silently=True,
                        )
                    except:
                        pass
                        
                elif participation.status == 'rejected':
                    UserNotification.objects.create(
                        user=participation.user,
                        notification_type='event_rejected',
                        title=f'Event Rejected: {participation.event.title}',
                        message=f'Your application for "{participation.event.title}" has been rejected.'
                    )
            
            messages.success(request, 'Participation updated successfully!')
        
        elif action == 'mark_attendance':
            participation_ids = request.POST.getlist('participation_ids')
            attended_ids = request.POST.getlist('attended')
            
            for participation_id in participation_ids:
                participation = get_object_or_404(EventParticipation, id=participation_id)
                participation.attended = str(participation_id) in attended_ids
                participation.attendance_marked_by = request.user
                participation.attendance_marked_at = timezone.now()
                participation.save()
            
            messages.success(request, 'Attendance marked successfully!')
    
    context = {
        'event': event,
        'participations': participations,
    }
    return render(request, 'admin/event_participations.html', context)

@login_required
def member_events(request):
    """Member/Volunteer events page"""
    from django.db.models import Avg, Count
    user = request.user
    
    # Get events assigned to user
    assigned_events = Event.objects.filter(
        Q(assignment_mode='all') |
        Q(assigned_to=user) |
        Q(branch=user.branch if hasattr(user, 'branch') else None),
        is_active=True
    ).filter(
        Q(user_type='both') |
        Q(user_type=user.user_type)
    ).distinct().order_by('-start_datetime')
    
    # Get user's participations
    user_participations = EventParticipation.objects.filter(user=user)
    participation_dict = {p.event_id: p for p in user_participations}
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'apply_event':
            event_id = request.POST.get('event_id')
            event = get_object_or_404(Event, id=event_id)
            application_message = request.POST.get('application_message', '')
            
            # Check if user already applied
            if EventParticipation.objects.filter(event=event, user=user).exists():
                messages.warning(request, 'You have already applied for this event!')
            else:
                # Create participation
                status = 'approved' if not event.requires_application else 'applied'
                EventParticipation.objects.create(
                    event=event,
                    user=user,
                    status=status,
                    application_message=application_message
                )
                
                # Create notification
                from notices.models import UserNotification
                UserNotification.objects.create(
                    user=user,
                    notification_type='event_applied',
                    title=f'Event Application: {event.title}',
                    message=f'Your application for "{event.title}" has been submitted successfully.'
                )
                
                # Send email
                from django.core.mail import send_mail
                try:
                    subject = f'✅ Event Application: {event.title}'
                    message = f'''Dear {user.first_name or user.email},

Your application for "{event.title}" has been submitted successfully.

📅 Event: {event.title}
📍 Date: {event.start_datetime.strftime("%B %d, %Y at %I:%M %p")}

{'You will be notified once reviewed.' if event.requires_application else 'You are now registered!'}

Best regards,
Aarambha Foundation Team'''
                    
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[user.email],
                        fail_silently=True,
                    )
                except:
                    pass
                
                if event.requires_application:
                    messages.success(request, 'Application submitted successfully! Wait for admin approval.')
                else:
                    messages.success(request, 'You have been registered for the event!')
        
        elif action == 'submit_review':
            event_id = request.POST.get('event_id')
            rating = request.POST.get('rating')
            review_text = request.POST.get('review', '')
            
            try:
                event = get_object_or_404(Event, id=event_id)
                participation = EventParticipation.objects.get(event=event, user=user)
                
                if participation.attended:
                    participation.rating = int(rating) if rating else None
                    participation.review = review_text
                    participation.save()
                    messages.success(request, 'Thank you for your review!')
                else:
                    messages.error(request, 'You can only review events you attended.')
            except EventParticipation.DoesNotExist:
                messages.error(request, 'Participation not found.')
            except Exception as e:
                messages.error(request, f'Error submitting review: {str(e)}')
    
    # Add participation status and review stats to events
    for event in assigned_events:
        event.user_participation = participation_dict.get(event.id)
        
        # Calculate review statistics
        reviews = EventParticipation.objects.filter(event=event, review__isnull=False).exclude(review='')
        event.review_count = reviews.count()
        event.avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
    
    context = {
        'events': assigned_events,
    }
    
    # Determine template based on user type
    if user.user_type == 'member':
        return render(request, 'member/events.html', context)
    else:
        return render(request, 'volunteer/events.html', context)

@login_required
def get_event_details(request, event_id):
    """API endpoint to get event details"""
    event = get_object_or_404(Event, id=event_id)
    
    data = {
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'event_type': event.event_type,
        'venue_type': event.venue_type,
        'venue_name': event.venue_name or '',
        'venue_address': event.venue_address or '',
        'meeting_link': event.meeting_link or '',
        'meeting_id': event.meeting_id or '',
        'meeting_password': event.meeting_password or '',
        'contact_person': event.contact_person or '',
        'contact_phone': event.contact_phone or '',
        'contact_email': event.contact_email or '',
        'start_datetime': event.start_datetime.strftime('%Y-%m-%dT%H:%M'),
        'end_datetime': event.end_datetime.strftime('%Y-%m-%dT%H:%M'),
        'user_type': event.user_type,
        'assignment_mode': event.assignment_mode,
        'requires_application': event.requires_application,
        'max_participants': event.max_participants or '',
        'is_active': event.is_active,
        'branch_id': event.branch_id or '',
        'assigned_to': list(event.assigned_to.values_list('id', flat=True)),
    }
    
    return JsonResponse(data)

@login_required
def event_reviews(request, event_id):
    """Public event reviews page for members/volunteers"""
    event = get_object_or_404(Event, id=event_id)
    reviews = EventParticipation.objects.filter(
        event=event, 
        review__isnull=False
    ).exclude(review='').select_related('user').order_by('-rating', '-id')
    
    context = {
        'event': event,
        'reviews': reviews,
    }
    
    # Determine template based on user type
    if request.user.user_type == 'member':
        return render(request, 'member/event_reviews.html', context)
    else:
        return render(request, 'volunteer/event_reviews.html', context)

@login_required
def event_certificate(request, event_id):
    """Generate and display event attendance certificate"""
    from django.http import HttpResponse
    from django.template.loader import render_to_string
    import uuid
    
    event = get_object_or_404(Event, id=event_id)
    try:
        participation = EventParticipation.objects.get(event=event, user=request.user, attended=True)
    except EventParticipation.DoesNotExist:
        messages.error(request, 'Certificate not available. You must have attended this event.')
        return redirect('member_events')
    
    # Generate certificate ID if not exists
    if not hasattr(participation, 'certificate_id') or not participation.certificate_id:
        participation.certificate_id = str(uuid.uuid4())[:8].upper()
        participation.save()
    
    context = {
        'event': event,
        'user': request.user,
        'participation': participation,
        'certificate_date': participation.attendance_marked_at or event.end_datetime,
    }
    
    return render(request, 'events/certificate.html', context)