from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from .models import DonorProfile, UserProfile
from .serializers import (
    RegistrationSerializer,
    UserSerializer,
    UserLoginSerializer,
    DonorProfileSerializer,
    UserProfileSerializer,
)
from .filters import DonorProfileFilter
from blood.models import BloodRequest, Donation
from blood.serializers import BloodRequestSerializer, DonationSerializer
import logging

logger = logging.getLogger(__name__)


# API View for User Dashboard
class UserDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BloodRequestSerializer

    def get(self, request, *args, **kwargs):
        user = request.user

        # Fetch the user's own blood requests
        user_requests = BloodRequest.objects.filter(requester=user)
        user_requests_serializer = BloodRequestSerializer(user_requests, many=True)

        # Fetch the user's own donations
        user_donations = Donation.objects.filter(donor=user)
        user_donations_serializer = DonationSerializer(user_donations, many=True)

        # Fetch all pending blood requests (excluding the user's own requests)
        pending_requests = BloodRequest.objects.exclude(requester=user)
        pending_requests_serializer = BloodRequestSerializer(
            pending_requests, many=True
        )

        # Combine all the data
        data = {
            "my_requests": user_requests_serializer.data,
            "my_donations": user_donations_serializer.data,
            "pending_requests": pending_requests_serializer.data,
        }

        return Response(data)


# Read-only ViewSet for listing users, accessible only to admin users
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, user_id):
        try:
            donor = DonorProfile.objects.get(user_id=user_id)
            serializer = DonorProfileSerializer(donor)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DonorProfile.DoesNotExist:
            return Response(
                {"detail": "Donor profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


# API View for User Profile Management
class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user__id=user_id)
            serializer = UserProfileSerializer(user_profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "UserProfile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API View for User Registration with Email Confirmation
class UserRegistrationApiView(APIView):
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirm_link = request.build_absolute_uri(
                reverse("activate", kwargs={"uid64": uid, "token": token})
            )
            email_subject = "Confirm Your Email"
            email_body = render_to_string(
                "confirm_email.html", {"confirm_link": confirm_link}
            )

            try:
                email = EmailMultiAlternatives(email_subject, "", to=[user.email])
                email.attach_alternative(email_body, "text/html")
                email.send()
                return Response(
                    {"message": "Check your email for confirmation."},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                logger.error(f"Error sending email: {e}")
                return Response(
                    {"error": "Failed to send confirmation email."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Function View to Activate User Account via Email Link
def activate(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect("login")
    else:
        return redirect("user_register")


# API View for User Login with Token Authentication
class UserLoginApiView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]

            user = authenticate(username=username, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                login(request, user)
                return Response(
                    {"token": token.key, "user_id": user.id}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Invalid Credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API View for User Logout
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        request.user.auth_token.delete()
        logout(request)
        return redirect("login")


# ViewSet for Managing Donor Profiles with Filtering and Search Capabilities
class DonorViewSet(viewsets.ModelViewSet):
    queryset = DonorProfile.objects.all()
    serializer_class = DonorProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = DonorProfileFilter
    search_fields = ["blood_group", "district", "date_of_donation", "donor_type"]
