from django.urls import path
from . import views

urlpatterns = [
    path('my-notifications/', views.my_notifications, name='my_notifications'),
    path('mark-read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
    path('notices/', views.NoticesAPI.as_view(), name='notices_api'),
    path('admin/notices/', views.AdminNoticesAPI.as_view(), name='admin_notices_api'),
    path('admin/notices/<int:notice_id>/', views.AdminNoticesAPI.as_view(), name='admin_notice_detail_api'),
]