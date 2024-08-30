from django.db import models
from django.contrib.auth.models import User


class BloodRequest(models.Model):
    requester = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="requests"
    )
    blood_group = models.CharField(max_length=4)
    request_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("fulfilled", "Fulfilled"),
            ("canceled", "Canceled"),
        ],
    )
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Request by {self.requester.username} for {self.blood_group} on {self.request_date}"


class Donation(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="donations")
    blood_group = models.CharField(max_length=4)
    donation_date = models.DateField()
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Donation by {self.donor.username} of {self.blood_group} on {self.donation_date}"
