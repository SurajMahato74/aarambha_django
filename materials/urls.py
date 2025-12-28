from django.urls import path
from . import views

urlpatterns = [
    path('my-materials/', views.MyMaterialsAPI.as_view(), name='my_materials'),
    path('admin-materials/', views.AdminMaterialsAPI.as_view(), name='admin_materials'),
    path('admin-materials/<int:pk>/', views.AdminMaterialsAPI.as_view(), name='admin_materials_detail'),
    path('categories/', views.MaterialCategoriesAPI.as_view(), name='material_categories'),
]