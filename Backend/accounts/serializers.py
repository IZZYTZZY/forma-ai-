from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    # Accept frontend field names
    phone = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, min_length=8)
    confirmPassword = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'name',
            'phone',
            'password',
            'confirmPassword',
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['confirmPassword']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        # Map frontend field -> model field
        phone = validated_data.pop('phone', None)
        validated_data.pop('confirmPassword')
        password = validated_data.pop('password')

        user = User(**validated_data)

        if phone:
            user.phone_number = phone

        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'phone_number', 'date_joined')
        read_only_fields = ('id', 'date_joined')
