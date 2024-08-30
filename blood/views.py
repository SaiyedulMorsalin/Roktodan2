from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import BloodRequest, Donation
from .serializers import BloodRequestSerializer, DonationSerializer
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404


class BloodRequestViewSet(viewsets.ModelViewSet):
    queryset = BloodRequest.objects.all()
    serializer_class = BloodRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated]


class AcceptRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        blood_request = get_object_or_404(BloodRequest, id=request_id, status="pending")
        if blood_request.requester == request.user:
            return Response(
                {"error": "You cannot accept your own request."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create a new donation record
        Donation.objects.create(
            donor=request.user,
            blood_group=blood_request.blood_group,
            donation_date=request.data.get("donation_date"),
            details=request.data.get("details"),
        )

        # Update the request status
        blood_request.status = "fulfilled"
        blood_request.save()

        return Response(
            {"message": "Request accepted and donation recorded"},
            status=status.HTTP_200_OK,
        )
