from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from applications.models import BirthdayCampaign, BirthdayDonation
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone

def create_test_birthday_campaign(request):
    """Create a test birthday campaign for development purposes"""
    try:
        # Check if a test campaign already exists
        existing_campaign = BirthdayCampaign.objects.filter(title__icontains='Test Campaign').first()
        
        if existing_campaign:
            return JsonResponse({
                'success': True,
                'message': f'Test campaign already exists with ID: {existing_campaign.id}',
                'campaign_id': existing_campaign.id,
                'campaign_url': f'/birthday-campaign/{existing_campaign.id}/'
            })
        
        # Create a test campaign
        campaign = BirthdayCampaign.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name='John Doe',
            email='john.doe@example.com',
            phone='9800000000',
            birthday_date=date.today() + timedelta(days=30),  # Birthday in 30 days
            target_amount=Decimal('50000.00'),
            current_amount=Decimal('15000.00'),
            title='Test Birthday Campaign for Education',
            description='This is a test birthday campaign to support education for underprivileged children. Instead of gifts, I am asking friends and family to donate to this noble cause. Every contribution, no matter how small, will make a difference in a child\'s life.',
            status='active',
            donors_count=5
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Test campaign created successfully with ID: {campaign.id}',
            'campaign_id': campaign.id,
            'campaign_url': f'/birthday-campaign/{campaign.id}/'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)