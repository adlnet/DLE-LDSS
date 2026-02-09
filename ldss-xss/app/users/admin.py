from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin form for the Custom User model"""
    verbose_name = 'User'
    verbose_name_plural = 'Users'
