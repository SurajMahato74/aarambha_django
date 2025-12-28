from django.shortcuts import render, redirect
from .districts import NEPAL_DISTRICTS
from .models import HeroSection, SupportCard, WhoWeAre, GrowingOurImpact, Statistics, Event, Partner, ContactInfo, Award, OurWork
from decimal import Decimal

def website_home(request):
    hero_section = HeroSection.get_active()
    support_cards = SupportCard.get_active_cards()
    who_we_are = WhoWeAre.get_active()
    growing_our_impact = GrowingOurImpact.get_active()
    statistics = Statistics.get_active()
    events = Event.get_active_events()
    partners = Partner.get_active_partners()
    contact_info = ContactInfo.get_active()
    awards = Award.get_active_awards()
    our_work_items = OurWork.get_active_works()
    context = {
        'hero_section': hero_section,
        'support_cards': support_cards,
        'who_we_are': who_we_are,
        'growing_our_impact': growing_our_impact,
        'statistics': statistics,
        'events': events,
        'partners': partners,
        'contact_info': contact_info,
        'awards': awards,
        'our_work_items': our_work_items
    }
    return render(request, 'website/index.html', context)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.urls import reverse
from .models import OurWork

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
        
def website_member_form(request):
    return render(request, 'website/member_form.html', {'districts': NEPAL_DISTRICTS})

def website_volunteer_form(request):
    return render(request, 'website/volunteer_form.html', {'districts': NEPAL_DISTRICTS})

def website_sponsor_child_form(request):
    return render(request, 'website/sponsor_child_form.html', {'districts': NEPAL_DISTRICTS})

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
    return render(request, 'admin/dashboard.html')

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
def admin_events(request):
    from django.core.serializers import serialize
    import json

    events = Event.objects.all().order_by('order', '-created_at')

    # Serialize events to JSON for JavaScript
    events_json = []
    for event in events:
        events_json.append({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'image': event.image.url if event.image else None,
            'event_date': event.event_date.isoformat() if event.event_date else None,
            'location': event.location,
            'order': event.order,
            'is_active': event.is_active,
            'created_at': event.created_at.isoformat(),
        })

    context = {
        'events': json.dumps(events_json)
    }
    return render(request, 'admin/events.html', context)
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
    context = {
        'districts': NEPAL_DISTRICTS,
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
    Callback should only acknowledge, not verify.
    """
    from django.http import HttpResponse
    import logging

    logger = logging.getLogger(__name__)
    logger.info("KHALTI CALLBACK HIT - Donation Payment")

    return HttpResponse("OK", status=200)

def debug_auth(request):
    """Debug page for authentication troubleshooting"""
    return render(request, 'debug/auth-debug.html')
