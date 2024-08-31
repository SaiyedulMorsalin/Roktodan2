from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

# Create a new router instance
router = DefaultRouter()

# Register viewsets with the router
router.register("users", views.UserViewSet, basename="user")  # For UserViewSet
router.register("donors", views.DonorViewSet, basename="donor")  # For DonorViewSet

urlpatterns = [
    path("register/", views.UserRegistrationApiView.as_view(), name="user_register"),
    path("users/activate/<str:uid64>/<str:token>/", views.activate, name="activate"),
    path("users/login/", views.UserLoginApiView.as_view(), name="login"),
    path("users/logout/", views.UserLogoutView.as_view(), name="logout"),
    path("dashboard/", views.UserDashboardAPIView.as_view(), name="user_dashboard"),
    path(
        "profile/<int:user_id>/",
        views.UserProfileAPIView.as_view(),
        name="user_profile",
    ),
    path("", include(router.urls)),  # Include router URLs
]
