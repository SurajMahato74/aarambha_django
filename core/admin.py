from django.contrib import admin
from .models import (
    HeroSection, WhoWeAre, GrowingOurImpact, Statistics, SupportCard, Partner, 
    ContactInfo, Award, OurWork, SchoolDropoutReport, Donation, RecommendationLetter,
    IndexEvent, BlogPost, BlogParagraph, BlogCategory
)
from ckeditor.widgets import CKEditorWidget
from ckeditor.fields import RichTextField
from django import forms

@admin.register(SupportCard)
class SupportCardAdmin(admin.ModelAdmin):
    list_display = ['title', 'button_text', 'order', 'is_active']
    list_filter = ['is_active']
    ordering = ['order']

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active']
    list_filter = ['is_active']
    ordering = ['order']

@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ['email', 'phone', 'is_active']
    list_filter = ['is_active']

@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ['title', 'year', 'order', 'is_active']
    list_filter = ['is_active', 'year']
    ordering = ['order']

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


@admin.register(RecommendationLetter)
class RecommendationLetterAdmin(admin.ModelAdmin):
    list_display = ['user', 'purpose', 'status', 'created_at', 'has_signed_letter']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'purpose']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'purpose', 'description')
        }),
        ('Admin Action', {
            'fields': ('status', 'admin_notes', 'signed_letter')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'approved_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_signed_letter(self, obj):
        return bool(obj.signed_letter)
    has_signed_letter.boolean = True
    has_signed_letter.short_description = 'Letter Uploaded'


@admin.register(IndexEvent)
class IndexEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'event_date', 'order', 'is_active']
    list_filter = ['is_active', 'event_date']
    search_fields = ['title', 'location']
    ordering = ['order', '-event_date']


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']


class BlogParagraphInline(admin.StackedInline):
    model = BlogParagraph
    extra = 0
    fields = ['order', 'paragraph_type', 'content', 'image', 'image_caption', 'image_alt_text', 'quote_text', 'quote_author']
    formfield_overrides = {
        RichTextField: {'widget': CKEditorWidget(config_name='default')},
    }
    
    def get_extra(self, request, obj=None, **kwargs):
        # Return 3 extra forms for new blog posts, 0 for existing ones
        if obj is None:
            return 3
        return 0


class BlogPostAdminForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = '__all__'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    form = BlogPostAdminForm
    list_display = ['title', 'author', 'status', 'is_featured', 'paragraph_count_display', 'created_at', 'published_at']
    list_filter = ['status', 'is_featured', 'categories', 'created_at', 'author']
    search_fields = ['title', 'excerpt', 'meta_description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['categories']
    inlines = [BlogParagraphInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'excerpt', 'featured_image')
        }),
        ('Categorization', {
            'fields': ('categories',)
        }),
        ('SEO & Meta', {
            'fields': ('meta_description',),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('status', 'is_featured', 'published_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def paragraph_count_display(self, obj):
        return obj.paragraphs.count()
    paragraph_count_display.short_description = 'Paragraphs'
    
    def save_model(self, request, obj, form, change):
        # Set author to current user if not set
        if not obj.author_id:
            obj.author = request.user
        
        # Set published_at when status changes to published
        if obj.status == 'published' and not obj.published_at:
            from django.utils import timezone
            obj.published_at = timezone.now()
        
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('categories', 'paragraphs')


@admin.register(BlogParagraph)
class BlogParagraphAdmin(admin.ModelAdmin):
    list_display = ['blog_post', 'order', 'paragraph_type', 'content_preview', 'has_image']
    list_filter = ['paragraph_type', 'blog_post__status']
    search_fields = ['blog_post__title', 'content', 'quote_text']
    ordering = ['blog_post', 'order']
    formfield_overrides = {
        RichTextField: {'widget': CKEditorWidget(config_name='default')},
    }
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('blog_post', 'order', 'paragraph_type')
        }),
        ('Text Content', {
            'fields': ('content',),
            'classes': ('collapse',)
        }),
        ('Image Content', {
            'fields': ('image', 'image_caption', 'image_alt_text'),
            'classes': ('collapse',)
        }),
        ('Quote Content', {
            'fields': ('quote_text', 'quote_author'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        if obj.paragraph_type == 'text' and obj.content:
            from django.utils.html import strip_tags
            return strip_tags(obj.content)[:100] + '...' if len(strip_tags(obj.content)) > 100 else strip_tags(obj.content)
        elif obj.paragraph_type == 'quote' and obj.quote_text:
            return f'Quote: {obj.quote_text[:50]}...' if len(obj.quote_text) > 50 else f'Quote: {obj.quote_text}'
        elif obj.paragraph_type == 'image' and obj.image_caption:
            return f'Image: {obj.image_caption}'
        return 'No content'
    content_preview.short_description = 'Content Preview'
    
    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Has Image'
