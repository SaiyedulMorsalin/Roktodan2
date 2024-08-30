from rest_framework import serializers
from .models import BloodRequest, Donation


class BloodRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodRequest
        fields = ["id", "requester", "blood_group", "request_date", "status", "details"]


class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ["id", "donor", "blood_group", "donation_date", "details"]
