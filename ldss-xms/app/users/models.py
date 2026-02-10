import re

from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from rest_framework import exceptions
from rest_framework.permissions import DjangoModelPermissions


class UserProfileManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates a new user profilen
        """

        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Creates and saves a new superuser with given details
        """

        user = self.create_user(email, password, **extra_fields)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """
    Model for a user
    """

    # fields
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    # flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # managers
    objects = UserProfileManager()

    # override
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def __str__(self):
        """
        Returns the email.
        """
        return self.email

    def save(self, *args, **kwargs):
        """
        Overrides the save method to hash the password.
        """
        super(UserProfile, self).save(*args, **kwargs)


class PermissionsChecker(DjangoModelPermissions):
    """
    Class to define the method for checking permissions for the XDS API
    """
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        # if current request is in OPEN_ENDPOINTS doesn't check permissions,
        # returns true
        open_endpoints_regex = '(?:% s)' % '|'.join(
            getattr(settings, 'OPEN_ENDPOINTS', []))
        if re.fullmatch(open_endpoints_regex, request.path_info):
            return True

        # checks if there is a logged in user
        if not request.user or (
                not request.user.is_authenticated and
                self.authenticated_users_only):
            return False

        try:
            # tries to get app and model names from view
            model_meta = self._queryset(view).model._meta

        except Exception:
            # if unable, generates app and model names
            def model_meta():
                return None

            model_meta.app_label = view.__module__.split('.')[0]
            model_meta.model_name = \
                view.get_view_name().lower().replace(' ', '')

        # determines permission required to access this endpoint
        perms = self.get_required_permissions(request.method, model_meta)

        # checks if the user has the required permission
        return request.user.has_perms(perms)

    def get_required_permissions(self, method, model_meta):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        kwargs = {
            'app_label': model_meta.app_label,
            'model_name': model_meta.model_name
        }

        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm % kwargs for perm in self.perms_map[method]]
