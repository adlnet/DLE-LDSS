from unittest.mock import Mock, patch

from rest_framework.test import APITestCase

from users.models import UserProfile


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in XIS"""

    def setUp(self):
        """Function to set up necessary data for testing"""

        self.su_username = "super@test.com"
        self.su_password = "1234"

        self.super_user = UserProfile.objects.create_superuser(
            self.su_username,
            self.su_password,
            first_name="super",
            last_name="user",
        )

        mock = Mock()
        mock.exists.return_value = True

        self.user_catalogs = patch("users.models.UserProfile.catalogs")
        self.user_catalogs_mock = self.user_catalogs.start()
        self.user_catalogs_mock.filter.return_value = mock

        self.mocked_get_xis_catalogs = patch(
            "api.views.get_xis_catalogs"
        ).start()
        self.mocked_get_xis_catalogs.return_value.json.return_value = [
            "catalog_1",
            "catalog_2",
        ]
        self.mocked_get_xis_catalogs.return_value.status_code = 200

        self.mocked_get_xis_experiences = patch(
            "api.views.get_catalog_experiences"
        ).start()

        self.mocked_get_xis_experiences.return_value.json.return_value = [
            "experience_1",
            "experience_2",
        ]
        self.mocked_get_xis_experiences.return_value.status_code = 200

        self.mocked_get_xis_experience = patch(
            "api.views.get_xis_experience"
        ).start()
        self.mocked_get_xis_experience.return_value.json.return_value = [
            {
                "course": "title",
            }
        ]
        self.mocked_get_xis_experience.return_value.status_code = 200

        self.post_experience_data_dict = {
            "course": "title",
        }
        self.mocked_post_xis_experience = patch(
            "api.views.post_xis_experience"
        ).start()
        self.mocked_post_xis_experience.return_value.json.return_value = [
            {
                "course": "title",
            }
        ]
        self.mocked_post_xis_experience.return_value.status_code = 201

        return super().setUp()

    def tearDown(self):
        return super().tearDown()
