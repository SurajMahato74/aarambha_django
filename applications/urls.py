from django.urls import path
from . import views, khalti_views

urlpatterns = [
    path('submit/', views.submit_application, name='submit_application'),
    path('list/', views.list_applications, name='list_applications'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('<int:pk>/', views.get_application, name='get_application'),
    path('<int:pk>/update-status/', views.update_application_status, name='update_application_status'),
    path('<int:pk>/acknowledge/', views.acknowledge_interview, name='acknowledge_interview'),
    path('<int:pk>/initiate-payment/', khalti_views.initiate_khalti_payment, name='initiate_payment'),
    path('<int:pk>/verify-payment/', khalti_views.verify_khalti_payment, name='verify_payment'),
]
