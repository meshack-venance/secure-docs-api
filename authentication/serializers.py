from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
        )
        read_only_fields = ("id",)

    def create(self, validated_data):
        password = validated_data.pop("password")
        # Always go through create_user so Django hashes the password correctly.
        return User.objects.create_user(password=password, **validated_data)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
