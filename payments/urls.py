from django.urls import path
from . import api_views

urlpatterns = [
    path('my-payments/', api_views.my_payments, name='my_payments'),
]