from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class CustomUser(AbstractUser):
    """Custom User model for user profiles"""
    EMAIL_FIELD = 'username'
    REQUIRED_FIELDS = []
    username = models.EmailField(
        verbose_name='email address', 
        unique=True,
        error_messages={
            'unique': "A user with that username already exists.",
        },
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
    )
