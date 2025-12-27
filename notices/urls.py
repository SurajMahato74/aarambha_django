from django.urls import path
from . import views

urlpatterns = [
    path('my-notifications/', views.my_notifications, name='my_notifications'),
    path('mark-read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
]