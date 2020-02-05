from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError

from accounts.models import User, Rate


# TODO decompose
class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=128, required=True, style={"input_type": "username"})
    password = serializers.CharField(max_length=128, required=True, style={"input_type": "password"})
    email = serializers.EmailField(required=True)

    def validate_password(self, password):
        try:
            validate_password(password)
        except DjangoValidationError as e:
            raise ValidationError(detail=e.messages)
        return password

    def create(self, validated_data):
        try:
            user = User.objects.create_user(
                username=validated_data["username"],
                email=validated_data["email"],
                password=validated_data["password"],
            )
        except IntegrityError:
            raise ValidationError({"username": "User with this username is already exists"})
        return user

    def update(self, instance, validated_data):
        assert False, "Could not use this serializer for update"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "photo",
            "location",
            "is_lector",
            "description",
        )
        read_only_fields = ('username', 'email', 'is_lector')


class CreateRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = (
            "id",
            "visitor",
            "lector",
            "rate",
            "comment",
        )

    def validate(self, attrs):
        if attrs.get("visitor") == attrs.get("lector"):
            raise ValidationError({"lector": "Can't set rate for yourself"})
        return attrs


class ReadUpdateRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = (
            "rate",
            "comment",
        )

    def create(self, validated_data):
        assert False, "Can't create rate"
