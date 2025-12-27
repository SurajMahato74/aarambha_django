
from rest_framework import serializers
from .models import HeroSection, SupportCard, WhoWeAre, GrowingOurImpact, Statistics, Event, Partner, ContactInfo, Award, OurWork, SchoolDropoutReport

class HeroSectionSerializer(serializers.ModelSerializer):
    background_image = serializers.ImageField(required=False, allow_null=True)
    background_video = serializers.FileField(required=False, allow_null=True)
    
    class Meta:
        model = HeroSection
        fields = ['id', 'title', 'subtitle', 'background_image', 'background_video', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        
        # Convert image and video to full URLs
        if instance.background_image and request:
            representation['background_image'] = request.build_absolute_uri(instance.background_image.url)
        else:
            representation['background_image'] = None
            
        if instance.background_video and request:
            representation['background_video'] = request.build_absolute_uri(instance.background_video.url)
        else:
            representation['background_video'] = None
            
        return representation


class GrowingOurImpactSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = GrowingOurImpact
        fields = ['id', 'title', 'image', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        # Convert image to full URL
        if instance.image and request:
            representation['image'] = request.build_absolute_uri(instance.image.url)
        else:
            representation['image'] = None

        return representation


class StatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistics
        fields = ['id', 'dropouts_enrolled', 'schools_supported', 'projects', 'districts', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SupportCardSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = SupportCard
        fields = ['id', 'title', 'description', 'image', 'button_text', 'button_url', 'order', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        
        # Convert image to full URL
        if instance.image and request:
            representation['image'] = request.build_absolute_uri(instance.image.url)
        else:
            representation['image'] = None

        return representation

class OurWorkSerializer(serializers.ModelSerializer):
    main_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = OurWork
        fields = ['id', 'navlink', 'title', 'description', 'main_image', 'external_link', 'order', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        # Convert image to full URL
        if instance.main_image and request:
            representation['main_image'] = request.build_absolute_uri(instance.main_image.url)
        else:
            representation['main_image'] = None

        return representation


class WhoWeAreSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = WhoWeAre
        fields = ['id', 'image', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        # Convert image to full URL
        if instance.image and request:
            representation['image'] = request.build_absolute_uri(instance.image.url)
        else:
            representation['image'] = None

        return representation


class EventSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'image', 'event_date', 'location', 'order', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        
        if instance.image and request:
            representation['image'] = request.build_absolute_uri(instance.image.url)
        else:
            representation['image'] = None

        return representation

class PartnerSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(required=True)
    
    class Meta:
        model = Partner
        fields = ['id', 'name', 'logo', 'website_url', 'order', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        
        if instance.logo and request:
            representation['logo'] = request.build_absolute_uri(instance.logo.url)
        else:
            representation['logo'] = None

        return representation
class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = ['id', 'address', 'phone', 'email', 'facebook_url', 'instagram_url', 'linkedin_url', 'youtube_url', 'whatsapp_url', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
class AwardSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)

    class Meta:
        model = Award
        fields = ['id', 'title', 'image', 'year', 'description', 'order', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if instance.image and request:
            representation['image'] = request.build_absolute_uri(instance.image.url)
        else:
            representation['image'] = None

        return representation


class SchoolDropoutReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolDropoutReport
        fields = [
            'id', 'reporter_name', 'reporter_email', 'reporter_phone',
            'dropout_name', 'dropout_age', 'dropout_gender', 'school_name',
            'school_location', 'district', 'reason_for_dropout', 'additional_notes',
            'is_anonymous', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']