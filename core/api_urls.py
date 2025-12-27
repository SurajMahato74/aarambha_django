from django.urls import path
from . import api_views

urlpatterns = [
    # Hero Section endpoints
    path('list/', api_views.hero_section_list, name='hero_section_list'),
    path('detail/<int:pk>/', api_views.hero_section_detail, name='hero_section_detail'),
    path('create/', api_views.hero_section_create, name='hero_section_create'),
    path('update/<int:pk>/', api_views.hero_section_update, name='hero_section_update'),
    path('delete/<int:pk>/', api_views.hero_section_delete, name='hero_section_delete'),
    path('toggle-active/<int:pk>/', api_views.hero_section_toggle_active, name='hero_section_toggle_active'),
    
    # Support Card endpoints
    path('support-cards/', api_views.support_card_list, name='support_card_list'),
    path('support-cards/admin/', api_views.support_card_list_admin, name='support_card_list_admin'),
    path('support-cards/detail/<int:pk>/', api_views.support_card_detail, name='support_card_detail'),
    path('support-cards/create/', api_views.support_card_create, name='support_card_create'),
    path('support-cards/update/<int:pk>/', api_views.support_card_update, name='support_card_update'),
    path('support-cards/delete/<int:pk>/', api_views.support_card_delete, name='support_card_delete'),
    path('support-cards/toggle-active/<int:pk>/', api_views.support_card_toggle_active, name='support_card_toggle_active'),

    # Who We Are endpoints
    path('who-we-are/active/', api_views.who_we_are_active, name='who_we_are_active'),
    path('who-we-are/admin/', api_views.who_we_are_list_admin, name='who_we_are_list_admin'),
    path('who-we-are/detail/<int:pk>/', api_views.who_we_are_detail, name='who_we_are_detail'),
    path('who-we-are/create/', api_views.who_we_are_create, name='who_we_are_create'),
    path('who-we-are/update/<int:pk>/', api_views.who_we_are_update, name='who_we_are_update'),
    path('who-we-are/delete/<int:pk>/', api_views.who_we_are_delete, name='who_we_are_delete'),
    path('who-we-are/toggle-active/<int:pk>/', api_views.who_we_are_toggle_active, name='who_we_are_toggle_active'),

    # Growing Our Impact endpoints
    path('growing-impact/active/', api_views.growing_impact_active, name='growing_impact_active'),
    path('growing-impact/admin/', api_views.growing_impact_list_admin, name='growing_impact_list_admin'),
    path('growing-impact/detail/<int:pk>/', api_views.growing_impact_detail, name='growing_impact_detail'),
    path('growing-impact/create/', api_views.growing_impact_create, name='growing_impact_create'),
    path('growing-impact/update/<int:pk>/', api_views.growing_impact_update, name='growing_impact_update'),
    path('growing-impact/delete/<int:pk>/', api_views.growing_impact_delete, name='growing_impact_delete'),
    path('growing-impact/toggle-active/<int:pk>/', api_views.growing_impact_toggle_active, name='growing_impact_toggle_active'),

    # Statistics endpoints
    path('statistics/active/', api_views.statistics_active, name='statistics_active'),
    path('statistics/admin/', api_views.statistics_list_admin, name='statistics_list_admin'),
    path('statistics/detail/<int:pk>/', api_views.statistics_detail, name='statistics_detail'),
    path('statistics/create/', api_views.statistics_create, name='statistics_create'),
    path('statistics/update/<int:pk>/', api_views.statistics_update, name='statistics_update'),
    path('statistics/delete/<int:pk>/', api_views.statistics_delete, name='statistics_delete'),
    path('statistics/toggle-active/<int:pk>/', api_views.statistics_toggle_active, name='statistics_toggle_active'),

    # Event endpoints
    path('events/', api_views.event_list, name='event_list'),
    path('events/admin/', api_views.event_list_admin, name='event_list_admin'),
    path('events/detail/<int:pk>/', api_views.event_detail, name='event_detail'),
    path('events/create/', api_views.event_create, name='event_create'),
    path('events/update/<int:pk>/', api_views.event_update, name='event_update'),
    path('events/delete/<int:pk>/', api_views.event_delete, name='event_delete'),
    path('events/toggle-active/<int:pk>/', api_views.event_toggle_active, name='event_toggle_active'),

    # Partner endpoints
    path('partners/', api_views.partner_list, name='partner_list'),
    path('partners/admin/', api_views.partner_list_admin, name='partner_list_admin'),
    path('partners/detail/<int:pk>/', api_views.partner_detail, name='partner_detail'),
    path('partners/create/', api_views.partner_create, name='partner_create'),
    path('partners/update/<int:pk>/', api_views.partner_update, name='partner_update'),
    path('partners/delete/<int:pk>/', api_views.partner_delete, name='partner_delete'),
    path('partners/toggle-active/<int:pk>/', api_views.partner_toggle_active, name='partner_toggle_active'),

    # Contact Info endpoints
    path('contact/active/', api_views.contact_info_active, name='contact_info_active'),
    path('contact/admin/', api_views.contact_info_list_admin, name='contact_info_list_admin'),
    path('contact/create/', api_views.contact_info_create, name='contact_info_create'),
    path('contact/update/<int:pk>/', api_views.contact_info_update, name='contact_info_update'),
    path('contact/delete/<int:pk>/', api_views.contact_info_delete, name='contact_info_delete'),
    path('contact/toggle-active/<int:pk>/', api_views.contact_info_toggle_active, name='contact_info_toggle_active'),

    # Award endpoints
    path('awards/', api_views.award_list, name='award_list'),
    path('awards/admin/', api_views.award_list_admin, name='award_list_admin'),
    path('awards/detail/<int:pk>/', api_views.award_detail, name='award_detail'),
    path('awards/create/', api_views.award_create, name='award_create'),
    path('awards/update/<int:pk>/', api_views.award_update, name='award_update'),
    path('awards/delete/<int:pk>/', api_views.award_delete, name='award_delete'),
    path('awards/toggle-active/<int:pk>/', api_views.award_toggle_active, name='award_toggle_active'),

    # Our Work endpoints
    path('our-work/', api_views.our_work_list, name='our_work_list'),
    path('our-work/admin/', api_views.our_work_list_admin, name='our_work_list_admin'),
    path('our-work/detail/<str:navlink>/', api_views.our_work_detail, name='our_work_detail'),
    path('our-work/admin/detail/<int:pk>/', api_views.our_work_detail_admin, name='our_work_detail_admin'),
    path('our-work/create/', api_views.our_work_create, name='our_work_create'),
    path('our-work/update/<int:pk>/', api_views.our_work_update, name='our_work_update'),
    path('our-work/delete/<int:pk>/', api_views.our_work_delete, name='our_work_delete'),
    path('our-work/toggle-active/<int:pk>/', api_views.our_work_toggle_active, name='our_work_toggle_active'),

    # School Dropout Report endpoints
    path('reports/school-dropout/', api_views.school_dropout_report_create, name='school_dropout_report_create'),
    path('reports/school-dropout/admin/', api_views.school_dropout_report_list_admin, name='school_dropout_report_list_admin'),
    path('reports/school-dropout/admin/<int:pk>/', api_views.school_dropout_report_detail_admin, name='school_dropout_report_detail_admin'),
    path('reports/school-dropout/admin/<int:pk>/update-status/', api_views.school_dropout_report_update_status, name='school_dropout_report_update_status'),

    # Donation / Khalti Payment endpoints
    path('donations/initiate/', api_views.donation_initiate_payment, name='donation_initiate_payment'),
    path('donations/verify/', api_views.donation_verify_payment, name='donation_verify_payment'),
    path('donations/admin/', api_views.donation_list_admin, name='donation_list_admin'),
]
