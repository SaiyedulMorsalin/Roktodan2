from django.contrib import admin
from .models import DonorProfile, UserProfile

# Register your models here.
# admin.site.register(UserRegister)
admin.site.register(DonorProfile)
admin.site.register(UserProfile)
