from rest_framework import serializers
from django.contrib.auth import get_user_model
import re


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "phone_number",
            "password",
            "password2"
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        del validated_data['password2']
        return get_user_model().objects.create_user(**validated_data)
    
    def validate_password(self, value):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        match = re.search(pattern, value)

        if not match:
            raise serializers.ValidationError('The password must have at least 8 characters, numbers, upper and lower case letters and symbols (@$!%*?&)')
        return value
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords doesn't match together.")
        return data