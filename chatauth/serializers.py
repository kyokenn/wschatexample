import re

from django.contrib.auth import authenticate, get_user_model

from rest_framework import serializers

User = get_user_model()


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30, write_only=True)
    password1 = serializers.CharField(max_length=30, write_only=True)
    password2 = serializers.CharField(max_length=30, write_only=True)

    def validate_username(self, value):
        if not re.match(r'^[a-z0-9\.\-_]+$', value):
            raise serializers.ValidationError(
                'Your username may only contain lowercase letters (a-z)')
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Sorry, that username isn't available.")
        return value

    def validate_password2(self, value):
        if self.initial_data['password1'] != value:
            raise serializers.ValidationError(
                'The passwords do not match, try again.')
        return value

    def save(self, **kwargs):
        username = self.initial_data.get('username')
        password = self.initial_data.get('password1')
        return User.objects.create_user(username=username, password=password)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30, write_only=True)
    password = serializers.CharField(max_length=30, write_only=True)

    def save(self, **kwargs):
        username = self.validated_data.get('username')
        password = self.validated_data.get('password')
        return authenticate(username=username, password=password)
