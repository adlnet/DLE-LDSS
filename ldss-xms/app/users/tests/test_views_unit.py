from django.test import tag
from django.urls import reverse
from rest_framework import status

from users.models import UserProfile

from .test_setup import TestSetUp


@tag('unit')
class UserTests(TestSetUp):

    def test_correct_validate(self):
        """Test that the validate endpoint verifies an active session"""
        url_validate = reverse('users:validate')

        validate_json = b'{"message":"valid"}'

        self.client.login(username=self.username, password=self.password)

        validate_response = self.client.get(url_validate)

        self.assertEqual(validate_response.status_code, status.HTTP_200_OK)
        self.assertEqual(validate_response.content, validate_json)

    def test_no_session_validate(self):
        """Test that the validate endpoint errors when no active session"""
        url_validate = reverse('users:validate')

        validate_response = self.client.get(url_validate)

        self.assertEqual(validate_response.status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_correct_login(self):
        """Test that the login endpoint creates a session and logs in"""
        url = reverse('users:login')
        url_validate = reverse('users:validate')

        validate_json = b'{"message":"valid"}'

        response = self.client.post(
            url, {'username': self.username, 'password': self.password},
            format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        validate_response = self.client.get(url_validate)

        self.assertEqual(validate_response.status_code, status.HTTP_200_OK)
        self.assertEqual(validate_response.content, validate_json)

    def test_no_login(self):
        """Test that the login endpoint errors with no credentials"""
        url = reverse('users:login')

        response = self.client.post(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bad_login(self):
        """Test that the login endpoint errors with incorrect credentials"""
        url = reverse('users:login')

        response = self.client.post(
            url, {'username': self.username, 'password': "wrongPass"},
            format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_correct_logout(self):
        """Test that the logout endpoint ends a session and logs out"""
        url = reverse('users:logout')
        url_validate = reverse('users:validate')

        self.client.login(username=self.username, password=self.password)

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        validate_response = self.client.get(url_validate)

        self.assertEqual(validate_response.status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_correct_register(self):
        """
        Test that the register endpoint creates a user and starts a session
        """
        url = reverse('users:register')
        url_validate = reverse('users:validate')

        validate_json = b'{"message":"valid"}'

        response = self.client.post(
            url, {'email': self.new_username, 'password': self.new_password,
                  'first_name': self.new_fname, 'last_name': self.new_lname},
            format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        validate_response = self.client.get(url_validate)

        self.assertEqual(validate_response.status_code, status.HTTP_200_OK)
        self.assertEqual(validate_response.content, validate_json)
        self.assertIsNotNone(UserProfile.objects.get(email=self.new_username))

    def test_repeated_register(self):
        """Test that the register endpoint errors when reusing a username"""
        url = reverse('users:register')

        response = self.client.post(
            url, {'email': self.username, 'password': self.new_password,
                  'first_name': self.new_fname, 'last_name': self.new_lname},
            format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_email_register(self):
        """Test that the register endpoint errors when missing an email"""
        url = reverse('users:register')

        response = self.client.post(
            url, {'password': self.new_password, 'first_name': self.new_fname,
                  'last_name': self.new_lname}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_password_register(self):
        """Test that the register endpoint errors when missing a password"""
        url = reverse('users:register')

        response = self.client.post(
            url, {'email': self.new_username, 'first_name': self.new_fname,
                  'last_name': self.new_lname}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_first_name_register(self):
        """Test that the register endpoint errors when missing a first name"""
        url = reverse('users:register')

        response = self.client.post(
            url, {'email': self.new_username, 'password': self.new_password,
                  'last_name': self.new_lname}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_last_name_register(self):
        """Test that the register endpoint errors when missing a last name"""
        url = reverse('users:register')

        response = self.client.post(
            url, {'email': self.new_username, 'password': self.new_password,
                  'first_name': self.new_fname}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
