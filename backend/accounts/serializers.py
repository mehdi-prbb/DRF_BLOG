from rest_framework import serializers
from django.contrib.auth import get_user_model


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "phone_number",
            "full_name",
            "password",
            "password2"
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        del validated_data['password2']
        return get_user_model().objects.create_user(**validated_data)
    