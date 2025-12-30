from django.urls import path
from . import views

urlpatterns = [
    path('members/', views.member_list, name='member_list'),
    path('conversations/', views.conversations, name='conversations'),
    path('chat/<str:type>/<int:id>/', views.chat, name='chat'),
    path('send-message/', views.send_message, name='send_message'),
    path('start-conversation/', views.start_conversation, name='start_conversation'),
    path('handle-request/', views.handle_message_request, name='handle_message_request'),
    path('create-group/', views.create_group, name='create_group'),
    path('get-conversation/<int:user_id>/', views.get_conversation, name='get_conversation'),
    path('get-messages/<int:conversation_id>/', views.get_messages, name='get_messages'),
    path('send-message-ajax/', views.send_message_ajax, name='send_message_ajax'),
    path('user-profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('leave-group/', views.leave_group, name='leave_group'),
]