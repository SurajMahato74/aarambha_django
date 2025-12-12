from rest_framework import serializers
from .models import Branch

class BranchSerializer(serializers.ModelSerializer):
    admin_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Branch
        fields = ['id', 'code', 'name', 'location', 'admin', 'admin_name', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_admin_name(self, obj):
        if obj.admin:
            return f"{obj.admin.first_name} {obj.admin.last_name}"
        return None

class BranchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['code', 'name', 'location', 'admin', 'is_active']
