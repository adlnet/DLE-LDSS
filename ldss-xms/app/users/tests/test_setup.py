from rest_framework.test import APITestCase

from users.models import UserProfile


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in XIS"""

    def setUp(self):
        """Function to set up necessary data for testing"""

        self.username = "base@test.com"
        self.password = "1234"

        self.base_user = UserProfile.objects.create_user(
            self.username,
            self.password,
            first_name="base",
            last_name="user")

        self.new_username = "another@test.com"
        self.new_password = "Laskdj30427."
        self.new_fname = "new"
        self.new_lname = "user"

        return super().setUp()

    def tearDown(self):
        return super().tearDown()
