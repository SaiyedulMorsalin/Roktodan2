from django.db import models
from django.contrib.auth.models import User
from .constants import BLOOD_GROUP, GENDER_TYPE


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_profile"
    )
    mobile_number = models.CharField(max_length=12)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP)
    gender = models.CharField(max_length=10, choices=GENDER_TYPE, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class DonorProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="donor_profile"
    )
    blood_group = models.CharField(max_length=4, choices=BLOOD_GROUP)
    district = models.CharField(max_length=100)
    date_of_donation = models.DateField(null=True, blank=True)  # Optional field
    donor_type = models.CharField(
        max_length=50
    )  # Example: 'regular', 'emergency', etc.
    is_available = models.BooleanField(default=True)  # Ensure this field is defined

    def __str__(self):
        return f"{self.user.username} - {self.blood_group}"
