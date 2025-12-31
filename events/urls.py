from django.urls import path
from . import views

urlpatterns = [
    path('admin/event-management/', views.admin_events, name='admin_event_management'),
    path('admin/event-management/<int:event_id>/participations/', views.admin_event_participations, name='admin_event_participations'),
    path('member/events/', views.member_events, name='member_events'),
    path('volunteer/events/', views.member_events, name='volunteer_events'),
    path('events/<int:event_id>/reviews/', views.event_reviews, name='event_reviews'),
    path('events/<int:event_id>/certificate/', views.event_certificate, name='event_certificate'),
    path('api/events/<int:event_id>/', views.get_event_details, name='get_event_details'),
]