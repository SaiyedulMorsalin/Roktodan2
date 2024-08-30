# serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import DonorProfile, UserProfile
from .constants import BLOOD_GROUP, GENDER_TYPE


# Serializer for the User model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(many=False)
    gender = serializers.ChoiceField(choices=GENDER_TYPE)

    class Meta:
        model = UserProfile
        fields = ["user", "mobile_number", "gender", "blood_group"]


# Serializer for user registration, including validation for password confirmation
class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    mobile_number = serializers.CharField(max_length=12, required=True)
    blood_group = serializers.ChoiceField(choices=BLOOD_GROUP, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "mobile_number",
            "blood_group",
            "password",
            "confirm_password",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, data):
        """Ensure passwords match and email is unique."""
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords don't match."})

        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"email": "Email already exists."})

        return data

    def create(self, validated_data):
        """Create a new user with the validated data."""
        validated_data.pop(
            "confirm_password"
        )  # Remove confirm_password field as it's not part of the User model

        # Extract fields for user creation
        username = validated_data["username"]
        first_name = validated_data["first_name"]
        last_name = validated_data["last_name"]
        email = validated_data["email"]
        mobile_number = validated_data["mobile_number"]
        blood_group = validated_data["blood_group"]
        password = validated_data["password"]

        # Create and save the user
        user = User(
            username=username, first_name=first_name, last_name=last_name, email=email
        )
        user.set_password(password)
        user.is_active = False  # Account is inactive until email verification
        user.save()

        # You can handle custom fields like mobile_number and blood_group as needed
        # Save them in a related model if not using User directly.

        return user


# Serializer for user login
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


# Serializer for DonorProfile, including nested fields for user details
class DonorProfileSerializer(serializers.ModelSerializer):
    # Nested fields to display user information
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = DonorProfile
        fields = [
            "id",
            "username",
            "email",
            "blood_group",
            "district",
            "date_of_donation",
            "donor_type",
            "is_available",
        ]

    def create(self, validated_data):
        """
        Creates a DonorProfile instance with the associated user.
        """
        # Extract the user from the request context
        user = (
            self.context["request"].user
            if self.context["request"].user.is_authenticated
            else None
        )
        # Ensure the user is provided when creating the profile
        if not user:
            raise serializers.ValidationError({"user": "User must be authenticated"})

        # Create the DonorProfile instance with the validated data
        donor_profile = DonorProfile.objects.create(user=user, **validated_data)
        return donor_profile

    def update(self, instance, validated_data):
        """
        Updates the DonorProfile fields.
        """
        # Update each field in the instance with the provided validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
