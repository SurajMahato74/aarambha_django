from django.urls import path
from . import api_views

urlpatterns = [
    path('create/', api_views.create_event, name='create_event'),
    path('', api_views.list_events, name='list_events'),
    path('<int:pk>/', api_views.event_detail, name='event_detail'),
    path('my-events/', api_views.my_events, name='my_events'),
    path('my-certificates/', api_views.my_certificates, name='my_certificates'),
    path('my-reviews/', api_views.my_reviews, name='my_reviews'),
    path('certificate/<str:cert_id>/view/', api_views.view_certificate, name='view_certificate'),
]