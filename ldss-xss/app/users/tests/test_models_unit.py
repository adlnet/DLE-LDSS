from django.test import tag

from users.models import CustomUser

from .test_setup import TestSetUp


@tag('unit')
class CustomUserTests(TestSetUp):
    def test_create_superuser(self):
        """
        Test to make sure superusers are correctly created
        """
        username = "testSuperUser@test.com"
        password = "pass123"
        f_name = "Super"
        l_name = "User"
        su_custom_user = CustomUser.objects.create_superuser(
            username, password=password, first_name=f_name, last_name=l_name)

        self.assertEqual(su_custom_user.username, username)
        self.assertEqual(su_custom_user.first_name, f_name)
        self.assertEqual(su_custom_user.last_name, l_name)
        self.assertTrue(su_custom_user.is_staff)
        self.assertTrue(su_custom_user.is_active)
        self.assertTrue(su_custom_user.is_superuser)

    def test_create_user(self):
        """
        Test to make sure users are correctly created
        """
        username = "testUser@test.com"
        password = "pass123"
        f_name = "Basic"
        l_name = "User"
        custom_user = CustomUser.objects.create_user(
            username, password=password, first_name=f_name, last_name=l_name)

        self.assertEqual(custom_user.username, username)
        self.assertEqual(custom_user.first_name, f_name)
        self.assertEqual(custom_user.last_name, l_name)
        self.assertFalse(custom_user.is_staff)
        self.assertTrue(custom_user.is_active)
        self.assertFalse(custom_user.is_superuser)
