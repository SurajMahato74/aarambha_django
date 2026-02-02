from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('my-tasks/', views.MyTasksAPI.as_view(), name='my_tasks_api'),
    path('<int:task_id>/submit/', views.SubmitTaskAPI.as_view(), name='submit_task_api'),
    path('admin/all-tasks/', views.AdminTasksAPI.as_view(), name='admin_tasks_api'),
    path('admin/<int:task_id>/detail/', views.TaskDetailAPI.as_view(), name='task_detail_api'),
    path('admin/<int:task_id>/submission/<int:user_id>/', views.SubmissionDetailAPI.as_view(), name='submission_detail_api'),
    path('admin/<int:task_id>/review/', views.ReviewTaskAPI.as_view(), name='review_task_api'),
    path('admin/<int:task_id>/review/<int:user_id>/', views.ReviewSubmissionAPI.as_view(), name='review_submission_api'),
    path('admin/create/', views.CreateTaskAPI.as_view(), name='create_task_api'),
    path('admin/email-status/', views.EmailStatusAPI.as_view(), name='email_status_api'),
]