from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'branch', 'phone', 'address', 'is_approved', 'membership_paid', 'is_superuser', 'is_active', 'date_joined', 'last_login']
        read_only_fields = ['id', 'is_approved', 'membership_paid', 'is_superuser', 'date_joined', 'last_login']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'user_type', 'branch', 'phone', 'address']
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            user_type=validated_data.get('user_type', 'volunteer'),
            branch=validated_data.get('branch'),
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', '')
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            if user.is_superuser:
                user.user_type = 'superadmin'
            return user
        raise serializers.ValidationError("Invalid credentials")
