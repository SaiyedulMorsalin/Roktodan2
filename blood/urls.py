from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(
    "blood_requests", views.BloodRequestViewSet, basename="blood_requests-list"
)
router.register("donations", views.DonationViewSet, basename="donations-list")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "blood_requests/accept/<int:request_id>/",
        views.AcceptRequestAPIView.as_view(),
        name="accept_request",
    ),
]
