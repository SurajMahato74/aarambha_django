from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import HeroSection, SupportCard, WhoWeAre, GrowingOurImpact, Statistics, Event, Partner, ContactInfo, Award, OurWork
from .serializers import HeroSectionSerializer, SupportCardSerializer, WhoWeAreSerializer, GrowingOurImpactSerializer, StatisticsSerializer, EventSerializer, PartnerSerializer, ContactInfoSerializer, AwardSerializer, OurWorkSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hero_section_list(request):
    """List all hero sections"""
    hero_sections = HeroSection.objects.all().order_by('-created_at')
    serializer = HeroSectionSerializer(hero_sections, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hero_section_detail(request, pk):
    """Get a specific hero section"""
    try:
        hero_section = HeroSection.objects.get(pk=pk)
        serializer = HeroSectionSerializer(hero_section, context={'request': request})
        return Response(serializer.data)
    except HeroSection.DoesNotExist:
        return Response({'error': 'Hero section not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def hero_section_create(request):
    """Create a new hero section"""
    serializer = HeroSectionSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        hero_section = serializer.save()
        return Response(
            HeroSectionSerializer(hero_section, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def hero_section_update(request, pk):
    """Update a hero section"""
    try:
        hero_section = HeroSection.objects.get(pk=pk)
    except HeroSection.DoesNotExist:
        return Response({'error': 'Hero section not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = HeroSectionSerializer(
        hero_section, 
        data=request.data, 
        partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        hero_section = serializer.save()
        return Response(HeroSectionSerializer(hero_section, context={'request': request}).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def hero_section_delete(request, pk):
    """Delete a hero section"""
    try:
        hero_section = HeroSection.objects.get(pk=pk)
        hero_section.delete()
        return Response({'message': 'Hero section deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except HeroSection.DoesNotExist:
        return Response({'error': 'Hero section not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def hero_section_toggle_active(request, pk):
    """Toggle active status of a hero section"""
    try:
        hero_section = HeroSection.objects.get(pk=pk)
        hero_section.is_active = not hero_section.is_active
        hero_section.save()
        return Response(HeroSectionSerializer(hero_section, context={'request': request}).data)
    except HeroSection.DoesNotExist:
        return Response({'error': 'Hero section not found'}, status=status.HTTP_404_NOT_FOUND)


# Support Card API Views
@api_view(['GET'])
@permission_classes([AllowAny])
def support_card_list(request):
    """List all active support cards (public endpoint)"""
    support_cards = SupportCard.get_active_cards()
    serializer = SupportCardSerializer(support_cards, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def support_card_list_admin(request):
    """List all support cards for admin"""
    support_cards = SupportCard.objects.all().order_by('order', '-created_at')
    serializer = SupportCardSerializer(support_cards, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def support_card_detail(request, pk):
    """Get a specific support card"""
    try:
        support_card = SupportCard.objects.get(pk=pk)
        serializer = SupportCardSerializer(support_card, context={'request': request})
        return Response(serializer.data)
    except SupportCard.DoesNotExist:
        return Response({'error': 'Support card not found'}, status=status.HTTP_404_NOT_FOUND)


# Who We Are API Views
@api_view(['GET'])
@permission_classes([AllowAny])
def who_we_are_active(request):
    """Get the active Who We Are section (public endpoint)"""
    who_we_are = WhoWeAre.get_active()
    if who_we_are:
        serializer = WhoWeAreSerializer(who_we_are, context={'request': request})
        return Response(serializer.data)
    return Response({'message': 'No active Who We Are section'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def who_we_are_list_admin(request):
    """List all Who We Are sections for admin"""
    who_we_are_sections = WhoWeAre.objects.all().order_by('-created_at')
    serializer = WhoWeAreSerializer(who_we_are_sections, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def who_we_are_detail(request, pk):
    """Get a specific Who We Are section"""
    try:
        who_we_are = WhoWeAre.objects.get(pk=pk)
        serializer = WhoWeAreSerializer(who_we_are, context={'request': request})
        return Response(serializer.data)
    except WhoWeAre.DoesNotExist:
        return Response({'error': 'Who We Are section not found'}, status=status.HTTP_404_NOT_FOUND)


# Growing Our Impact API Views
@api_view(['GET'])
@permission_classes([AllowAny])
def growing_impact_active(request):
    """Get the active Growing Our Impact section (public endpoint)"""
    growing_impact = GrowingOurImpact.get_active()
    if growing_impact:
        serializer = GrowingOurImpactSerializer(growing_impact, context={'request': request})
        return Response(serializer.data)
    return Response({'message': 'No active Growing Our Impact section'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def growing_impact_list_admin(request):
    """List all Growing Our Impact sections for admin"""
    growing_impact_sections = GrowingOurImpact.objects.all().order_by('-created_at')
    serializer = GrowingOurImpactSerializer(growing_impact_sections, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def growing_impact_detail(request, pk):
    """Get a specific Growing Our Impact section"""
    try:
        growing_impact = GrowingOurImpact.objects.get(pk=pk)
        serializer = GrowingOurImpactSerializer(growing_impact, context={'request': request})
        return Response(serializer.data)
    except GrowingOurImpact.DoesNotExist:
        return Response({'error': 'Growing Our Impact section not found'}, status=status.HTTP_404_NOT_FOUND)


# Statistics API Views
@api_view(['GET'])
@permission_classes([AllowAny])
def statistics_active(request):
    """Get the active Statistics section (public endpoint)"""
    statistics = Statistics.get_active()
    if statistics:
        serializer = StatisticsSerializer(statistics)
        return Response(serializer.data)
    return Response({'message': 'No active Statistics section'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def statistics_list_admin(request):
    """List all Statistics sections for admin"""
    statistics_sections = Statistics.objects.all().order_by('-created_at')
    serializer = StatisticsSerializer(statistics_sections, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def statistics_detail(request, pk):
    """Get a specific Statistics section"""
    try:
        statistics = Statistics.objects.get(pk=pk)
        serializer = StatisticsSerializer(statistics)
        return Response(serializer.data)
    except Statistics.DoesNotExist:
        return Response({'error': 'Statistics section not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def statistics_create(request):
    """Create a new Statistics section"""
    serializer = StatisticsSerializer(data=request.data)
    if serializer.is_valid():
        statistics = serializer.save()
        return Response(
            StatisticsSerializer(statistics).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
def statistics_update(request, pk):
    """Update a Statistics section"""
    try:
        statistics = Statistics.objects.get(pk=pk)
    except Statistics.DoesNotExist:
        return Response({'error': 'Statistics section not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = StatisticsSerializer(
        statistics,
        data=request.data,
        partial=True
    )
    if serializer.is_valid():
        statistics = serializer.save()
        return Response(StatisticsSerializer(statistics).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def statistics_delete(request, pk):
    """Delete a Statistics section"""
    try:
        statistics = Statistics.objects.get(pk=pk)
        statistics.delete()
        return Response({'message': 'Statistics section deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Statistics.DoesNotExist:
        return Response({'error': 'Statistics section not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def statistics_toggle_active(request, pk):
    """Toggle active status of a Statistics section"""
    try:
        statistics = Statistics.objects.get(pk=pk)
        statistics.is_active = not statistics.is_active
        statistics.save()
        return Response(StatisticsSerializer(statistics).data)
    except Statistics.DoesNotExist:
        return Response({'error': 'Statistics section not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def growing_impact_create(request):
    """Create a new Growing Our Impact section"""
    serializer = GrowingOurImpactSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        growing_impact = serializer.save()
        return Response(
            GrowingOurImpactSerializer(growing_impact, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def growing_impact_update(request, pk):
    """Update a Growing Our Impact section"""
    try:
        growing_impact = GrowingOurImpact.objects.get(pk=pk)
    except GrowingOurImpact.DoesNotExist:
        return Response({'error': 'Growing Our Impact section not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = GrowingOurImpactSerializer(
        growing_impact,
        data=request.data,
        partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        growing_impact = serializer.save()
        return Response(GrowingOurImpactSerializer(growing_impact, context={'request': request}).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def growing_impact_delete(request, pk):
    """Delete a Growing Our Impact section"""
    try:
        growing_impact = GrowingOurImpact.objects.get(pk=pk)
        growing_impact.delete()
        return Response({'message': 'Growing Our Impact section deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except GrowingOurImpact.DoesNotExist:
        return Response({'error': 'Growing Our Impact section not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def growing_impact_toggle_active(request, pk):
    """Toggle active status of a Growing Our Impact section"""
    try:
        growing_impact = GrowingOurImpact.objects.get(pk=pk)
        growing_impact.is_active = not growing_impact.is_active
        growing_impact.save()
        return Response(GrowingOurImpactSerializer(growing_impact, context={'request': request}).data)
    except GrowingOurImpact.DoesNotExist:
        return Response({'error': 'Growing Our Impact section not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def who_we_are_create(request):
    """Create a new Who We Are section"""
    serializer = WhoWeAreSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        who_we_are = serializer.save()
        return Response(
            WhoWeAreSerializer(who_we_are, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def who_we_are_update(request, pk):
    """Update a Who We Are section"""
    try:
        who_we_are = WhoWeAre.objects.get(pk=pk)
    except WhoWeAre.DoesNotExist:
        return Response({'error': 'Who We Are section not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = WhoWeAreSerializer(
        who_we_are,
        data=request.data,
        partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        who_we_are = serializer.save()
        return Response(WhoWeAreSerializer(who_we_are, context={'request': request}).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def who_we_are_delete(request, pk):
    """Delete a Who We Are section"""
    try:
        who_we_are = WhoWeAre.objects.get(pk=pk)
        who_we_are.delete()
        return Response({'message': 'Who We Are section deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except WhoWeAre.DoesNotExist:
        return Response({'error': 'Who We Are section not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def who_we_are_toggle_active(request, pk):
    """Toggle active status of a Who We Are section"""
    try:
        who_we_are = WhoWeAre.objects.get(pk=pk)
        who_we_are.is_active = not who_we_are.is_active
        who_we_are.save()
        return Response(WhoWeAreSerializer(who_we_are, context={'request': request}).data)
    except WhoWeAre.DoesNotExist:
        return Response({'error': 'Who We Are section not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def support_card_create(request):
    """Create a new support card"""
    serializer = SupportCardSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        support_card = serializer.save()
        return Response(
            SupportCardSerializer(support_card, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def support_card_update(request, pk):
    """Update a support card"""
    try:
        support_card = SupportCard.objects.get(pk=pk)
    except SupportCard.DoesNotExist:
        return Response({'error': 'Support card not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = SupportCardSerializer(
        support_card, 
        data=request.data, 
        partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        support_card = serializer.save()
        return Response(SupportCardSerializer(support_card, context={'request': request}).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def support_card_delete(request, pk):
    """Delete a support card"""
    try:
        support_card = SupportCard.objects.get(pk=pk)
        support_card.delete()
        return Response({'message': 'Support card deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except SupportCard.DoesNotExist:
        return Response({'error': 'Support card not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def support_card_toggle_active(request, pk):
    """Toggle active status of a support card"""
    try:
        support_card = SupportCard.objects.get(pk=pk)
        support_card.is_active = not support_card.is_active
        support_card.save()
        return Response(SupportCardSerializer(support_card, context={'request': request}).data)
    except SupportCard.DoesNotExist:
        return Response({'error': 'Support card not found'}, status=status.HTTP_404_NOT_FOUND)

# Event API Views
@api_view(['GET'])
@permission_classes([AllowAny])
def event_list(request):
    """List all active events (public endpoint)"""
    events = Event.get_active_events()
    serializer = EventSerializer(events, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_list_admin(request):
    """List all events for admin"""
    events = Event.objects.all().order_by('order', '-created_at')
    serializer = EventSerializer(events, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_detail(request, pk):
    """Get a specific event"""
    try:
        event = Event.objects.get(pk=pk)
        serializer = EventSerializer(event, context={'request': request})
        return Response(serializer.data)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def event_create(request):
    """Create a new event"""
    serializer = EventSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        event = serializer.save()
        return Response(
            EventSerializer(event, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def event_update(request, pk):
    """Update an event"""
    try:
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = EventSerializer(
        event, 
        data=request.data, 
        partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        event = serializer.save()
        return Response(EventSerializer(event, context={'request': request}).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def event_delete(request, pk):
    """Delete an event"""
    try:
        event = Event.objects.get(pk=pk)
        event.delete()
        return Response({'message': 'Event deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def event_toggle_active(request, pk):
    """Toggle active status of an event"""
    try:
        event = Event.objects.get(pk=pk)
        event.is_active = not event.is_active
        event.save()
        return Response(EventSerializer(event, context={'request': request}).data)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
# Partner API Views
@api_view(['GET'])
@permission_classes([AllowAny])
def partner_list(request):
    """List all active partners (public endpoint)"""
    partners = Partner.get_active_partners()
    serializer = PartnerSerializer(partners, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def partner_list_admin(request):
    """List all partners for admin"""
    partners = Partner.objects.all().order_by('order', '-created_at')
    serializer = PartnerSerializer(partners, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def partner_detail(request, pk):
    """Get a specific partner"""
    try:
        partner = Partner.objects.get(pk=pk)
        serializer = PartnerSerializer(partner, context={'request': request})
        return Response(serializer.data)
    except Partner.DoesNotExist:
        return Response({'error': 'Partner not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def partner_create(request):
    """Create a new partner"""
    serializer = PartnerSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        partner = serializer.save()
        return Response(
            PartnerSerializer(partner, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def partner_update(request, pk):
    """Update a partner"""
    try:
        partner = Partner.objects.get(pk=pk)
    except Partner.DoesNotExist:
        return Response({'error': 'Partner not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = PartnerSerializer(
        partner, 
        data=request.data, 
        partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        partner = serializer.save()
        return Response(PartnerSerializer(partner, context={'request': request}).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def partner_delete(request, pk):
    """Delete a partner"""
    try:
        partner = Partner.objects.get(pk=pk)
        partner.delete()
        return Response({'message': 'Partner deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Partner.DoesNotExist:
        return Response({'error': 'Partner not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def partner_toggle_active(request, pk):
    """Toggle active status of a partner"""
    try:
        partner = Partner.objects.get(pk=pk)
        partner.is_active = not partner.is_active
        partner.save()
        return Response(PartnerSerializer(partner, context={'request': request}).data)
    except Partner.DoesNotExist:
        return Response({'error': 'Partner not found'}, status=status.HTTP_404_NOT_FOUND)
# Contact Info API Views
@api_view(['GET'])
@permission_classes([AllowAny])
def contact_info_active(request):
    """Get the active contact info (public endpoint)"""
    contact_info = ContactInfo.get_active()
    if contact_info:
        serializer = ContactInfoSerializer(contact_info)
        return Response(serializer.data)
    return Response({'message': 'No active contact info'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contact_info_list_admin(request):
    """List all contact info for admin"""
    contact_infos = ContactInfo.objects.all().order_by('-created_at')
    serializer = ContactInfoSerializer(contact_infos, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def contact_info_create(request):
    """Create new contact info"""
    serializer = ContactInfoSerializer(data=request.data)
    if serializer.is_valid():
        contact_info = serializer.save()
        return Response(ContactInfoSerializer(contact_info).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
def contact_info_update(request, pk):
    """Update contact info"""
    try:
        contact_info = ContactInfo.objects.get(pk=pk)
    except ContactInfo.DoesNotExist:
        return Response({'error': 'Contact info not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ContactInfoSerializer(contact_info, data=request.data, partial=True)
    if serializer.is_valid():
        contact_info = serializer.save()
        return Response(ContactInfoSerializer(contact_info).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def contact_info_delete(request, pk):
    """Delete contact info"""
    try:
        contact_info = ContactInfo.objects.get(pk=pk)
        contact_info.delete()
        return Response({'message': 'Contact info deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except ContactInfo.DoesNotExist:
        return Response({'error': 'Contact info not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def contact_info_toggle_active(request, pk):
    """Toggle active status of contact info"""
    try:
        contact_info = ContactInfo.objects.get(pk=pk)
        contact_info.is_active = not contact_info.is_active
        contact_info.save()
        return Response(ContactInfoSerializer(contact_info).data)
    except ContactInfo.DoesNotExist:
        return Response({'error': 'Contact info not found'}, status=status.HTTP_404_NOT_FOUND)
# Award API Views
@api_view(['GET'])
@permission_classes([AllowAny])
def award_list(request):
    """List all active awards (public endpoint)"""
    awards = Award.get_active_awards()
    serializer = AwardSerializer(awards, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def award_list_admin(request):
    """List all awards for admin"""
    awards = Award.objects.all().order_by('order', '-created_at')
    serializer = AwardSerializer(awards, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def award_detail(request, pk):
    """Get a specific award"""
    try:
        award = Award.objects.get(pk=pk)
        serializer = AwardSerializer(award, context={'request': request})
        return Response(serializer.data)
    except Award.DoesNotExist:
        return Response({'error': 'Award not found'}, status=status.HTTP_404_NOT_FOUND)

# Our Work API Views
@api_view(['GET'])
@permission_classes([AllowAny])
def our_work_list(request):
    """List all active our work items (public endpoint)"""
    our_works = OurWork.get_active_works()
    serializer = OurWorkSerializer(our_works, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def our_work_list_admin(request):
    """List all our work items for admin"""
    our_works = OurWork.objects.all().order_by('order', '-created_at')
    serializer = OurWorkSerializer(our_works, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def our_work_detail(request, navlink):
    """Get a specific our work item by navlink (public endpoint)"""
    try:
        our_work = OurWork.objects.get(navlink=navlink, is_active=True)
        serializer = OurWorkSerializer(our_work, context={'request': request})
        return Response(serializer.data)
    except OurWork.DoesNotExist:
        return Response({'error': 'Our work item not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def our_work_detail_admin(request, pk):
    """Get a specific our work item for admin"""
    try:
        our_work = OurWork.objects.get(pk=pk)
        serializer = OurWorkSerializer(our_work, context={'request': request})
        return Response(serializer.data)
    except OurWork.DoesNotExist:
        return Response({'error': 'Our work item not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def our_work_create(request):
    """Create a new our work item"""
    serializer = OurWorkSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        our_work = serializer.save()
        return Response(
            OurWorkSerializer(our_work, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def our_work_update(request, pk):
    """Update an our work item"""
    try:
        our_work = OurWork.objects.get(pk=pk)
    except OurWork.DoesNotExist:
        return Response({'error': 'Our work item not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = OurWorkSerializer(
        our_work,
        data=request.data,
        partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        our_work = serializer.save()
        return Response(OurWorkSerializer(our_work, context={'request': request}).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def our_work_delete(request, pk):
    """Delete an our work item"""
    try:
        our_work = OurWork.objects.get(pk=pk)
        our_work.delete()
        return Response({'message': 'Our work item deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except OurWork.DoesNotExist:
        return Response({'error': 'Our work item not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def our_work_toggle_active(request, pk):
    """Toggle active status of an our work item"""
    try:
        our_work = OurWork.objects.get(pk=pk)
        our_work.is_active = not our_work.is_active
        our_work.save()
        return Response(OurWorkSerializer(our_work, context={'request': request}).data)
    except OurWork.DoesNotExist:
        return Response({'error': 'Our work item not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def award_create(request):
    """Create a new award"""
    serializer = AwardSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        award = serializer.save()
        return Response(
            AwardSerializer(award, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def award_update(request, pk):
    """Update an award"""
    try:
        award = Award.objects.get(pk=pk)
    except Award.DoesNotExist:
        return Response({'error': 'Award not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = AwardSerializer(
        award, 
        data=request.data, 
        partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        award = serializer.save()
        return Response(AwardSerializer(award, context={'request': request}).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def award_delete(request, pk):
    """Delete an award"""
    try:
        award = Award.objects.get(pk=pk)
        award.delete()
        return Response({'message': 'Award deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Award.DoesNotExist:
        return Response({'error': 'Award not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def award_toggle_active(request, pk):
    """Toggle active status of an award"""
    try:
        award = Award.objects.get(pk=pk)
        award.is_active = not award.is_active
        award.save()
        return Response(AwardSerializer(award, context={'request': request}).data)
    except Award.DoesNotExist:
        return Response({'error': 'Award not found'}, status=status.HTTP_404_NOT_FOUND)