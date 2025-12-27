from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from .models import HeroSection, SupportCard, WhoWeAre, GrowingOurImpact, Statistics, Event, Partner, ContactInfo, Award, OurWork, SchoolDropoutReport
from .serializers import HeroSectionSerializer, SupportCardSerializer, WhoWeAreSerializer, GrowingOurImpactSerializer, StatisticsSerializer, EventSerializer, PartnerSerializer, ContactInfoSerializer, AwardSerializer, OurWorkSerializer, SchoolDropoutReportSerializer

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


# School Dropout Report API Views
@api_view(['POST'])
@permission_classes([AllowAny])
def school_dropout_report_create(request):
    """Create a new school dropout report (public endpoint)"""
    from django.core.mail import send_mail
    from django.conf import settings

    serializer = SchoolDropoutReportSerializer(data=request.data)
    if serializer.is_valid():
        report = serializer.save()

        # Send confirmation email to the reporter
        try:
            subject = '📋 School Dropout Report Submitted - Aarambha Foundation'
            message = f'''Dear {report.reporter_name},

Thank you for submitting a school dropout report to Aarambha Foundation.

Your report details:
- Child's Name: {report.dropout_name}
- School: {report.school_name}
- Location: {report.school_location}, {report.district}

We appreciate your contribution to helping children return to education. Our team will review this report and take appropriate action.

If you have any additional information or questions, please don't hesitate to contact us.

Warm regards,
Aarambha Foundation Team
Email: we.aarambha@gmail.com
Phone: +977 (984)346-7402'''

            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [report.reporter_email],
                fail_silently=False,
            )
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Failed to send confirmation email: {e}")

        return Response(
            SchoolDropoutReportSerializer(report).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def school_dropout_report_list_admin(request):
    """List all school dropout reports for admin"""
    reports = SchoolDropoutReport.objects.all().order_by('-created_at')

    # Filters
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    district = request.GET.get('district', '')
    gender = request.GET.get('gender', '')

    if search:
        reports = reports.filter(
            Q(dropout_name__icontains=search) |
            Q(school_name__icontains=search) |
            Q(reporter_name__icontains=search) |
            Q(reporter_email__icontains=search)
        )
    if status_filter:
        reports = reports.filter(status=status_filter)
    if district:
        reports = reports.filter(district=district)
    if gender:
        reports = reports.filter(dropout_gender=gender)

    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    start = (page - 1) * page_size
    end = start + page_size

    total = reports.count()
    reports_page = reports[start:end]

    serializer = SchoolDropoutReportSerializer(reports_page, many=True)
    return Response({
        'results': serializer.data,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def school_dropout_report_detail_admin(request, pk):
    """Get a specific school dropout report for admin"""
    try:
        report = SchoolDropoutReport.objects.get(pk=pk)
        serializer = SchoolDropoutReportSerializer(report)
        return Response(serializer.data)
    except SchoolDropoutReport.DoesNotExist:
        return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def school_dropout_report_update_status(request, pk):
    """Update status of a school dropout report"""
    try:
        report = SchoolDropoutReport.objects.get(pk=pk)
        new_status = request.data.get('status')
        if new_status in ['pending', 'investigated', 'resolved']:
            report.status = new_status
            report.save()
            return Response(SchoolDropoutReportSerializer(report).data)
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
    except SchoolDropoutReport.DoesNotExist:
        return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)


# Khalti Payment Integration for Donations
import requests
import uuid
import logging
from decimal import Decimal
from django.utils import timezone
from .models import Donation
from django.conf import settings

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def donation_initiate_payment(request):
    """
    Initiate a donation payment with Khalti.
    Creates a donation record and initiates Khalti payment.
    """
    try:
        logger.info("Starting donation_initiate_payment")
        # Extract donation data
        title = request.data.get('title', 'Mr.')
        full_name = request.data.get('full_name')
        email = request.data.get('email')
        phone = request.data.get('phone', '')
        amount = request.data.get('amount')
        logger.info(f"Received data: title={title}, full_name={full_name}, email={email}, phone={phone}, amount={amount}")
        
        # Validate required fields
        if not full_name or not email or not amount:
            return Response(
                {'error': 'full_name, email, and amount are required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate amount
        try:
            amount = Decimal(str(amount))
            logger.info(f"Amount converted to Decimal: {amount}")
            if amount < 10:
                return Response(
                    {'error': 'Amount should be greater than Rs. 10'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if amount > 200:
                return Response(
                    {'error': 'Amount should not exceed Rs. 200. For larger donations, please contact us directly.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f"Amount validation error: {e}")
            return Response(
                {'error': 'Invalid amount format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate unique purchase order ID
        purchase_order_id = f"DON-{uuid.uuid4().hex[:12].upper()}"
        logger.info(f"Generated purchase_order_id: {purchase_order_id}")

        # Create donation record
        try:
            donation = Donation.objects.create(
                title=title,
                full_name=full_name,
                email=email,
                phone=phone,
                amount=amount,
                purchase_order_id=purchase_order_id,
                payment_status='initiated'
            )
            logger.info(f"Donation created with ID: {donation.id}")
        except Exception as e:
            logger.error(f"Error creating donation: {e}")
            raise
        
        # Get Khalti credentials from settings
        khalti_secret_key = getattr(settings, 'KHALTI_SECRET_KEY', 'live_secret_key_9fa11bce45e44676bb9040b5354a3918')
        logger.info(f"Using Khalti secret key: {khalti_secret_key[:10]}...")

        # Get return URL from request or use default
        base_url = request.build_absolute_uri('/').rstrip('/')
        return_url = f"{base_url}/donation/callback/"
        website_url = base_url
        logger.info(f"Return URL: {return_url}, Website URL: {website_url}")

        # Prepare Khalti payment initiate payload
        khalti_payload = {
            "return_url": return_url,
            "website_url": website_url,
            "amount": donation.amount_in_paisa,
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": f"Donation by {full_name}",
            "customer_info": {
                "name": full_name,
                "email": email,
                "phone": phone if phone else "9800000000"
            }
        }
        logger.info(f"Khalti payload: {khalti_payload}")

        # Make request to Khalti API
        khalti_url = "https://pay.khalti.com/api/v2/epayment/initiate/"
        headers = {
            'Authorization': f'key {khalti_secret_key}',
            'Content-Type': 'application/json',
        }
        logger.info(f"Making request to Khalti API: {khalti_url}")

        try:
            response = requests.post(khalti_url, json=khalti_payload, headers=headers, timeout=30)
            logger.info(f"Khalti API response status: {response.status_code}")
        except Exception as e:
            logger.error(f"Request to Khalti API failed: {e}")
            raise
        
        if response.status_code == 200:
            try:
                khalti_response = response.json()
                logger.info(f"Khalti response: {khalti_response}")
            except Exception as e:
                logger.error(f"Failed to parse Khalti response JSON: {e}, content: {response.text}")
                raise

            # Update donation with Khalti response
            try:
                donation.pidx = khalti_response.get('pidx')
                donation.payment_url = khalti_response.get('payment_url')
                donation.save()
                logger.info(f"Donation updated with pidx: {donation.pidx}")
            except Exception as e:
                logger.error(f"Failed to update donation: {e}")
                raise

            return Response({
                'success': True,
                'donation_id': donation.id,
                'purchase_order_id': purchase_order_id,
                'pidx': khalti_response.get('pidx'),
                'payment_url': khalti_response.get('payment_url'),
                'expires_at': khalti_response.get('expires_at'),
                'expires_in': khalti_response.get('expires_in'),
                'full_response': khalti_response  # For debugging
            }, status=status.HTTP_200_OK)
        else:
            # Khalti API error
            logger.error(f"Khalti API error status: {response.status_code}, content: {response.text}")
            donation.payment_status = 'failed'
            donation.save()

            try:
                error_data = response.json() if response.content else {'error': 'Unknown error'}
            except:
                error_data = {'error': 'Failed to parse error response', 'content': response.text}
            return Response({
                'error': 'Failed to initiate payment with Khalti',
                'details': error_data
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Unexpected error in donation_initiate_payment: {e}", exc_info=True)
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def donation_verify_payment(request):
    """
    Verify a donation payment with Khalti.
    This endpoint is called to confirm the payment status.
    """
    try:
        pidx = request.data.get('pidx')
        token = request.data.get('token')  # transaction_id from callback
        amount = request.data.get('amount')

        if not pidx:
            return Response(
                {'error': 'pidx is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find donation by pidx
        try:
            donation = Donation.objects.get(pidx=pidx)
        except Donation.DoesNotExist:
            return Response(
                {'error': 'Donation not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Idempotency: If already verified, return success
        if donation.payment_status == 'completed':
            return Response({
                'success': True,
                'donation_id': donation.id,
                'purchase_order_id': donation.purchase_order_id,
                'status': donation.payment_status,
                'transaction_id': donation.transaction_id,
                'amount': str(donation.amount),
                'fee': str(donation.fee),
                'refunded': donation.refunded,
                'message': 'Payment already verified'
            }, status=status.HTTP_200_OK)

        # Get Khalti credentials from settings
        khalti_secret_key = getattr(settings, 'KHALTI_SECRET_KEY', 'live_secret_key_9fa11bce45e44676bb9040b5354a3918')

        # Use ePayment lookup API as per Khalti support recommendation
        khalti_url = "https://pay.khalti.com/api/v2/epayment/lookup/"
        headers = {
            'Authorization': f'key {khalti_secret_key}',
            'Content-Type': 'application/json',
        }

        lookup_payload = {"pidx": pidx}
        response = requests.post(khalti_url, json=lookup_payload, headers=headers)

        if response.status_code == 200:
            khalti_response = response.json()

            # Update donation with lookup response
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
            donation.fee = Decimal(str(khalti_response.get('fee', 0))) / 100  # Convert paisa to rupees
            donation.refunded = khalti_response.get('refunded', False)

            if donation.payment_status == 'completed' and not donation.completed_at:
                donation.completed_at = timezone.now()

            donation.save()

            return Response({
                'success': True,
                'donation_id': donation.id,
                'purchase_order_id': donation.purchase_order_id,
                'status': donation.payment_status,
                'transaction_id': donation.transaction_id,
                'amount': str(donation.amount),
                'fee': str(donation.fee),
                'refunded': donation.refunded,
                'full_response': khalti_response
            }, status=status.HTTP_200_OK)
        else:
            # Lookup failed
            error_data = response.json() if response.content else {'error': 'Unknown error'}
            return Response({
                'error': 'Failed to verify payment with Khalti',
                'details': error_data
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def donation_list_admin(request):
    """List all donations for admin"""
    donations = Donation.objects.all().order_by('-created_at')
    
    # Filters
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search:
        donations = donations.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(purchase_order_id__icontains=search) |
            Q(transaction_id__icontains=search)
        )
    if status_filter:
        donations = donations.filter(payment_status=status_filter)
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    
    total = donations.count()
    donations_page = donations[start:end]
    
    # Serialize data
    data = [{
        'id': d.id,
        'title': d.title,
        'full_name': d.full_name,
        'email': d.email,
        'phone': d.phone,
        'amount': str(d.amount),
        'purchase_order_id': d.purchase_order_id,
        'transaction_id': d.transaction_id,
        'payment_status': d.payment_status,
        'refunded': d.refunded,
        'created_at': d.created_at.isoformat(),
        'completed_at': d.completed_at.isoformat() if d.completed_at else None
    } for d in donations_page]
    
    return Response({
        'results': data,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    })
