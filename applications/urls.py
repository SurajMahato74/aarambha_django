from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_application, name='submit_application'),
    path('list/', views.list_applications, name='list_applications'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('<int:pk>/', views.get_application, name='get_application'),
    path('<int:pk>/update/', views.UpdateApplicationView.as_view(), name='update_application'),
    path('<int:pk>/update-status/', views.update_application_status, name='update_application_status'),
    path('<int:pk>/approve-upgrade/', views.approve_upgrade, name='approve_upgrade'),
    path('auto-upgrade/', views.auto_upgrade_to_member, name='auto_upgrade_to_member'),
    path('<int:pk>/resend-email/', views.resend_email, name='resend_email'),
    path('<int:pk>/acknowledge/', views.acknowledge_interview, name='acknowledge_interview'),
    path('<int:pk>/initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('<int:pk>/verify-payment/', views.verify_payment, name='verify_payment'),
    path('<int:pk>/confirm-test-payment/', views.confirm_test_payment, name='confirm_test_payment'),
    
    # Child Sponsorship URLs
    path('sponsorships/submit/', views.submit_sponsorship, name='submit_sponsorship'),
    path('sponsorships/my/', views.my_sponsorships, name='my_sponsorships'),
    path('sponsorships/list/', views.list_sponsorships, name='list_sponsorships'),
    path('sponsorships/<int:pk>/', views.get_sponsorship, name='get_sponsorship'),
    path('sponsorships/<int:pk>/update-status/', views.update_sponsorship_status, name='update_sponsorship_status'),
    path('sponsorships/<int:pk>/update/', views.update_sponsorship, name='update_sponsorship'),
    path('sponsorships/<int:pk>/assign-children/', views.assign_children_to_sponsor, name='assign_children_to_sponsor'),
    
    # Children Management URLs
    path('children/', views.children_api, name='children_api'),
    path('children/<int:pk>/', views.child_detail_api, name='child_detail_api'),
    path('children/<int:pk>/make-available/', views.make_child_available, name='make_child_available'),
    path('children/stats/', views.children_stats, name='children_stats'),
    
    # Sponsor URLs
    path('my-assignments/', views.my_child_assignments, name='my_child_assignments'),
    path('assignments/<int:assignment_id>/approve/', views.approve_child_assignment, name='approve_child_assignment'),
    path('assignments/<int:assignment_id>/reject/', views.reject_child_assignment, name='reject_child_assignment'),
    path('simple-approve/<int:assignment_id>/', views.simple_approve_assignment, name='simple_approve_assignment'),
    path('simple-reject/<int:assignment_id>/', views.simple_reject_assignment, name='simple_reject_assignment'),
    path('simple-payment/<int:child_id>/', views.simple_initiate_payment, name='simple_initiate_payment'),
    path('simple-payment-details/<int:child_id>/', views.simple_initiate_payment_details, name='simple_initiate_payment_details'),
    path('my-sponsored-children/', views.my_sponsored_children, name='my_sponsored_children'),
    
    # Assignment Management URLs
    path('sponsorships/<int:pk>/assignments/', views.get_sponsorship_assignments, name='get_sponsorship_assignments'),
    path('assignments/<int:assignment_id>/remove/', views.remove_assignment, name='remove_assignment'),
    
    # Child Payment URLs
    path('child-payment/<int:child_id>/initiate/', views.initiate_child_payment, name='initiate_child_payment'),
    path('child-payment/<int:installment_id>/verify/', views.verify_child_payment, name='verify_child_payment'),
    path('child-payments/<int:child_id>/', views.get_child_payments, name='get_child_payments'),
    path('cancel-sponsorship/<int:child_id>/', views.cancel_sponsorship, name='cancel_sponsorship'),
    path('my-sponsorship-history/', views.my_sponsorship_history, name='my_sponsorship_history'),
    
    # Admin Payment Management URLs
    path('child-payments/stats/', views.admin_payment_stats, name='admin_payment_stats'),
    path('child-payments/', views.admin_payment_list, name='admin_payment_list'),
    path('child-payments/<int:payment_id>/', views.admin_payment_detail, name='admin_payment_detail'),
    path('child-payments/<int:payment_id>/mark-completed/', views.admin_mark_payment_completed, name='admin_mark_payment_completed'),
    
    # One Rupee Campaign URLs
    path('one-rupee-campaign/enroll/', views.enroll_one_rupee_campaign, name='enroll_one_rupee_campaign'),
    path('one-rupee-campaign/<int:campaign_id>/initiate-payment/', views.initiate_campaign_payment, name='initiate_campaign_payment'),
    path('campaign-payment/<int:payment_id>/verify/', views.verify_campaign_payment, name='verify_campaign_payment'),
    path('my-campaign-status/', views.my_campaign_status, name='my_campaign_status'),
    
    # Admin Campaign Management URLs
    path('admin-campaign-stats/', views.admin_campaign_stats, name='admin_campaign_stats'),
    path('admin-campaigns/', views.admin_campaign_list, name='admin_campaign_list'),
    path('admin-campaign/<int:campaign_id>/', views.admin_campaign_detail, name='admin_campaign_detail'),
    
    # Birthday Campaign URLs
    path('birthday-campaign/create/', views.create_birthday_campaign, name='create_birthday_campaign'),
    path('birthday-campaign/list/', views.list_active_birthday_campaigns, name='list_active_birthday_campaigns'),
    path('birthday-campaign/<int:campaign_id>/', views.get_birthday_campaign, name='get_birthday_campaign'),
    path('birthday-campaign/<int:campaign_id>/donate/', views.donate_to_birthday_campaign, name='donate_to_birthday_campaign'),
    path('verify-birthday-donation/', views.verify_birthday_donation, name='verify_birthday_donation'),
    
    # Admin Birthday Campaign URLs
    path('admin-birthday-campaign-stats/', views.admin_birthday_campaign_stats, name='admin_birthday_campaign_stats'),
    path('admin-birthday-campaigns/', views.admin_birthday_campaign_list, name='admin_birthday_campaign_list'),
    
    # Donation Record URLs
    path('donation-record/create/', views.create_donation_record, name='create_donation_record'),
]
