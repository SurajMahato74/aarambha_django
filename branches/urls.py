from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.list_branches, name='list_branches'),
    path('create/', views.create_branch, name='create_branch'),
]
