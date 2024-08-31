from rest_framework import serializers
from django.contrib.auth.models import User
from .models import DonorProfile, UserProfile
from .constants import BLOOD_GROUP, GENDER_TYPE


# Serializer for the User model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


# Serializer for the UserProfile model
class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
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
        validated_data.pop("confirm_password")  # Remove confirm_password field

        # Create and save the user
        user = User(
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.is_active = False  # Account is inactive until email verification
        user.save()

        # Save additional fields like mobile_number and blood_group in a related model
        return user


# Serializer for user login
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


# Serializer for DonorProfile, including nested fields for user details
class DonorProfileSerializer(serializers.ModelSerializer):
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
        """Creates a DonorProfile instance with the associated user."""
        user = self.context["request"].user
        if not user or not user.is_authenticated:
            raise serializers.ValidationError({"user": "User must be authenticated."})

        return DonorProfile.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        """Updates the DonorProfile fields."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
