from django.db import models
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model

User = get_user_model()

class HeroSection(models.Model):
    """
    Model to store hero section content for the index page.
    Only one instance should exist at a time.
    """
    title = models.CharField(max_length=200, default="Welcome to Aarambha Foundation")
    subtitle = models.TextField(blank=True, default="Our Beginning for the Change")
    background_image = models.ImageField(
        upload_to='hero_images/',
        null=True,
        blank=True,
        help_text="Upload hero section background image. If not provided, default image will be used."
    )
    background_video = models.FileField(
        upload_to='hero_videos/',
        null=True,
        blank=True,
        help_text="Upload hero section background video (optional). Video takes precedence over image."
    )
    is_active = models.BooleanField(default=True, help_text="Set to active to display this hero section")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Hero Section"
        verbose_name_plural = "Hero Section"
        ordering = ['-created_at']

    def __str__(self):
        return f"Hero Section - {self.title}"

    def clean(self):
        """Ensure only one active hero section exists"""
        if self.is_active:
            # Check if there's already an active hero section
            existing = HeroSection.objects.filter(is_active=True).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError("Only one hero section can be active at a time. Please deactivate the existing one first.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls):
        """Get the active hero section or None"""
        return cls.objects.filter(is_active=True).first()


class SupportCard(models.Model):
    """
    Model to store support cards for the 'Need your support' section.
    Three cards will be displayed by default.
    """
    title = models.CharField(max_length=200, help_text="Card title")
    description = models.TextField(help_text="Card description (supports HTML)")
    image = models.ImageField(
        upload_to='support_cards/',
        null=True,
        blank=True,
        help_text="Upload card image. If not provided, logo will be used."
    )
    button_text = models.CharField(max_length=50, default="Donate", help_text="Button text")
    button_url = models.CharField(max_length=200, blank=True, help_text="Button URL (leave empty for default donate page)")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    is_active = models.BooleanField(default=True, help_text="Set to active to display this card")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Support Card"
        verbose_name_plural = "Support Cards"
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"Support Card - {self.title}"

    @classmethod
    def get_active_cards(cls):
        """Get all active support cards ordered by order field"""
        return cls.objects.filter(is_active=True).order_by('order')


class WhoWeAre(models.Model):
    """
    Model to store Who We Are section content for the index page.
    Only one instance should exist at a time.
    """
    image = models.ImageField(
        upload_to='who_we_are/',
        null=True,
        blank=True,
        help_text="Upload Who We Are section image. If not provided, default image will be used."
    )
    is_active = models.BooleanField(default=True, help_text="Set to active to display this section")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Who We Are Section"
        verbose_name_plural = "Who We Are Section"
        ordering = ['-created_at']

    def __str__(self):
        return f"Who We Are Section - {self.created_at.date()}"

    def clean(self):
        """Ensure only one active Who We Are section exists"""
        if self.is_active:
            # Check if there's already an active section
            existing = WhoWeAre.objects.filter(is_active=True).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError("Only one Who We Are section can be active at a time. Please deactivate the existing one first.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls):
        """Get the active Who We Are section or None"""
        return cls.objects.filter(is_active=True).first()


class GrowingOurImpact(models.Model):
    """
    Model to store Growing Our Impact section content for the index page.
    Only one instance should exist at a time.
    """
    title = models.CharField(max_length=200, default="Growing Our Impact")
    image = models.ImageField(
        upload_to='growing_impact/',
        null=True,
        blank=True,
        help_text="Upload Growing Our Impact section image. If not provided, default image will be used."
    )
    is_active = models.BooleanField(default=True, help_text="Set to active to display this section")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Growing Our Impact Section"
        verbose_name_plural = "Growing Our Impact Section"
        ordering = ['-created_at']

    def __str__(self):
        return f"Growing Our Impact Section - {self.title}"

    def clean(self):
        """Ensure only one active Growing Our Impact section exists"""
        if self.is_active:
            # Check if there's already an active section
            existing = GrowingOurImpact.objects.filter(is_active=True).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError("Only one Growing Our Impact section can be active at a time. Please deactivate the existing one first.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls):
        """Get the active Growing Our Impact section or None"""
        return cls.objects.filter(is_active=True).first()


class Statistics(models.Model):
    """
    Model to store statistics for the index page.
    Only one instance should exist at a time.
    """
    dropouts_enrolled = models.PositiveIntegerField(default=29, help_text="Number of dropouts enrolled")
    schools_supported = models.PositiveIntegerField(default=19, help_text="Number of schools supported")
    projects = models.PositiveIntegerField(default=8, help_text="Number of projects")
    districts = models.PositiveIntegerField(default=9, help_text="Number of districts")
    is_active = models.BooleanField(default=True, help_text="Set to active to display this statistics section")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Statistics Section"
        verbose_name_plural = "Statistics Section"
        ordering = ['-created_at']

    def __str__(self):
        return f"Statistics - {self.dropouts_enrolled} dropouts, {self.schools_supported} schools"

    def clean(self):
        """Ensure only one active Statistics section exists"""
        if self.is_active:
            # Check if there's already an active section
            existing = Statistics.objects.filter(is_active=True).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError("Only one Statistics section can be active at a time. Please deactivate the existing one first.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls):
        """Get the active Statistics section or None"""
        return cls.objects.filter(is_active=True).first()


class Partner(models.Model):
    """
    Model to store partners for the Partners section.
    """
    name = models.CharField(max_length=200, help_text="Partner name")
    logo = models.ImageField(
        upload_to='partners/',
        help_text="Upload partner logo"
    )
    website_url = models.URLField(blank=True, help_text="Partner website URL (optional)")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    is_active = models.BooleanField(default=True, help_text="Set to active to display this partner")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Partner"
        verbose_name_plural = "Partners"
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"Partner - {self.name}"

    @classmethod
    def get_active_partners(cls):
        """Get all active partners ordered by order field"""
        return cls.objects.filter(is_active=True).order_by('order')


class ContactInfo(models.Model):
    """
    Model to store contact information for the Contact Us page.
    Only one instance should exist at a time.
    """
    address = models.TextField(help_text="Organization address")
    phone = models.CharField(max_length=20, help_text="Phone number")
    email = models.EmailField(help_text="Email address")
    facebook_url = models.URLField(blank=True, help_text="Facebook URL (optional)")
    instagram_url = models.URLField(blank=True, help_text="Instagram URL (optional)")
    linkedin_url = models.URLField(blank=True, help_text="LinkedIn URL (optional)")
    youtube_url = models.URLField(blank=True, help_text="YouTube URL (optional)")
    whatsapp_url = models.URLField(blank=True, help_text="WhatsApp URL (optional)")
    is_active = models.BooleanField(default=True, help_text="Set to active to display this contact info")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information"
        ordering = ['-created_at']

    def __str__(self):
        return f"Contact Info - {self.email}"

    def clean(self):
        """Ensure only one active contact info exists"""
        if self.is_active:
            existing = ContactInfo.objects.filter(is_active=True).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError("Only one contact info can be active at a time. Please deactivate the existing one first.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls):
        """Get the active contact info or None"""
        return cls.objects.filter(is_active=True).first()


class Award(models.Model):
    """
    Model to store awards for the footer section.
    """
    title = models.CharField(max_length=200, help_text="Award title")
    image = models.ImageField(
        upload_to='awards/',
        help_text="Upload award image"
    )
    year = models.PositiveIntegerField(blank=True, null=True, help_text="Award year (optional)")
    description = models.TextField(blank=True, help_text="Award description (optional)")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    is_active = models.BooleanField(default=True, help_text="Set to active to display this award")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Award"
        verbose_name_plural = "Awards"
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"Award - {self.title}"

    @classmethod
    def get_active_awards(cls):
        """Get all active awards ordered by order field"""
        return cls.objects.filter(is_active=True).order_by('order')


class OurWork(models.Model):
    """
    Model to store Our Work sections for the website.
    Each work item has a navlink, title, rich description, images, and links.
    """
    navlink = models.SlugField(unique=True, help_text="Slug for URL and navbar link")
    title = models.CharField(max_length=200, help_text="Title of the work item")
    description = RichTextField(help_text="Rich text description with formatting and images")
    main_image = models.ImageField(
        upload_to='our_work/',
        null=True,
        blank=True,
        help_text="Main image for the work item"
    )
    external_link = models.URLField(blank=True, help_text="Optional external link")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    is_active = models.BooleanField(default=True, help_text="Set to active to display this work item")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Our Work"
        verbose_name_plural = "Our Work"
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"Our Work - {self.title}"

    @classmethod
    def get_active_works(cls):
        """Get all active work items ordered by order field"""
        return cls.objects.filter(is_active=True).order_by('order')


class SchoolDropoutReport(models.Model):
    """
    Model to store school dropout reports submitted by users.
    """
    # Reporter Information
    reporter_name = models.CharField(max_length=200, help_text="Name of the person reporting")
    reporter_email = models.EmailField(help_text="Email of the reporter")
    reporter_phone = models.CharField(max_length=15, blank=True, help_text="Phone number of the reporter")

    # Dropout Information
    dropout_name = models.CharField(max_length=200, help_text="Name of the school dropout")
    dropout_age = models.PositiveIntegerField(help_text="Age of the dropout")
    dropout_gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], help_text="Gender of the dropout")
    school_name = models.CharField(max_length=200, help_text="Name of the school")
    school_location = models.TextField(help_text="Location/address of the school")
    district = models.CharField(max_length=100, help_text="District where the school is located")

    # Report Details
    reason_for_dropout = models.TextField(help_text="Reason for dropping out")
    additional_notes = models.TextField(blank=True, help_text="Any additional information")

    # Meta
    is_anonymous = models.BooleanField(default=False, help_text="Whether the report is anonymous")
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('investigated', 'Investigated'), ('resolved', 'Resolved')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "School Dropout Report"
        verbose_name_plural = "School Dropout Reports"
        ordering = ['-created_at']

    def __str__(self):
        return f"Report for {self.dropout_name} from {self.school_name}"


class Donation(models.Model):
    """
    Model to store donation transactions with Khalti payment integration.
    """
    # Donor Information
    title = models.CharField(max_length=10, choices=[('Mr.', 'Mr.'), ('Mrs.', 'Mrs.'), ('Ms.', 'Ms.')], default='Mr.')
    full_name = models.CharField(max_length=200, help_text="Full name of the donor")
    email = models.EmailField(help_text="Email address of the donor")
    phone = models.CharField(max_length=15, blank=True, help_text="Phone number of the donor (optional)")
    
    # Donation Details
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Donation amount in NPR")
    
    # Khalti Payment Details
    purchase_order_id = models.CharField(max_length=100, unique=True, help_text="Unique purchase order ID")
    pidx = models.CharField(max_length=100, blank=True, null=True, help_text="Khalti payment identifier")
    transaction_id = models.CharField(max_length=100, blank=True, null=True, help_text="Khalti transaction ID")
    
    # Payment Status
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
        ('canceled', 'User Canceled'),
        ('refunded', 'Refunded'),
    ]
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    
    # Metadata
    payment_url = models.URLField(blank=True, null=True, help_text="Khalti payment URL")
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Transaction fee")
    refunded = models.BooleanField(default=False, help_text="Whether the transaction has been refunded")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True, help_text="When the payment was completed")

    class Meta:
        verbose_name = "Donation"
        verbose_name_plural = "Donations"
        ordering = ['-created_at']

    def __str__(self):
        return f"Donation by {self.full_name} - Rs.{self.amount} ({self.payment_status})"

    @property
    def amount_in_paisa(self):
        """Convert amount to paisa (required by Khalti API)"""
        return int(self.amount * 100)


class RecommendationLetter(models.Model):
    """
    Model to store recommendation letter requests from members.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendation_letters')
    purpose = models.CharField(max_length=200, help_text="Purpose of the recommendation letter")
    description = models.TextField(help_text="Detailed description of why the letter is needed")
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Admin fields
    admin_notes = models.TextField(blank=True, help_text="Admin notes (optional)")
    letter_content = models.TextField(blank=True, help_text="Generated letter content")
    signed_letter = models.FileField(
        upload_to='recommendation_letters/',
        blank=True,
        null=True,
        help_text="Upload signed recommendation letter (PDF format preferred)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Recommendation Letter"
        verbose_name_plural = "Recommendation Letters"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Recommendation Letter - {self.user.get_full_name() or self.user.email} ({self.purpose})"


class IndexEvent(models.Model):
    """
    Model to store events displayed on the index page.
    This is separate from the main Event model used for event management.
    """
    title = models.CharField(max_length=300, help_text="Event title")
    description = models.TextField(help_text="Event description")
    image = models.ImageField(
        upload_to='index_events/',
        blank=True,
        null=True,
        help_text="Event image for display on index page"
    )
    location = models.CharField(max_length=200, blank=True, help_text="Event location")
    event_date = models.DateTimeField(blank=True, null=True, help_text="Event date and time")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    is_active = models.BooleanField(default=True, help_text="Set to active to display this event on index page")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Index Page Event"
        verbose_name_plural = "Index Page Events"
        ordering = ['order', '-event_date']
    
    def __str__(self):
        return f"Index Event - {self.title}"
    
    @classmethod
    def get_active_events(cls):
        """Get all active events for index page display"""
        return cls.objects.filter(is_active=True).order_by('order', '-event_date')
