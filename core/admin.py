from django.contrib import admin
from .models import HeroSection, WhoWeAre, GrowingOurImpact, Statistics, OurWork
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