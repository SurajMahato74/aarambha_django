from rest_framework import serializers
from .models import Application
import json

class ApplicationSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ['user', 'status', 'applied_at', 'branch', 'created_user']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Ensure skills is always a list
        if isinstance(data.get('skills'), str):
            try:
                data['skills'] = json.loads(data['skills'])
            except:
                data['skills'] = []
        return data
