import json
from unittest.mock import Mock, patch
from ddt import ddt
from django.test import tag
from django.urls import reverse
# from rest_framework import status
from api.tests.test_setup import TestSetUp

@tag("unit")
@ddt
class XISViewsTests(TestSetUp):

    def test_xis_get_catalogs_view(self):
        """
        Tests that the catalog api returns a list of catalogs
        """
        # mock the response from the get_xis_catalogs function
        with patch("api.views.get_xis_catalogs") as mocked_get:
            # mocked_get.return_value.json.return_value = json.dumps([
            #     "catalog_1",
            #     "catalog_2",
            # ])
            self.super_user.catalogs = Mock()
            self.user_catalogs_mock.all.return_value = [
                "catalog_1", "catalog_2"]
            mocked_get.return_value.status_code = 400

            self.client.force_login(self.super_user)

            # call the function
            response = self.client.get(reverse("api:catalogs"), follow = True)
            # assert the response
            self.assertEqual(
                json.loads(response.data), ["catalog_1", "catalog_2"],
            )

    def test_xis_get_catalogs_view_error(self):
        """
        Tests the catalog api returns a error when no user
        """
        with patch("api.views.get_xis_catalogs") as mocked_get:
            mocked_get.return_value.status_code = 500

            response = self.client.get(reverse("api:catalogs"), follow=True
            )

            # assert the response
            self.assertTrue(
                response.status_code in [301, 403]
                )
    def test_xis_get_catalog_experiences_view(self):
        """
        Tests that the catalog api returns a list of experiences for a catalog
        """
        self.client.login(username=self.su_username, password=self.su_password)

        # call the function
        response = self.client.get(
            reverse(
                "api:catalog-experiences",
                kwargs={"provider_id": "catalog_1"},
            ), follow = True
        )

        # Check for redirect first
        if response.status_code in [301, 302]:
            self.assertIn('Location', response.headers)
            # Optionally follow the redirect
            redirect_response = self.client.get(response.headers['Location'])
            self.assertEqual(redirect_response.status_code, 200)
            # Handle response after redirect
            # Assuming it returns JSON, you can assert here
            self.assertEqual(
                redirect_response.data,
                {"experiences": ["experience_1", "experience_2"]},
            )
        else:
            # If no redirect, proceed as normal
            self.assertEqual(
                response.data,
                {"experiences": ["experience_1", "experience_2"]},
            )

    def test_xis_get_catalog_experiences_view_error_getting_catalogs(self):
        """
        Tests the catalog api returns a error when the status code returned
        from get xis catalogs is not 200
        """
        self.client.login(username=self.su_username, password=self.su_password)
        self.mocked_get_xis_catalogs.return_value.status_code = 500
        # call the function
        response = self.client.get(
            reverse(
                "api:catalog-experiences",
                kwargs={"provider_id": "catalog_1"}
            ), follow=True
        )
        # assert the response  returns a 500
        self.assertEqual(
            response.data["detail"],
            "There was an error processing your request.",
        )

    def test_xis_get_catalog_experiences_view_error_provider_not_found(self):
        """
        Tests the catalog api returns an error when the provider is not a valid
        provider.
        """
        self.client.login(username=self.su_username, password=self.su_password)
        # call the function
        response = self.client.get(
            reverse(
                "api:catalog-experiences",
                kwargs={"provider_id": "catalog_3"},
            ), follow = True
        )
        # assert the response  returns a 500
        self.assertEqual(
            response.data["detail"],
            "The provider id does not exist in the XIS catalogs",
        )

    def test_xis_get_catalog_experiences_view_error_getting_experiences(self):
        """
        Tests the catalog api returns an error when the status code returned is
        not 200
        """
        self.client.login(username=self.su_username, password=self.su_password)
        self.mocked_get_xis_experiences.return_value.status_code = 500
        # call the function
        response = self.client.get(
            reverse(
                "api:catalog-experiences",
                kwargs={"provider_id": "catalog_2"}
            ), follow=True
        )
        # assert the response  returns a 500
        self.assertEqual(
            response.data["detail"],
            "There was an error processing your request.",
        )

    def test_xis_get_experience_view(self):
        """
        Tests that the experience api returns the experience requested
        """
        self.client.login(username=self.su_username, password=self.su_password)

        response = self.client.get(
            reverse(
                "api:experience",
                kwargs={
                    "provider_id": "catalog_1",
                    "experience_id": "experience_1",
                },
            ), follow = True
        )

        # assert the response
        self.assertEqual(response.data, {"course": "title"})

    def test_xis_get_experience_error_getting_catalogs(self):
        """
        Test that the experience api returns an error when the status code is
        not 200
        """
        self.client.login(username=self.su_username, password=self.su_password)

        self.mocked_get_xis_catalogs.return_value.status_code = 500

        response = self.client.get(
            reverse(
                "api:experience",
                kwargs={
                    "provider_id": "catalog_1",
                    "experience_id": "experience_1",
                },
            ), follow = True
        )

        # assert the response
        self.assertEqual(
            response.data["detail"],
            "There was an error processing your request.",
        )

    def test_xis_get_experience_error_provider_not_found(self):
        """
        Tests that the experience api returns an error when the provider is not
        found in the list of available catalogs
        """

        self.client.login(username=self.su_username, password=self.su_password)

        response = self.client.get(
            reverse(
                "api:experience",
                kwargs={
                    "provider_id": "catalog_3",
                    "experience_id": "experience_1",
                },
            ),follow = True
        )

        # assert the response
        self.assertEqual(
            response.data["detail"],
            "The provider id does not exist in the XIS catalogs",
        )

    def test_xis_get_experience_error_getting_experience(self):
        """
        Tests that the experience api returns an error when there is an error
        getting the experience
        """

        self.client.login(username=self.su_username, password=self.su_password)
        self.mocked_get_xis_experience.return_value.status_code = 500

        response = self.client.get(
            reverse(
                "api:experience",
                kwargs={
                    "provider_id": "catalog_2",
                    "experience_id": "experience_1",
                },
            ), follow=True
        )

        # assert the response
        self.assertEqual(
            response.data["detail"],
            "There was an error processing your request.",
        )

    def test_xis_post_experience_view(self):
        """
        Tests that the experience api writes and return the response for the
         experience requested
        """
        self.client.login(username=self.su_username, password=self.su_password)

        response = self.client.post(
            path=reverse(
                "api:experience",
                kwargs={
                    "provider_id": "catalog_1",
                    "experience_id": "experience_1",
                },
            ),
            data=self.post_experience_data_dict, follow = True
        )

        self.assertTrue(
                response.status_code in [200, 201]
                )


    def test_xis_post_experience_error_getting_catalogs(self):
        """
        Test that the experience api returns an error when the status code is
        not 200
        """
        self.client.login(username=self.su_username, password=self.su_password)

        self.mocked_get_xis_catalogs.return_value.status_code = 500

        response = self.client.post(
            reverse(
                "api:experience",
                kwargs={
                    "provider_id": "catalog_1",
                    "experience_id": "experience_1",
                },
            ),
            data=self.post_experience_data_dict, follow = True
        )

        # assert the response
        self.assertEqual(
            response.data["detail"],
            "There was an error processing your request.",
        )

    def test_xis_post_experience_error_provider_not_found(self):
        """
        Tests that the experience api returns an error when the provider is not
        found in the list of available catalogs
        """

        self.client.login(username=self.su_username, password=self.su_password)

        response = self.client.post(
            reverse(
                "api:experience",
                kwargs={
                    "provider_id": "catalog_3",
                    "experience_id": "experience_1",
                },
            ),
            data=self.post_experience_data_dict, follow=True
        )

        # assert the response
        self.assertEqual(
            response.data["detail"],
            "The provider id does not exist in the XIS catalogs",
        )

    def test_xis_post_experience_error_getting_experience(self):
        """
        Tests that the experience api returns an error when there is an error
        getting the experience
        """

        self.client.login(username=self.su_username, password=self.su_password)
        self.mocked_get_xis_experience.return_value.status_code = 500

        response = self.client.post(
            reverse(
                "api:experience",
                kwargs={
                    "provider_id": "catalog_2",
                    "experience_id": "experience_1",
                },
            ),
            data=self.post_experience_data_dict
        )

        # assert the response
        self.assertEqual(
            response.data["detail"],
            "The experience does not exist in the XIS catalogs",
        )

    def test_xis_post_experience_error_posting_experience(self):
        """
        Tests that the experience api returns an error when there is an error
        getting the experience
        """

        self.client.login(username=self.su_username, password=self.su_password)
        self.mocked_post_xis_experience.return_value.status_code = 500

        response = self.client.post(
            reverse(
                "api:experience",
                kwargs={
                    "provider_id": "catalog_2",
                    "experience_id": "experience_1",
                },
            ),
            data=self.post_experience_data_dict
        )

        # assert the response
        self.assertEqual(
            response.data["detail"],
            "There was an error processing your request.",
        )
