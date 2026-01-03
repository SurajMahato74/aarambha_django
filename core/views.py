from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from .districts import NEPAL_DISTRICTS
from .models import (
    HeroSection, SupportCard, WhoWeAre, GrowingOurImpact, Statistics, Partner, 
    ContactInfo, Award, OurWork, RecommendationLetter, IndexEvent,
    BlogPost, BlogParagraph, BlogCategory, Donation
)
from decimal import Decimal

def website_home(request):
    hero_section = HeroSection.get_active()
    support_cards = SupportCard.get_active_cards()
    who_we_are = WhoWeAre.get_active()
    growing_our_impact = GrowingOurImpact.get_active()
    statistics = Statistics.get_active()
    partners = Partner.get_active_partners()
    contact_info = ContactInfo.get_active()
    awards = Award.get_active_awards()
    our_work_items = OurWork.get_active_works()
    
    # Get events for the index page from IndexEvent model
    events = IndexEvent.get_active_events()[:6]  # Show latest 6 events
    
    context = {
        'hero_section': hero_section,
        'support_cards': support_cards,
        'who_we_are': who_we_are,
        'growing_our_impact': growing_our_impact,
        'statistics': statistics,
        'partners': partners,
        'contact_info': contact_info,
        'awards': awards,
        'our_work_items': our_work_items,
        'events': events
    }
    return render(request, 'website/index.html', context)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse
from .models import OurWork, Donation
import requests
import uuid
from django.conf import settings
from decimal import Decimal

class OurWorkAPI(APIView):
    permission_classes = [AllowAny]  # Make this endpoint public

    def get(self, request):
        works = OurWork.get_active_works()  # Reuse your manager method
        data = [
            {
                'title': work.title,
                'url': request.build_absolute_uri(reverse('our_work_detail', args=[work.navlink])),
            }
            for work in works
        ]
        return Response(data)


class DonationCreateAPI(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # Create donation record
            donation = Donation.objects.create(
                title=request.data.get('title', 'Mr.'),
                full_name=request.data.get('full_name'),
                email=request.data.get('email'),
                phone=request.data.get('phone', ''),
                amount=Decimal(str(request.data.get('amount'))),
                program_name=request.data.get('program_name', ''),
                program_type=request.data.get('program_type', 'general'),
                purchase_order_id=f"DON-{uuid.uuid4().hex[:12].upper()}",
                payment_status='initiated'
            )
            
            # Initialize Khalti payment
            khalti_url = "https://dev.khalti.com/api/v2/epayment/initiate/"
            headers = {
                'Authorization': f'key {settings.KHALTI_SECRET_KEY}',
                'Content-Type': 'application/json',
            }
            
            payload = {
                "return_url": f"{settings.SITE_URL}/donation/callback/",
                "website_url": settings.SITE_URL,
                "amount": donation.amount_in_paisa,
                "purchase_order_id": donation.purchase_order_id,
                "purchase_order_name": f"Donation - {donation.program_name or 'General'}",
                "customer_info": {
                    "name": donation.full_name,
                    "email": donation.email,
                    "phone": donation.phone or "9800000000"
                }
            }
            
            response = requests.post(khalti_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                khalti_response = response.json()
                donation.pidx = khalti_response.get('pidx')
                donation.payment_url = khalti_response.get('payment_url')
                donation.save()
                
                return Response({
                    'success': True,
                    'donation_id': donation.id,
                    'payment_url': khalti_response.get('payment_url'),
                    'pidx': khalti_response.get('pidx')
                })
            else:
                donation.payment_status = 'failed'
                donation.save()
                return Response({'error': 'Payment initialization failed'}, status=400)
                
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class BlogCategoriesAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = BlogCategory.objects.filter(is_active=True)[:5]  # Limit to 5 for navbar
        data = [
            {
                'name': category.name,
                'url': request.build_absolute_uri(reverse('website_blogs')) + f'?category={category.slug}',
                'color': category.color,
            }
            for category in categories
        ]
        return Response(data)


@method_decorator(csrf_exempt, name='dispatch')
class BlogCreateAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # Create blog post
            blog_post = BlogPost.objects.create(
                title=request.data.get('title'),
                slug=request.data.get('slug') or slugify(request.data.get('title')),
                excerpt=request.data.get('excerpt'),
                featured_image=request.FILES.get('featured_image'),
                author=request.user if request.user.is_authenticated else None,
                status=request.data.get('status', 'draft'),
                is_featured=request.data.get('is_featured') == 'true'
            )
            
            # Add categories
            category_ids = request.data.getlist('categories')
            if category_ids:
                blog_post.categories.set(category_ids)
            
            # Create paragraphs if specified
            paragraph_count = int(request.data.get('paragraph_count', 3))
            for i in range(1, paragraph_count + 1):
                BlogParagraph.objects.create(
                    blog_post=blog_post,
                    order=i,
                    paragraph_type='text',
                    content=f'<p>Content for paragraph {i}. Edit this to add your content.</p>'
                )
            
            return Response({'id': blog_post.id, 'message': 'Blog post created successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        
def website_member_form(request):
    return render(request, 'website/member_form.html', {'districts': NEPAL_DISTRICTS})

def website_volunteer_form(request):
    return render(request, 'website/volunteer_form.html', {'districts': NEPAL_DISTRICTS})

def website_sponsor_child_form(request):
    return render(request, 'website/sponsor_child_form.html', {'districts': NEPAL_DISTRICTS})

def website_events(request):
    # Get all active IndexEvents for the events page
    events = IndexEvent.get_active_events()
    contact_info = ContactInfo.get_active()
    awards = Award.get_active_awards()
    
    context = {
        'events': events,
        'contact_info': contact_info,
        'awards': awards,
    }
    return render(request, 'website/events.html', context)

def website_event_detail(request, event_id):
    """Display event detail page"""
    event = get_object_or_404(IndexEvent, id=event_id, is_active=True)
    contact_info = ContactInfo.get_active()
    awards = Award.get_active_awards()
    
    context = {
        'event': event,
        'contact_info': contact_info,
        'awards': awards,
    }
    return render(request, 'website/event_detail.html', context)

def website_blogs(request):
    # Get published blog posts with categories
    blog_posts = BlogPost.get_published_posts()
    featured_posts = BlogPost.get_featured_posts()[:3]  # Show 3 featured posts
    categories = BlogCategory.objects.filter(is_active=True)
    
    # Filter by category if requested
    category_slug = request.GET.get('category')
    if category_slug:
        try:
            category = BlogCategory.objects.get(slug=category_slug, is_active=True)
            blog_posts = blog_posts.filter(categories=category)
        except BlogCategory.DoesNotExist:
            pass
    
    # Apply limit after filtering
    blog_posts = blog_posts[:12]  # Show latest 12 posts
    
    context = {
        'blog_posts': blog_posts,
        'featured_posts': featured_posts,
        'categories': categories,
        'selected_category': category_slug,
        'contact_info': ContactInfo.get_active(),
        'awards': Award.get_active_awards(),
    }
    return render(request, 'website/blogs.html', context)


def blog_detail(request, slug):
    """Display individual blog post with all paragraphs"""
    blog_post = get_object_or_404(BlogPost, slug=slug, status='published')
    paragraphs = blog_post.paragraphs.all().order_by('order')
    
    # Get related posts from same categories
    related_posts = BlogPost.get_published_posts().filter(
        categories__in=blog_post.categories.all()
    ).exclude(id=blog_post.id).distinct()[:3]
    
    context = {
        'blog_post': blog_post,
        'paragraphs': paragraphs,
        'related_posts': related_posts,
        'contact_info': ContactInfo.get_active(),
        'awards': Award.get_active_awards(),
    }
    return render(request, 'website/blog_detail.html', context)

def website_pravicy_policy(request):
    return render(request, 'website/privacy_policy.html')

def website_enrollDayCamping(request):
    return render(request, 'website/enrollDayCamping.html')

def website_celebratebirthday(request):
    return render(request, 'website/celebrateBirthday.html')

def birthday_campaign_detail(request, campaign_id):
    """Display birthday campaign detail page"""
    return render(request, 'website/birthday_campaign_detail.html', {'campaign_id': campaign_id})

from django.contrib.auth.decorators import login_required
from applications.models import BirthdayCampaign, BirthdayDonation
from django.db.models import Sum

@login_required
def admin_birthday_campaigns(request):
    """Admin birthday campaigns management page"""
    if not request.user.is_superuser:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Access denied")
    
    # Get data directly
    campaigns = BirthdayCampaign.objects.all().order_by('-created_at')
    donations = BirthdayDonation.objects.filter(status='completed')
    
    stats = {
        'total_campaigns': campaigns.count(),
        'active_campaigns': campaigns.filter(status='active').count(),
        'total_raised': float(donations.aggregate(total=Sum('amount'))['total'] or 0),
        'total_donors': donations.count()
    }
    
    context = {
        'stats': stats,
        'campaigns': campaigns
    }
    return render(request, 'admin/birthday_campaigns.html', context)


def get_involved(request):
    return render(request, 'website/get_involved.html')

def login_view(request):
    return render(request, 'auth/login.html')

def logout_view(request):
    if request.method == 'POST':
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Logout requested by user: {request.user} via method: {request.method}")
        from django.contrib.auth import logout
        logout(request)
        from django.shortcuts import redirect
        from django.urls import reverse
        return redirect(reverse('home'))
    else:
        from django.http import HttpResponseNotAllowed
        return HttpResponseNotAllowed(['POST'])

def admin_dashboard(request):
    from users.models import CustomUser
    from branches.models import Branch
    from applications.models import Application
    from payments.models import Payment
    from events.models import Event, EventParticipation
    from tasks.models import Task
    from notices.models import Notice, UserNotification
    from messaging.models import Message
    from django.db.models import Count, Sum
    from django.utils import timezone
    from datetime import timedelta
    
    # Calculate statistics
    total_users = CustomUser.objects.count()
    total_branches = Branch.objects.count()
    total_applications = Application.objects.count()
    total_payments = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_events = Event.objects.count()
    total_tasks = Task.objects.count()
    total_notices = Notice.objects.count()
    total_messages = Message.objects.count()
    
    # Recent activity (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_applications = Application.objects.filter(applied_at__gte=thirty_days_ago).order_by('-applied_at')[:10]
    recent_payments = Payment.objects.filter(paid_at__gte=thirty_days_ago).order_by('-paid_at')[:5]
    recent_events = Event.objects.filter(created_at__gte=thirty_days_ago).order_by('-created_at')[:5]
    
    # Recent notices for admin
    recent_notices = Notice.objects.filter(is_active=True).order_by('-created_at')[:5]
    
    context = {
        'stats': {
            'total_users': total_users,
            'total_branches': total_branches,
            'total_applications': total_applications,
            'total_payments': total_payments,
            'total_events': total_events,
            'total_tasks': total_tasks,
            'total_notices': total_notices,
            'total_messages': total_messages,
        },
        'recent_applications': recent_applications,
        'recent_payments': recent_payments,
        'recent_events': recent_events,
        'recent_notices': recent_notices,
    }
    return render(request, 'admin/dashboard.html', context)

def admin_users(request):
    return render(request, 'admin/users.html')

def admin_branches(request):
    return render(request, 'admin/branches.html')

def admin_tasks(request):
    return render(request, 'admin/tasks.html')

def admin_task_detail(request):
    return render(request, 'admin/task_detail.html')

def admin_notices(request):
    return render(request, 'admin/notices.html')

def member_notices(request):
    return render(request, 'member/notices.html')

def volunteer_notices(request):
    return render(request, 'volunteer/notices.html')

def admin_applications(request):
    return render(request, 'admin/applications.html')

def admin_sponsorships(request):
    return render(request, 'admin/sponsorships.html')

def admin_event_management(request):
    return render(request, 'admin/event_management.html')

def admin_herosection(request):
    from django.core.serializers import serialize
    import json
    
    hero_sections = HeroSection.objects.all().order_by('-created_at')
    
    # Serialize hero sections to JSON for JavaScript
    hero_sections_json = []
    for hero in hero_sections:
        hero_sections_json.append({
            'id': hero.id,
            'title': hero.title,
            'subtitle': hero.subtitle,
            'background_image': hero.background_image.url if hero.background_image else None,
            'background_video': hero.background_video.url if hero.background_video else None,
            'is_active': hero.is_active,
            'created_at': hero.created_at.isoformat(),
        })
    
    context = {
        'hero_sections': json.dumps(hero_sections_json)
    }
    return render(request, 'admin/herosection.html', context)

def apply_member(request):
    return render(request, 'public/apply_member.html', {'districts': NEPAL_DISTRICTS})

def apply_volunteer(request):
    return render(request, 'public/apply_volunteer.html', {'districts': NEPAL_DISTRICTS})

from django.shortcuts import render, redirect

def guest_welcome(request):
    contact_info = ContactInfo.get_active()
    awards = Award.get_active_awards()
    context = {
        'contact_info': contact_info,
        'awards': awards,
    }
    return render(request, 'guest/profile.html', context)  # Use the new combined template

def guest_dashboard(request):
    return render(request, 'guest/dashboard.html')

def guest_profile(request):
    # Always show profile if user reaches this page
    contact_info = ContactInfo.get_active()
    awards = Award.get_active_awards()
    
    # If Django user is authenticated, sync to localStorage
    if request.user.is_authenticated:
        from rest_framework_simplejwt.tokens import RefreshToken
        import json
        
        refresh = RefreshToken.for_user(request.user)
        user_data = {
            'id': request.user.id,
            'email': request.user.email,
            'user_type': getattr(request.user, 'user_type', 'guest'),
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
        
        context = {
            'contact_info': contact_info,
            'awards': awards,
            'django_authenticated': True,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user_data': json.dumps(user_data),
        }
    else:
        context = {
            'contact_info': contact_info,
            'awards': awards,
            'django_authenticated': False,
        }
    
    return render(request, 'guest/profile.html', context)

def guest_applications(request):
    return render(request, 'guest/applications.html')

def member_profile(request):
    return render(request, 'member/profile.html')

def member_dashboard(request):
    return render(request, 'member/dashboard.html')

def member_tasks(request):
    return render(request, 'member/tasks.html')

def member_notifications(request):
    return render(request, 'member/notifications.html')

def admin_materials(request):
    return render(request, 'admin/materials.html')

def member_materials(request):
    return render(request, 'member/materials.html')

def volunteer_dashboard(request):
    return render(request, 'volunteer/dashboard.html')

def volunteer_tasks(request):
    return render(request, 'volunteer/tasks.html')

def volunteer_materials(request):
    return render(request, 'volunteer/materials.html')

def admin_supportcards(request):
    from django.core.serializers import serialize
    import json
    
    support_cards = SupportCard.objects.all().order_by('order', '-created_at')
    
    # Serialize support cards to JSON for JavaScript
    support_cards_json = []
    for card in support_cards:
        support_cards_json.append({
            'id': card.id,
            'title': card.title,
            'description': card.description,
            'image': card.image.url if card.image else None,
            'button_text': card.button_text,
            'button_url': card.button_url,
            'order': card.order,
            'is_active': card.is_active,
            'created_at': card.created_at.isoformat(),
        })
    
    context = {
        'support_cards': json.dumps(support_cards_json)
    }
    return render(request, 'admin/supportcards.html', context)

def admin_whoweare(request):
    from django.core.serializers import serialize
    import json

    who_we_are_sections = WhoWeAre.objects.all().order_by('-created_at')

    # Serialize who we are sections to JSON for JavaScript
    who_we_are_json = []
    for section in who_we_are_sections:
        who_we_are_json.append({
            'id': section.id,
            'image': section.image.url if section.image else None,
            'is_active': section.is_active,
            'created_at': section.created_at.isoformat(),
        })

    context = {
        'who_we_are_sections': json.dumps(who_we_are_json)
    }
    return render(request, 'admin/whoweare.html', context)

def admin_growingimpact(request):
    from django.core.serializers import serialize
    import json

    growing_impact_sections = GrowingOurImpact.objects.all().order_by('-created_at')

    # Serialize growing impact sections to JSON for JavaScript
    growing_impact_json = []
    for section in growing_impact_sections:
        growing_impact_json.append({
            'id': section.id,
            'title': section.title,
            'image': section.image.url if section.image else None,
            'is_active': section.is_active,
            'created_at': section.created_at.isoformat(),
        })

    context = {
        'growing_impact_sections': json.dumps(growing_impact_json)
    }
    return render(request, 'admin/growingimpact.html', context)

def admin_statistics(request):
    from django.core.serializers import serialize
    import json

    statistics_sections = Statistics.objects.all().order_by('-created_at')

    # Serialize statistics sections to JSON for JavaScript
    statistics_json = []
    for section in statistics_sections:
        statistics_json.append({
            'id': section.id,
            'dropouts_enrolled': section.dropouts_enrolled,
            'schools_supported': section.schools_supported,
            'projects': section.projects,
            'districts': section.districts,
            'is_active': section.is_active,
            'created_at': section.created_at.isoformat(),
        })

    context = {
        'statistics_sections': json.dumps(statistics_json)
    }
    return render(request, 'admin/statistics.html', context)

def payment_success(request, pk):
    """
    Handle Khalti payment callback for applications.
    This view is called when user returns from Khalti payment gateway.
    Callback should only acknowledge, not verify.
    """
    from django.http import HttpResponse
    import logging

    logger = logging.getLogger(__name__)
    logger.info("KHALTI CALLBACK HIT - Application Payment")

    return HttpResponse("OK", status=200)
def admin_partners(request):
    from django.core.serializers import serialize
    import json

    partners = Partner.objects.all().order_by('order', '-created_at')

    # Serialize partners to JSON for JavaScript
    partners_json = []
    for partner in partners:
        partners_json.append({
            'id': partner.id,
            'name': partner.name,
            'logo': partner.logo.url if partner.logo else None,
            'website_url': partner.website_url,
            'order': partner.order,
            'is_active': partner.is_active,
            'created_at': partner.created_at.isoformat(),
        })

    context = {
        'partners': json.dumps(partners_json)
    }
    return render(request, 'admin/partners.html', context)

def admin_events(request):
    """Content management for events displayed on index page"""
    import json
    from django.contrib import messages
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            try:
                event = IndexEvent.objects.create(
                    title=request.POST.get('title'),
                    description=request.POST.get('description'),
                    location=request.POST.get('location', ''),
                    event_date=request.POST.get('event_date') or None,
                    order=int(request.POST.get('order', 0)),
                    is_active=request.POST.get('is_active') == 'on'
                )
                
                if request.FILES.get('image'):
                    event.image = request.FILES['image']
                    event.save()
                
                messages.success(request, 'Event created successfully!')
            except Exception as e:
                messages.error(request, f'Error creating event: {str(e)}')
        
        elif action == 'update':
            try:
                event_id = request.POST.get('event_id')
                event = get_object_or_404(IndexEvent, id=event_id)
                
                event.title = request.POST.get('title')
                event.description = request.POST.get('description')
                event.location = request.POST.get('location', '')
                event.event_date = request.POST.get('event_date') or None
                event.order = int(request.POST.get('order', 0))
                event.is_active = request.POST.get('is_active') == 'on'
                
                if request.FILES.get('image'):
                    event.image = request.FILES['image']
                
                event.save()
                messages.success(request, 'Event updated successfully!')
            except Exception as e:
                messages.error(request, f'Error updating event: {str(e)}')
        
        elif action == 'delete':
            try:
                event_id = request.POST.get('event_id')
                event = get_object_or_404(IndexEvent, id=event_id)
                event.delete()
                messages.success(request, 'Event deleted successfully!')
            except Exception as e:
                messages.error(request, f'Error deleting event: {str(e)}')
        
        return redirect('admin_events')
    
    # Get IndexEvents for the index page content management
    events = IndexEvent.objects.all().order_by('order', '-event_date')
    
    # Serialize events to JSON for JavaScript
    events_json = []
    for event in events:
        events_json.append({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'image': event.image.url if event.image else None,
            'location': event.location,
            'event_date': event.event_date.isoformat() if event.event_date else None,
            'order': event.order,
            'is_active': event.is_active,
            'created_at': event.created_at.isoformat(),
        })
    
    context = {
        'events': json.dumps(events_json)
    }
    return render(request, 'admin/events.html', context)

def admin_event_participants(request, event_id):
    """Event participants management page"""
    from events.models import Event, EventParticipation
    import json
    
    event = get_object_or_404(Event, id=event_id)
    participants = EventParticipation.objects.filter(event=event).select_related('user').order_by('-applied_at')
    
    # Serialize participants to JSON
    participants_json = []
    for p in participants:
        participants_json.append({
            'id': p.id,
            'user_name': p.user.get_full_name() or p.user.email,
            'user_email': p.user.email,
            'user_type': p.user.user_type,
            'status': p.status,
            'application_message': p.application_message or '',
            'admin_notes': p.admin_notes or '',
            'applied_at': p.applied_at.isoformat(),
            'attended': p.attended,
            'rating': p.rating,
            'review': p.review or '',
        })
    
    context = {
        'event': event,
        'participants': json.dumps(participants_json)
    }
    return render(request, 'admin/event_participants.html', context)

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@csrf_exempt
def admin_event_reviews(request, event_id):
    """Event reviews detail page"""
    from events.models import Event, EventParticipation
    import json
    
    event = get_object_or_404(Event, id=event_id)
    reviews = EventParticipation.objects.filter(
        event=event, 
        review__isnull=False
    ).exclude(review='').select_related('user').order_by('-rating', '-id')
    
    # Serialize reviews to JSON
    reviews_json = []
    for review in reviews:
        reviews_json.append({
            'user_name': review.user.get_full_name() or review.user.email,
            'user_email': review.user.email,
            'rating': review.rating,
            'review': review.review,
            'created_at': review.id,  # Using ID as proxy for creation order
        })
    
    context = {
        'event': event,
        'reviews': json.dumps(reviews_json)
    }
    return render(request, 'admin/event_reviews.html', context)

@csrf_exempt
def toggle_attendance(request, participation_id):
    """Toggle attendance for event participant"""
    from events.models import EventParticipation
    from notices.models import UserNotification
    from django.http import JsonResponse
    from django.utils import timezone
    from django.core.mail import send_mail
    from django.conf import settings
    from django.views.decorators.csrf import csrf_exempt
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        participation = get_object_or_404(EventParticipation, id=participation_id)
        
        # Toggle attendance
        participation.attended = not participation.attended
        if request.user.is_authenticated:
            participation.attendance_marked_by = request.user
            participation.attendance_marked_at = timezone.now()
        participation.save()
        
        # Create notification if marked present
        if participation.attended:
            UserNotification.objects.create(
                user=participation.user,
                notification_type='event_attended',
                title=f'Attendance Marked: {participation.event.title}',
                message=f'Your attendance has been marked for "{participation.event.title}"'
            )
            
            # Send email
            try:
                subject = f'✅ Attendance Confirmed: {participation.event.title}'
                message = f'''Dear {participation.user.first_name or participation.user.email},

Your attendance has been confirmed for "{participation.event.title}".

📅 Event: {participation.event.title}
📍 Date: {participation.event.start_datetime.strftime("%B %d, %Y at %I:%M %p")}

Thank you for participating!

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
        
        return JsonResponse({
            'success': True,
            'attended': participation.attended,
            'message': f'Attendance {"marked" if participation.attended else "unmarked"}'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    """Toggle attendance for event participant"""
    from events.models import EventParticipation
    from notices.models import UserNotification
    from django.http import JsonResponse
    from django.utils import timezone
    from django.core.mail import send_mail
    from django.conf import settings
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        participation = get_object_or_404(EventParticipation, id=participation_id)
        
        # Toggle attendance
        participation.attended = not participation.attended
        if request.user.is_authenticated:
            participation.attendance_marked_by = request.user
            participation.attendance_marked_at = timezone.now()
        participation.save()
        
        # Create notification if marked present
        if participation.attended:
            UserNotification.objects.create(
                user=participation.user,
                notification_type='event_attended',
                title=f'Attendance Marked: {participation.event.title}',
                message=f'Your attendance has been marked for "{participation.event.title}"'
            )
            
            # Send email
            try:
                subject = f'✅ Attendance Confirmed: {participation.event.title}'
                message = f'''Dear {participation.user.first_name or participation.user.email},

Your attendance has been confirmed for "{participation.event.title}".

📅 Event: {participation.event.title}
📍 Date: {participation.event.start_datetime.strftime("%B %d, %Y at %I:%M %p")}

Thank you for participating!

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
        
        return JsonResponse({
            'success': True,
            'attended': participation.attended,
            'message': f'Attendance {"marked" if participation.attended else "unmarked"}'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
def contact_us(request):
    contact_info = ContactInfo.get_active()
    context = {
        'contact_info': contact_info
    }
    return render(request, 'website/contact.html', context)

def admin_contact(request):
    from django.core.serializers import serialize
    import json

    contact_infos = ContactInfo.objects.all().order_by('-created_at')

    # Serialize contact info to JSON for JavaScript
    contact_infos_json = []
    for contact in contact_infos:
        contact_infos_json.append({
            'id': contact.id,
            'address': contact.address,
            'phone': contact.phone,
            'email': contact.email,
            'facebook_url': contact.facebook_url,
            'instagram_url': contact.instagram_url,
            'linkedin_url': contact.linkedin_url,
            'youtube_url': contact.youtube_url,
            'whatsapp_url': contact.whatsapp_url,
            'is_active': contact.is_active,
            'created_at': contact.created_at.isoformat(),
        })

    context = {
        'contact_infos': json.dumps(contact_infos_json)
    }
    return render(request, 'admin/contact.html', context)
def admin_awards(request):
    from django.core.serializers import serialize
    import json

    awards = Award.objects.all().order_by('order', '-created_at')

    # Serialize awards to JSON for JavaScript
    awards_json = []
    for award in awards:
        awards_json.append({
            'id': award.id,
            'title': award.title,
            'image': award.image.url if award.image else None,
            'year': award.year,
            'description': award.description,
            'order': award.order,
            'is_active': award.is_active,
            'created_at': award.created_at.isoformat(),
        })

    context = {
        'awards': json.dumps(awards_json)
    }
    return render(request, 'admin/awards.html', context)

def admin_ourwork(request):
    from django.core.serializers import serialize
    import json

    our_works = OurWork.objects.all().order_by('order', '-created_at')

    # Serialize our works to JSON for JavaScript
    our_works_json = []
    for work in our_works:
        our_works_json.append({
            'id': work.id,
            'navlink': work.navlink,
            'title': work.title,
            'description': work.description,
            'main_image': work.main_image.url if work.main_image else None,
            'external_link': work.external_link,
            'order': work.order,
            'is_active': work.is_active,
            'created_at': work.created_at.isoformat(),
        })

    context = {
        'our_works': json.dumps(our_works_json)
    }
    return render(request, 'admin/ourwork.html', context)

def our_work_detail(request, navlink):
    """Display a specific our work item"""
    try:
        work = OurWork.objects.get(navlink=navlink, is_active=True)
        our_work_items = OurWork.get_active_works()
        awards = Award.get_active_awards()
        context = {
            'work': work,
            'our_work_items': our_work_items,
            'hero_section': HeroSection.get_active(),
            'contact_info': ContactInfo.get_active(),
            'awards': awards,
        }
        return render(request, 'website/our_work_detail.html', context)
    except OurWork.DoesNotExist:
        from django.http import Http404
        raise Http404("Our work item not found")


def report_school_dropout(request):
    """Display the school dropout report form"""
    from .districts import NEPAL_DISTRICTS
    
    # If Django user is authenticated, sync to context
    if request.user.is_authenticated:
        from rest_framework_simplejwt.tokens import RefreshToken
        import json
        
        refresh = RefreshToken.for_user(request.user)
        user_data = {
            'id': request.user.id,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
        
        context = {
            'districts': NEPAL_DISTRICTS,
            'django_authenticated': True,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user_data': json.dumps(user_data),
        }
    else:
        context = {
            'districts': NEPAL_DISTRICTS,
            'django_authenticated': False,
        }
    
    return render(request, 'website/report_school_dropout.html', context)


def admin_school_dropout_reports(request):
    """Display admin page for school dropout reports"""
    from .districts import NEPAL_DISTRICTS
    context = {
        'districts': NEPAL_DISTRICTS,
    }
    return render(request, 'admin/school_dropout_reports.html', context)


def donation_callback(request):
    """
    Handle Khalti payment callback after donation.
    This view is called when user returns from Khalti payment gateway.
    """
    from django.http import HttpResponse
    import logging
    import requests
    from .models import Donation
    from notices.models import UserNotification
    from django.core.mail import send_mail
    from django.conf import settings
    from django.utils import timezone
    from decimal import Decimal

    logger = logging.getLogger(__name__)
    logger.info("KHALTI CALLBACK HIT - Donation Payment")
    
    # Get parameters from callback
    pidx = request.GET.get('pidx')
    transaction_id = request.GET.get('transaction_id')
    tidx = request.GET.get('tidx')
    amount = request.GET.get('amount')
    mobile = request.GET.get('mobile')
    status = request.GET.get('status')
    
    logger.info(f"Callback params: pidx={pidx}, transaction_id={transaction_id}, status={status}")
    
    if pidx:
        try:
            # Find donation by pidx
            donation = Donation.objects.get(pidx=pidx)
            
            # Verify payment with Khalti
            khalti_secret_key = settings.KHALTI_SECRET_KEY
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
                
                # Map Khalti status to our status
                status_mapping = {
                    'completed': 'completed',
                    'pending': 'pending',
                    'initiated': 'initiated',
                    'refunded': 'refunded',
                    'expired': 'expired',
                    'user canceled': 'canceled'
                }
                
                donation.payment_status = status_mapping.get(payment_status, 'failed')
                donation.transaction_id = khalti_response.get('transaction_id')
                donation.fee = Decimal(str(khalti_response.get('fee', 0))) / 100
                donation.refunded = khalti_response.get('refunded', False)
                
                if donation.payment_status == 'completed' and not donation.completed_at:
                    donation.completed_at = timezone.now()
                    
                    # Send notification and email on successful payment
                    try:
                        # Send email receipt
                        subject = f'✅ Donation Receipt - Rs. {donation.amount} - Aarambha Foundation'
                        message = f'''Dear {donation.full_name},

Thank you for your generous donation to Aarambha Foundation!

💰 Donation Details:
- Amount: Rs. {donation.amount}
- Transaction ID: {donation.transaction_id}
- Date: {donation.completed_at.strftime("%B %d, %Y at %I:%M %p")}
- Receipt ID: {donation.purchase_order_id}

Your contribution helps us provide education, healthcare, and community development programs. Together, we are making a lasting impact in our communities.

This email serves as your official receipt for tax purposes.

With gratitude,
Aarambha Foundation Team
Email: we.aarambha@gmail.com
Phone: +977 (984)346-7402'''
                        
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[donation.email],
                            fail_silently=True,
                        )
                        logger.info(f"Email sent to {donation.email}")
                    except Exception as e:
                        logger.error(f"Failed to send email: {e}")
                
                donation.save()
                logger.info(f"Donation {donation.id} updated with status: {donation.payment_status}")
                
                # Redirect based on status
                return redirect('/guest/profile/?tab=donations')
            else:
                logger.error(f"Khalti lookup failed: {response.text}")
                return redirect('/guest/profile/?tab=donations')
                
        except Donation.DoesNotExist:
            logger.error(f"Donation not found for pidx: {pidx}")
            return redirect('/guest/profile/?tab=donations')
        except Exception as e:
            logger.error(f"Callback processing error: {e}")
            return redirect('/guest/profile/?tab=donations')
    
    return HttpResponse("OK", status=200)

def debug_auth(request):
    """Debug page for authentication troubleshooting"""
    return render(request, 'debug/auth-debug.html')


def member_recommendation_letters(request):
    """Member recommendation letters page"""
    if request.method == 'POST':
        from django.contrib import messages
        from notices.models import UserNotification
        from django.core.mail import send_mail
        from django.conf import settings
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"POST data: {request.POST}")
        
        purpose = request.POST.get('purpose')
        description = request.POST.get('description')
        
        logger.info(f"Purpose: {purpose}, Description length: {len(description) if description else 0}")
        
        if purpose and description:
            try:
                letter = RecommendationLetter.objects.create(
                    user=request.user,
                    purpose=purpose,
                    description=description
                )
                logger.info(f"Created letter with ID: {letter.id}")
                
                # Create notification
                UserNotification.objects.create(
                    user=request.user,
                    notification_type='general',
                    title='Recommendation Letter Request Submitted',
                    message=f'Your recommendation letter request for "{purpose}" has been submitted and is under review.'
                )
                
                # Send email to admin
                try:
                    send_mail(
                        subject=f'New Recommendation Letter Request - {purpose}',
                        message=f'New recommendation letter request from {request.user.get_full_name() or request.user.email}\n\nPurpose: {purpose}\nDescription: {description}',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[settings.EMAIL_HOST_USER],
                        fail_silently=True,
                    )
                except Exception as e:
                    logger.error(f"Email error: {e}")
                
                messages.success(request, 'Recommendation letter request submitted successfully!')
                return redirect('member_recommendation_letters')
            except Exception as e:
                logger.error(f"Error creating letter: {e}")
                messages.error(request, f'Error creating request: {str(e)}')
        else:
            logger.warning(f"Missing fields - Purpose: {bool(purpose)}, Description: {bool(description)}")
            messages.error(request, 'Please fill in all required fields.')
    
    # Get user statistics
    from events.models import EventParticipation
    from tasks.models import TaskSubmission
    
    events_attended = EventParticipation.objects.filter(user=request.user, attended=True).count()
    tasks_submitted = TaskSubmission.objects.filter(user=request.user).count()
    
    letters = RecommendationLetter.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'letters': letters,
        'user_stats': {
            'events_attended': events_attended,
            'tasks_submitted': tasks_submitted,
            'user_type': request.user.user_type,
            'date_joined': request.user.date_joined,
        }
    }
    return render(request, 'member/recommendation_letters.html', context)


def volunteer_recommendation_letters(request):
    """Volunteer recommendation letters page"""
    if request.method == 'POST':
        from django.contrib import messages
        from notices.models import UserNotification
        from django.core.mail import send_mail
        from django.conf import settings
        
        purpose = request.POST.get('purpose')
        description = request.POST.get('description')
        
        if purpose and description:
            RecommendationLetter.objects.create(
                user=request.user,
                purpose=purpose,
                description=description
            )
            
            # Create notification
            UserNotification.objects.create(
                user=request.user,
                notification_type='general',
                title='Recommendation Letter Request Submitted',
                message=f'Your recommendation letter request for "{purpose}" has been submitted and is under review.'
            )
            
            # Send email to admin
            try:
                send_mail(
                    subject=f'New Recommendation Letter Request - {purpose}',
                    message=f'New recommendation letter request from {request.user.get_full_name() or request.user.email}\n\nPurpose: {purpose}\nDescription: {description}',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=True,
                )
            except:
                pass
            
            messages.success(request, 'Recommendation letter request submitted successfully!')
            return redirect('volunteer_recommendation_letters')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    # Get user statistics
    from events.models import EventParticipation
    from tasks.models import TaskSubmission
    
    events_attended = EventParticipation.objects.filter(user=request.user, attended=True).count()
    tasks_submitted = TaskSubmission.objects.filter(user=request.user).count()
    
    letters = RecommendationLetter.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'letters': letters,
        'user_stats': {
            'events_attended': events_attended,
            'tasks_submitted': tasks_submitted,
            'user_type': request.user.user_type,
            'date_joined': request.user.date_joined,
        }
    }
    return render(request, 'volunteer/recommendation_letters.html', context)


def sponsor_dashboard(request):
    return render(request, 'sponsor/dashboard.html')

def sponsor_profile(request):
    return render(request, 'sponsor/profile.html')

def sponsor_children(request):
    return render(request, 'sponsor/children.html')

def sponsor_payment_details(request):
    return render(request, 'sponsor/payment_details.html')

def sponsor_notifications(request):
    return render(request, 'sponsor/notifications.html')

def sponsor_assignments(request):
    return render(request, 'sponsor/assignments.html')

def admin_children(request):
    return render(request, 'admin/children.html')

def admin_sponsorship_payments(request):
    """Admin sponsorship payment details page"""
    return render(request, 'admin/sponsorship_payments.html')

def admin_one_rupee_campaign(request):
    """Admin One Rupee Campaign management page"""
    return render(request, 'admin/one_rupee_campaign.html')

def admin_recommendation_letters(request):
    """Admin recommendation letters management page"""
    import json
    from django.contrib import messages
    from notices.models import UserNotification
    from django.core.mail import send_mail
    from django.conf import settings
    from django.utils import timezone
    
    if request.method == 'POST':
        letter_id = request.POST.get('letter_id')
        action = request.POST.get('action')
        
        if action == 'approve':
            signed_letter = request.FILES.get('signed_letter')
            admin_notes = request.POST.get('admin_notes', '')
            
            try:
                letter = get_object_or_404(RecommendationLetter, id=letter_id)
                letter.status = 'approved'
                letter.admin_notes = admin_notes
                letter.approved_at = timezone.now()
                
                if signed_letter:
                    letter.signed_letter = signed_letter
                
                letter.save()
                
                # Create notification
                UserNotification.objects.create(
                    user=letter.user,
                    notification_type='general',
                    title='Recommendation Letter Approved',
                    message=f'Your recommendation letter request for "{letter.purpose}" has been approved.'
                )
                
                # Send email
                try:
                    subject = f'✅ Recommendation Letter Approved - {letter.purpose}'
                    message = f'''Dear {letter.user.first_name or letter.user.email},

Your recommendation letter request has been approved!

📄 Purpose: {letter.purpose}
📅 Approved: {timezone.now().strftime("%B %d, %Y")}

📎 Your signed letter is now available for download in your portal.

Best regards,
Aarambha Foundation Team'''
                    
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[letter.user.email],
                        fail_silently=True,
                    )
                except:
                    pass
                
                messages.success(request, 'Recommendation letter approved successfully!')
                
            except Exception as e:
                messages.error(request, f'Error approving letter: {str(e)}')
        
        elif action == 'reject':
            admin_notes = request.POST.get('admin_notes', '')
            
            try:
                letter = get_object_or_404(RecommendationLetter, id=letter_id)
                letter.status = 'rejected'
                letter.admin_notes = admin_notes
                letter.save()
                
                # Create notification
                UserNotification.objects.create(
                    user=letter.user,
                    notification_type='general',
                    title='Recommendation Letter Request Update',
                    message=f'Your recommendation letter request for "{letter.purpose}" has been reviewed.'
                )
                
                # Send email
                try:
                    subject = f'📋 Recommendation Letter Request Update - {letter.purpose}'
                    message = f'''Dear {letter.user.first_name or letter.user.email},

We have reviewed your recommendation letter request.

📄 Purpose: {letter.purpose}
📅 Reviewed: {timezone.now().strftime("%B %d, %Y")}

{f"Note: {admin_notes}" if admin_notes else ""}

Best regards,
Aarambha Foundation Team'''
                    
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[letter.user.email],
                        fail_silently=True,
                    )
                except:
                    pass
                
                messages.success(request, 'Recommendation letter rejected successfully!')
                
            except Exception as e:
                messages.error(request, f'Error rejecting letter: {str(e)}')
        
        return redirect('admin_recommendation_letters')
    
    letters = RecommendationLetter.objects.all().select_related('user').order_by('-created_at')
    
    letters_json = []
    for letter in letters:
        # Get user statistics
        from events.models import EventParticipation
        from tasks.models import TaskSubmission
        
        events_attended = EventParticipation.objects.filter(user=letter.user, attended=True).count()
        tasks_submitted = TaskSubmission.objects.filter(user=letter.user).count()
        
        letters_json.append({
            'id': letter.id,
            'user_name': letter.user.get_full_name() or letter.user.email,
            'user_email': letter.user.email,
            'user_type': letter.user.user_type,
            'user_branch': str(getattr(letter.user, 'branch', None)) if getattr(letter.user, 'branch', None) else None,
            'date_joined': letter.user.date_joined.isoformat(),
            'events_attended': events_attended,
            'tasks_submitted': tasks_submitted,
            'purpose': letter.purpose,
            'description': letter.description,
            'status': letter.status,
            'admin_notes': letter.admin_notes or '',
            'letter_content': letter.letter_content or '',
            'signed_letter': letter.signed_letter.url if letter.signed_letter else None,
            'created_at': letter.created_at.isoformat(),
        })
    
    context = {
        'letters': json.dumps(letters_json)
    }
    return render(request, 'admin/recommendation_letters.html', context)


def admin_blogs(request):
    """Admin blog management page"""
    import json
    from django.contrib import messages
    
    # Get all blog posts with related data
    blog_posts = BlogPost.objects.all().select_related('author').prefetch_related('categories', 'paragraphs').order_by('-created_at')
    categories = BlogCategory.objects.filter(is_active=True)
    
    # Serialize blog posts to JSON
    posts_json = []
    for post in blog_posts:
        posts_json.append({
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'excerpt': post.excerpt,
            'author_name': post.author.get_full_name() or post.author.email,
            'status': post.status,
            'is_featured': post.is_featured,
            'featured_image': post.featured_image.url if post.featured_image else None,
            'categories': [{'name': cat.name, 'color': cat.color} for cat in post.categories.all()],
            'paragraph_count': post.paragraphs.count(),
            'created_at': post.created_at.isoformat(),
            'published_at': post.published_at.isoformat() if post.published_at else None,
            'view_url': post.get_absolute_url,
        })
    
    # Serialize categories to JSON
    categories_json = []
    for category in categories:
        categories_json.append({
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'color': category.color,
            'post_count': category.blog_posts.filter(status='published').count(),
        })
    
    context = {
        'blog_posts': json.dumps(posts_json),
        'categories': json.dumps(categories_json),
        'total_posts': blog_posts.count(),
        'published_posts': blog_posts.filter(status='published').count(),
        'draft_posts': blog_posts.filter(status='draft').count(),
    }
    return render(request, 'admin/blogs.html', context)


def admin_blog_edit(request, blog_id):
    """Custom blog post editor"""
    import json
    from django.contrib import messages
    
    blog_post = get_object_or_404(BlogPost, id=blog_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_post':
            try:
                blog_post.title = request.POST.get('title')
                blog_post.slug = request.POST.get('slug') or slugify(request.POST.get('title'))
                blog_post.excerpt = request.POST.get('excerpt')
                blog_post.meta_description = request.POST.get('meta_description', '')
                blog_post.status = request.POST.get('status')
                blog_post.is_featured = request.POST.get('is_featured') == 'on'
                
                if request.FILES.get('featured_image'):
                    blog_post.featured_image = request.FILES['featured_image']
                
                # Update categories
                category_ids = request.POST.getlist('categories')
                blog_post.categories.set(category_ids)
                
                # Set published_at when status changes to published
                if blog_post.status == 'published' and not blog_post.published_at:
                    from django.utils import timezone
                    blog_post.published_at = timezone.now()
                
                blog_post.save()
                messages.success(request, 'Blog post updated successfully!')
            except Exception as e:
                messages.error(request, f'Error updating blog post: {str(e)}')
        
        elif action == 'update_paragraph':
            try:
                paragraph_id = request.POST.get('paragraph_id')
                paragraph = get_object_or_404(BlogParagraph, id=paragraph_id, blog_post=blog_post)
                
                paragraph.paragraph_type = request.POST.get('paragraph_type')
                paragraph.content = request.POST.get('content', '')
                paragraph.quote_text = request.POST.get('quote_text', '')
                paragraph.quote_author = request.POST.get('quote_author', '')
                paragraph.image_caption = request.POST.get('image_caption', '')
                paragraph.image_alt_text = request.POST.get('image_alt_text', '')
                
                if request.FILES.get('image'):
                    paragraph.image = request.FILES['image']
                
                paragraph.save()
                messages.success(request, 'Paragraph updated successfully!')
            except Exception as e:
                messages.error(request, f'Error updating paragraph: {str(e)}')
        
        elif action == 'add_paragraph':
            try:
                max_order = blog_post.paragraphs.aggregate(models.Max('order'))['order__max'] or 0
                BlogParagraph.objects.create(
                    blog_post=blog_post,
                    order=max_order + 1,
                    paragraph_type='text',
                    content='<p>New paragraph content...</p>'
                )
                messages.success(request, 'Paragraph added successfully!')
            except Exception as e:
                messages.error(request, f'Error adding paragraph: {str(e)}')
        
        elif action == 'delete_paragraph':
            try:
                paragraph_id = request.POST.get('paragraph_id')
                paragraph = get_object_or_404(BlogParagraph, id=paragraph_id, blog_post=blog_post)
                paragraph.delete()
                messages.success(request, 'Paragraph deleted successfully!')
            except Exception as e:
                messages.error(request, f'Error deleting paragraph: {str(e)}')
        
        return redirect('admin_blog_edit', blog_id=blog_id)
    
    # Get data for template
    paragraphs = blog_post.paragraphs.all().order_by('order')
    categories = BlogCategory.objects.filter(is_active=True)
    
    # Serialize data
    paragraphs_json = []
    for p in paragraphs:
        paragraphs_json.append({
            'id': p.id,
            'order': p.order,
            'paragraph_type': p.paragraph_type,
            'content': p.content,
            'image': p.image.url if p.image else None,
            'image_caption': p.image_caption,
            'image_alt_text': p.image_alt_text,
            'quote_text': p.quote_text,
            'quote_author': p.quote_author,
        })
    
    categories_json = []
    for c in categories:
        categories_json.append({
            'id': c.id,
            'name': c.name,
            'color': c.color,
        })
    
    context = {
        'blog_post': blog_post,
        'paragraphs': json.dumps(paragraphs_json),
        'categories': json.dumps(categories_json),
        'selected_categories': list(blog_post.categories.values_list('id', flat=True)),
    }
    return render(request, 'admin/blog_edit.html', context)


def admin_donations(request):
    """Admin donations management page"""
    import json
    from django.db.models import Sum, Count
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # Get all donations
    donations = Donation.objects.all().order_by('-created_at')
    
    # Calculate statistics
    total_donations = donations.aggregate(total=Sum('amount'))['total'] or 0
    completed_donations = donations.filter(payment_status='completed')
    total_completed = completed_donations.aggregate(total=Sum('amount'))['total'] or 0
    total_count = donations.count()
    completed_count = completed_donations.count()
    
    # Filter by date if requested
    date_filter = request.GET.get('date_filter')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if date_filter:
        today = timezone.now().date()
        if date_filter == 'today':
            donations = donations.filter(created_at__date=today)
        elif date_filter == 'week':
            week_ago = today - timedelta(days=7)
            donations = donations.filter(created_at__date__gte=week_ago)
        elif date_filter == 'month':
            month_ago = today - timedelta(days=30)
            donations = donations.filter(created_at__date__gte=month_ago)
        elif date_filter == 'year':
            year_ago = today - timedelta(days=365)
            donations = donations.filter(created_at__date__gte=year_ago)
    
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            donations = donations.filter(created_at__date__gte=start, created_at__date__lte=end)
        except ValueError:
            pass
    
    # Serialize donations to JSON
    donations_json = []
    for donation in donations:
        donations_json.append({
            'id': donation.id,
            'full_name': donation.full_name,
            'email': donation.email,
            'phone': donation.phone,
            'amount': float(donation.amount),
            'program_name': donation.program_name,
            'program_type': donation.program_type,
            'payment_status': donation.payment_status,
            'purchase_order_id': donation.purchase_order_id,
            'transaction_id': donation.transaction_id or '',
            'created_at': donation.created_at.isoformat(),
            'completed_at': donation.completed_at.isoformat() if donation.completed_at else None,
            'refunded': donation.refunded,
        })
    
    context = {
        'donations': json.dumps(donations_json),
        'stats': {
            'total_donations': float(total_donations),
            'total_completed': float(total_completed),
            'total_count': total_count,
            'completed_count': completed_count,
        },
        'date_filter': date_filter,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'admin/donations.html', context)


def admin_blog_categories(request):
    """Admin blog categories management page"""
    import json
    from django.contrib import messages
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            try:
                BlogCategory.objects.create(
                    name=request.POST.get('name'),
                    slug=request.POST.get('slug') or slugify(request.POST.get('name')),
                    description=request.POST.get('description', ''),
                    color=request.POST.get('color', '#007bff'),
                    is_active=request.POST.get('is_active') == 'on'
                )
                messages.success(request, 'Category created successfully!')
            except Exception as e:
                messages.error(request, f'Error creating category: {str(e)}')
        
        elif action == 'update':
            try:
                category_id = request.POST.get('category_id')
                category = get_object_or_404(BlogCategory, id=category_id)
                category.name = request.POST.get('name')
                category.slug = request.POST.get('slug') or slugify(request.POST.get('name'))
                category.description = request.POST.get('description', '')
                category.color = request.POST.get('color', '#007bff')
                category.is_active = request.POST.get('is_active') == 'on'
                category.save()
                messages.success(request, 'Category updated successfully!')
            except Exception as e:
                messages.error(request, f'Error updating category: {str(e)}')
        
        elif action == 'delete':
            try:
                category_id = request.POST.get('category_id')
                category = get_object_or_404(BlogCategory, id=category_id)
                category.delete()
                messages.success(request, 'Category deleted successfully!')
            except Exception as e:
                messages.error(request, f'Error deleting category: {str(e)}')
        
        return redirect('admin_blog_categories')
    
    categories = BlogCategory.objects.all().order_by('name')
    
    categories_json = []
    for category in categories:
        categories_json.append({
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'description': category.description,
            'color': category.color,
            'is_active': category.is_active,
            'post_count': category.blog_posts.count(),
            'created_at': category.created_at.isoformat(),
        })
    
    context = {
        'categories': json.dumps(categories_json)
    }
    return render(request, 'admin/blog_categories.html', context)
    """Admin blog categories management page"""
    import json
    from django.contrib import messages
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            try:
                BlogCategory.objects.create(
                    name=request.POST.get('name'),
                    slug=request.POST.get('slug') or slugify(request.POST.get('name')),
                    description=request.POST.get('description', ''),
                    color=request.POST.get('color', '#007bff'),
                    is_active=request.POST.get('is_active') == 'on'
                )
                messages.success(request, 'Category created successfully!')
            except Exception as e:
                messages.error(request, f'Error creating category: {str(e)}')
        
        elif action == 'update':
            try:
                category_id = request.POST.get('category_id')
                category = get_object_or_404(BlogCategory, id=category_id)
                category.name = request.POST.get('name')
                category.slug = request.POST.get('slug') or slugify(request.POST.get('name'))
                category.description = request.POST.get('description', '')
                category.color = request.POST.get('color', '#007bff')
                category.is_active = request.POST.get('is_active') == 'on'
                category.save()
                messages.success(request, 'Category updated successfully!')
            except Exception as e:
                messages.error(request, f'Error updating category: {str(e)}')
        
        elif action == 'delete':
            try:
                category_id = request.POST.get('category_id')
                category = get_object_or_404(BlogCategory, id=category_id)
                category.delete()
                messages.success(request, 'Category deleted successfully!')
            except Exception as e:
                messages.error(request, f'Error deleting category: {str(e)}')
        
        return redirect('admin_blog_categories')
    
    categories = BlogCategory.objects.all().order_by('name')
    
    categories_json = []
    for category in categories:
        categories_json.append({
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'description': category.description,
            'color': category.color,
            'is_active': category.is_active,
            'post_count': category.blog_posts.count(),
            'created_at': category.created_at.isoformat(),
        })
    
    context = {
        'categories': json.dumps(categories_json)
    }
    return render(request, 'admin/blog_categories.html', context)
