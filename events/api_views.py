from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Event, EventParticipation, EventCertificate
from .serializers import EventSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_events(request):
    """List all events"""
    events = Event.objects.filter(is_active=True).order_by('-start_datetime')
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_event(request):
    """Create a new event"""
    serializer = EventSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_detail(request, pk):
    """Get event details"""
    event = get_object_or_404(Event, pk=pk)
    serializer = EventSerializer(event)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_certificates(request):
    """Get current user's certificates"""
    participations = EventParticipation.objects.filter(
        user=request.user, 
        attended=True,
        certificate_id__isnull=False
    ).select_related('event').order_by('-attendance_marked_at')
    
    data = []
    for participation in participations:
        data.append({
            'id': participation.certificate_id,
            'event_title': participation.event.title,
            'event_id': participation.event.id,
            'issued_at': participation.attendance_marked_at.isoformat() if participation.attendance_marked_at else participation.event.end_datetime.isoformat(),
        })
    
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_reviews(request):
    """Get current user's event reviews"""
    reviews = EventParticipation.objects.filter(
        user=request.user,
        review__isnull=False
    ).exclude(review='').select_related('event').order_by('-updated_at')
    
    data = []
    for review in reviews:
        data.append({
            'id': review.id,
            'event_title': review.event.title,
            'event_id': review.event.id,
            'rating': review.rating,
            'review': review.review,
            'created_at': review.updated_at.isoformat(),
        })
    
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_events(request):
    """Get current user's events"""
    participations = EventParticipation.objects.filter(
        user=request.user
    ).select_related('event').order_by('-applied_at')
    
    data = []
    for participation in participations:
        data.append({
            'id': participation.event.id,
            'title': participation.event.title,
            'status': participation.status,
            'attended': participation.attended,
            'start_datetime': participation.event.start_datetime.isoformat(),
            'end_datetime': participation.event.end_datetime.isoformat(),
        })
    
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_certificate(request, cert_id):
    """View certificate by certificate ID"""
    try:
        participation = EventParticipation.objects.get(
            certificate_id=cert_id,
            user=request.user,
            attended=True
        )
        
        context = {
            'event': participation.event,
            'user': request.user,
            'participation': participation,
            'certificate_date': participation.attendance_marked_at or participation.event.end_datetime,
        }
        
        html_content = render_to_string('events/certificate.html', context)
        return HttpResponse(html_content)
        
    except EventParticipation.DoesNotExist:
        return HttpResponse('<h1>Certificate not found</h1>', status=404)