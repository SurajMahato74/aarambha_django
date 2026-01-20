@api_view(['POST'])
@permission_classes([AllowAny])
def create_donation_record(request):
    try:
        from .models import BirthdayCampaign, BirthdayDonationRecord
        from django.utils import timezone
        
        campaign_id = request.data.get('campaign_id')
        donor_name = request.data.get('donor_name')
        amount = request.data.get('amount')
        message = request.data.get('message', 'Birthday donation')
        
        if not all([campaign_id, donor_name, amount]):
            return Response({'error': 'All required fields must be provided'}, status=400)
        
        campaign = BirthdayCampaign.objects.get(id=campaign_id)
        
        donation_record = BirthdayDonationRecord.objects.create(
            campaign=campaign,
            participant_name=donor_name,
            donation_amount=amount,
            donation_description=message,
            donation_date=timezone.now().date(),
            added_by=request.user if request.user.is_authenticated else None
        )
        
        # Update campaign totals
        campaign.current_amount += float(amount)
        campaign.donors_count += 1
        campaign.save()
        
        return Response({'success': True, 'message': 'Donation record created successfully'})
        
    except BirthdayCampaign.DoesNotExist:
        return Response({'error': 'Campaign not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)