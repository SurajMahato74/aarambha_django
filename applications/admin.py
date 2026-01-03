from django.contrib import admin
from .models import Application, ChildSponsorship, Child

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'get_age', 'gender', 'district', 'status', 'current_sponsor', 'created_at']
    list_filter = ['status', 'gender', 'district', 'grade_level']
    search_fields = ['full_name', 'father_name', 'mother_name', 'school_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('full_name', 'date_of_birth', 'gender', 'photo')
        }),
        ('Location', {
            'fields': ('country', 'district', 'village', 'address')
        }),
        ('Family Information', {
            'fields': ('father_name', 'mother_name', 'guardian_name', 'guardian_relationship', 'family_situation')
        }),
        ('Education', {
            'fields': ('school_name', 'grade_level', 'educational_needs')
        }),
        ('Health & Personal', {
            'fields': ('health_status', 'special_needs', 'interests_hobbies', 'personality_description')
        }),
        ('Sponsorship', {
            'fields': ('monthly_sponsorship_amount', 'sponsorship_start_date', 'current_sponsor', 'status')
        }),
        ('Admin', {
            'fields': ('admin_notes', 'created_at', 'updated_at')
        }),
    )

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'application_type', 'status', 'payment_completed', 'applied_at']
    list_filter = ['application_type', 'status', 'payment_completed', 'country']
    search_fields = ['full_name', 'user__email', 'phone']
    readonly_fields = ['applied_at', 'updated_at']

@admin.register(ChildSponsorship)
class ChildSponsorshipAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'sponsorship_type', 'status', 'payment_amount', 'created_at']
    list_filter = ['sponsorship_type', 'status', 'country', 'child_gender', 'child_age']
    search_fields = ['full_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'full_name', 'email', 'phone', 'country', 'city', 'address', 'occupation', 'organization')
        }),
        ('Sponsorship Preferences', {
            'fields': ('sponsorship_type', 'child_gender', 'child_age', 'special_requests')
        }),
        ('Communication', {
            'fields': ('update_frequency', 'comm_method', 'message')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_amount', 'payment_frequency', 'tax_deductible')
        }),
        ('Status & Admin', {
            'fields': ('status', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
