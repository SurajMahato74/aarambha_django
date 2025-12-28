from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_branches_simple, name='list_branches_simple'),
    path('list/', views.list_branches, name='list_branches'),
    path('create/', views.create_branch, name='create_branch'),
    path('<int:branch_id>/assign-admin/', views.assign_branch_admin, name='assign_branch_admin'),
]
