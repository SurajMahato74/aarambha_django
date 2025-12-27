from django.contrib import admin
from .models import HeroSection, WhoWeAre, GrowingOurImpact, Statistics, OurWork, SchoolDropoutReport, Donation
from ckeditor.widgets import CKEditorWidget
from ckeditor.fields import RichTextField

@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'has_image', 'has_video', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'subtitle']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle', 'is_active')
        }),
        ('Media', {
            'fields': ('background_image', 'background_video'),
            'description': 'Upload background image or video. Video takes precedence if both are provided.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_image(self, obj):
        return bool(obj.background_image)
    has_image.boolean = True
    has_image.short_description = 'Image'

    def has_video(self, obj):
        return bool(obj.background_video)
    has_video.boolean = True
    has_video.short_description = 'Video'

    def has_add_permission(self, request):
        # Allow adding only if no active hero section exists
        if HeroSection.objects.filter(is_active=True).exists():
            return False
        return super().has_add_permission(request)


@admin.register(WhoWeAre)
class WhoWeAreAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active', 'has_image', 'updated_at']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Content', {
            'fields': ('image', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Image'

    def has_add_permission(self, request):
        # Allow adding only if no active Who We Are section exists
        if WhoWeAre.objects.filter(is_active=True).exists():
            return False
        return super().has_add_permission(request)


@admin.register(GrowingOurImpact)
class GrowingOurImpactAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'has_image', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Content', {
            'fields': ('title', 'image', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Image'

    def has_add_permission(self, request):
        # Allow adding only if no active Growing Our Impact section exists
        if GrowingOurImpact.objects.filter(is_active=True).exists():
            return False
        return super().has_add_permission(request)


@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    list_display = ['dropouts_enrolled', 'schools_supported', 'projects', 'districts', 'is_active', 'updated_at']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Statistics', {
            'fields': ('dropouts_enrolled', 'schools_supported', 'projects', 'districts', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Allow adding only if no active Statistics section exists
        if Statistics.objects.filter(is_active=True).exists():
            return False
        return super().has_add_permission(request)


@admin.register(OurWork)
class OurWorkAdmin(admin.ModelAdmin):
    list_display = ['navlink', 'title', 'is_active', 'has_image', 'order', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['navlink', 'title']
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {'navlink': ('title',)}
    formfield_overrides = {
        RichTextField: {'widget': CKEditorWidget(config_name='default')},
    }

    fieldsets = (
        ('Content', {
            'fields': ('navlink', 'title', 'description', 'is_active')
        }),
        ('Media', {
            'fields': ('main_image',),
        }),
        ('Links', {
            'fields': ('external_link', 'order'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_image(self, obj):
        return bool(obj.main_image)
    has_image.boolean = True
    has_image.short_description = 'Image'


@admin.register(SchoolDropoutReport)
class SchoolDropoutReportAdmin(admin.ModelAdmin):
    list_display = ['dropout_name', 'school_name', 'district', 'reporter_name', 'status', 'is_anonymous', 'created_at']
    list_filter = ['status', 'district', 'dropout_gender', 'is_anonymous', 'created_at']
    search_fields = ['dropout_name', 'school_name', 'reporter_name', 'reporter_email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Reporter Information', {
            'fields': ('reporter_name', 'reporter_email', 'reporter_phone', 'is_anonymous')
        }),
        ('Dropout Information', {
            'fields': ('dropout_name', 'dropout_age', 'dropout_gender', 'school_name', 'school_location', 'district')
        }),
        ('Report Details', {
            'fields': ('reason_for_dropout', 'additional_notes', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['purchase_order_id', 'full_name', 'amount', 'payment_status', 'created_at', 'completed_at']
    list_filter = ['payment_status', 'refunded', 'created_at', 'completed_at']
    search_fields = ['full_name', 'email', 'purchase_order_id', 'transaction_id', 'pidx']
    readonly_fields = ['purchase_order_id', 'pidx', 'transaction_id', 'payment_url', 'created_at', 'updated_at', 'completed_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Donor Information', {
            'fields': ('title', 'full_name', 'email', 'phone')
        }),
        ('Donation Details', {
            'fields': ('amount', 'payment_status', 'refunded')
        }),
        ('Khalti Payment Information', {
            'fields': ('purchase_order_id', 'pidx', 'transaction_id', 'payment_url', 'fee'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Disable manual creation of donations (should be created via API)
        return False
