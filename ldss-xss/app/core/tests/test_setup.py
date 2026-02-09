from django.test import TestCase
# from core.models import SchemaLedger, TermSet
# from users.models import CustomUser

class TestSetUp(TestCase):
    """Class with setup and teardown for tests in XDS"""

    def setUp(self):
        """Function to set up necessary data for testing"""

        # self.schema_name = 'test_name'
        # self.schema_iri = 'test_iri'
        # self.metadata = {'test': {
        #     'test1': {"use": "Required",
        #               "type": "int"
        #               },
        #     'test2': {"use": "Optional",
        #               "type": "char"
        #               }
        # }
        # }
        # self.status = 'published'
        # self.version = '1.0.0'
        # self.major_version = 1
        # self.minor_version = 0
        # self.patch_version = 0

        # CustomUser(username="test@test.com").save()
        # self.user = CustomUser.objects.get(username="test@test.com")

        # self.schema = SchemaLedger(schema_name=self.schema_name,
        #                            schema_iri=self.schema_iri,
        #                            metadata=self.metadata,
        #                            status=self.status,
        #                            version=self.version,
        #                            major_version=self.major_version,
        #                            minor_version=self.minor_version,
        #                            patch_version=self.patch_version)

        # self.termset = TermSet(name=self.schema_name,
        #                        status=self.status,
        #                        version=self.version)
        # self.schema.save()

        # self.ts_name = "test_name"
        # self.ts_version = "1.0.0"
        # self.ts_status = TermSet.STATUS_CHOICES[0][0]

        # self.ts = TermSet(name=self.ts_name,
        #                   version=self.ts_version, status=self.ts_status)

        # self.ts.save()

        return super().setUp()

    def tearDown(self):
        return super().tearDown()
    