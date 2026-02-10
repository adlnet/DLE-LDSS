from unittest.mock import patch

from ddt import ddt
from django.test import TestCase, tag

from api.utils.xis_helper_functions import (get_catalog_experiences,
                                            get_xis_catalogs,
                                            get_xis_experience)
from configurations.models import XMSConfigurations


@tag("unit")
@ddt
class TestXISUtils(TestCase):
    """
    Tests for utilities
    """

    def setUp(self) -> None:
        self.xms_config = XMSConfigurations.objects.create()

        return super().setUp()

    def test_get_xis_catalogs(self):
        """
        Test that the get_xis_catalogs function returns a response
        """

        # mock the response from the XIS catalogs
        with patch("requests.get") as mocked_get:
            mocked_get.return_value = {"test": "value"}

            # call the function
            response = get_xis_catalogs()

            # assert the response
            self.assertEqual(response, {"test": "value"})

    def test_get_xis_experience(self):
        """
        Test that the get_xis_experiences function returns a response
        """

        # mock the response from the XIS experiences
        with patch("requests.get") as mocked_get:
            mocked_get.return_value = {"test": "value"}

            # call the function
            response = get_xis_experience("test", "experience_id")

            # assert the response
            self.assertEqual(response, {"test": "value"})

    def test_get_catalog_experiences(self):
        """
        Test that the get_catalog_experiences function returns a response
        """

        # mock the response from the XIS experiences
        with patch("requests.get") as mocked_get,\
                patch("api.utils.xis_helper_functions."
                      "CourseInformationMapping.objects") as cim:
            mocked_get.return_value = {"test": "value"}
            cim.list_fields.return_value = ['abc']

            # call the function
            response = get_catalog_experiences("test", None, None, None)

            # assert the response
            self.assertEqual(response, {"test": "value"})
