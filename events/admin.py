from django.contrib import admin
from .models import Event, EventParticipation, EventCertificate

# Change the app name in admin
admin.site.app_index_template = 'admin/app_index.html'

class EventsAdminConfig:
    verbose_name = "Event Management"

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'venue_type', 'start_datetime', 'contact_person', 'max_participants', 'is_active']
    list_filter = ['event_type', 'venue_type', 'user_type', 'assignment_mode', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'contact_person', 'venue_name']
    filter_horizontal = ['assigned_to']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'event_type', 'is_active')
        }),
        ('Date & Time', {
            'fields': ('start_datetime', 'end_datetime')
        }),
        ('Venue Information', {
            'fields': ('venue_type', 'venue_name', 'venue_address')
        }),
        ('Online Meeting Details', {
            'fields': ('meeting_link', 'meeting_id', 'meeting_password'),
            'description': 'Fill these fields if venue type is Online or Hybrid'
        }),
        ('Contact Person', {
            'fields': ('contact_person', 'contact_phone', 'contact_email'),
            'description': 'Contact person for this event'
        }),
        ('Participant Management', {
            'fields': ('requires_application', 'max_participants'),
            'description': 'Set participation limits and requirements'
        }),
        ('User Assignment', {
            'fields': ('user_type', 'assignment_mode', 'assigned_to', 'branch'),
            'description': 'Define who can participate in this event'
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(EventParticipation)
class EventParticipationAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'status', 'attended', 'applied_at']
    list_filter = ['status', 'attended', 'applied_at', 'event__event_type']
    search_fields = ['event__title', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['applied_at', 'updated_at']
    
    fieldsets = (
        ('Event & User', {
            'fields': ('event', 'user')
        }),
        ('Application', {
            'fields': ('status', 'application_message')
        }),
        ('Admin Notes', {
            'fields': ('admin_notes',)
        }),
        ('Attendance', {
            'fields': ('attended', 'attendance_marked_by', 'attendance_marked_at')
        }),
        ('Timestamps', {
            'fields': ('applied_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(EventCertificate)
class EventCertificateAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'issued_by', 'issued_at']
    list_filter = ['issued_at', 'event__event_type']
    search_fields = ['event__title', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['issued_at']