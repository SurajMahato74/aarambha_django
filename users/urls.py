from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('list/', views.list_users, name='list_users'),
    path('update/<int:user_id>/', views.update_user, name='update_user'),
    path('detail/<int:user_id>/', views.get_user, name='get_user'),
]
