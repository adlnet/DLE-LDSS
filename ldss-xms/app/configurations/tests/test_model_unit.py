from django.forms import ValidationError
from django.test import TestCase, tag

from configurations.models import XMSConfigurations


@tag("unit")
class XMSConfigurationModelTests(TestCase):

    def test_creating_xms_config_with_values(self):
        """
        Test that the XMSConfigurations model can be created with
        custom values.
        """
        XMSConfigurations.objects.create(
            target_xis_host="http://test:8080/api/metadata/",
        )
        # get the created object
        xms_config = XMSConfigurations.objects.first()

        self.assertEqual(
            xms_config.target_xis_host,
            "http://test:8080/api/metadata/"
        )

    def test_creating_multiple_xms_config(self):
        """
        Test that a user cannot create multiple XMSConfigurations models.
        """
        XMSConfigurations.objects.create(
            target_xis_host="http://test:8080/api/metadata/",
        )
        with self.assertRaises(ValidationError):
            # attempt to save another XMSConfigurations model
            XMSConfigurations.objects.create(
                target_xis_host="http://test:8080/api/metadata/",
            )
