import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken



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
    

class OtpVerifySerializer(serializers.Serializer):
        code = serializers.IntegerField(required=True)


def check_email_or_phone(value):
    if '@' in value:
        try:
            get_user_model().objects.get(email=value)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")
    else: 
        try:
            get_user_model().objects.get(phone_number=value)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError("Invalid phone number or password.")


class LoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(validators=[check_email_or_phone])
    password = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token' : ('Toekn is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')
