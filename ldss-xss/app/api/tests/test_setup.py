from rest_framework.test import APITestCase

# from core.models import SchemaLedger, TermSet, TransformationLedger


class TestSetUp(APITestCase):
    """Class with setup and teardown for tests in XDS"""

    def setUp(self):
        """Function to set up necessary data for testing"""

        self.metadata = {
            "Course": {
                "CourseProviderName": {
                    "use": "Required"
                },
                "DepartmentName": {
                    "use": "Optional"
                },
                "CourseCode": {
                    "use": "Required",
                    "data_type": "int"
                },
                "CourseTitle": {
                    "use": "Required",
                    "data_type": "str"
                },
                "CourseShortDescription": {
                    "use": "Required",
                    "data_type": "str"
                },
                "CourseAudience": {
                    "use": "Required"
                },
                "CourseSectionDeliveryMode": {
                    "use": "Optional"
                },
                "CourseObjective": {
                    "use": "Optional",
                    "data_type": "str"
                },
                "CoursePrerequisites": {
                    "use": "Required",
                    "data_type": "str"
                },
                "EstimatedCompletionTime": {
                    "use": "Optional"
                },
                "CourseSpecialNotes": {
                    "use": "Optional",
                    "data_type": "str"
                },
                "CourseAdditionalInformation": {
                    "use": "Optional",
                    "data_type": "str"
                },
                "CourseURL": {
                    "use": "Optional",
                    "data_type": "str"
                },
                "CourseLevel": {
                    "use": "Optional",
                    "data_type": "int"
                },
                "CourseSubjectMatter": {
                    "use": "Required",
                    "data_type": "str"
                },
                "CourseCareerCategory": {
                    "use": "Optional",
                    "data_type": "str"
                },
                "CourseAdministratorInstruction": {
                    "use": "Optional",
                    "data_type": "str"
                },
                "CourseApplicationProcess": {
                    "use": "Optional",
                    "data_type": "str"
                },
                "CourseCredits": {
                    "use": "Optional"
                },
                "CourseFullDescription": {
                    "use": "Optional"
                },
                "CourseEligibility": {
                    "use": "Optional",
                    "data_type": "bool"
                },
                "CourseRegistrationInstructions": {
                    "use": "Optional",
                    "data_type": "str"
                },
                "CourseEquipmentRequired": {
                    "use": "Optional",
                    "data_type": "str"
                },
                "CourseFunding": {
                    "use": "Optional",
                    "data_type": "str"
                },
                "CourseLearningOutcome": {
                    "use": "Optional",
                    "data_type": "str"
                },
                "CourseOfficeOfCoordinationResponsibility": {
                    "use": "Optional",
                    "data_type": "str"
                },
                "CourseReportingInstructions": {
                    "use": "Optional",
                    "data_type": "str"
                },
                "CourseSecurityRequirements": {
                    "use": "Optional",
                    "data_type": "str"
                },
                "CourseSelectionProcess": {
                    "use": "Optional",
                    "data_type": "str"
                },
                "CourseSpecialRequirements": {
                    "use": "Optional",
                    "data_type": "str"
                },
                "CourseTeachingFTD": {
                    "use": "Optional",
                    "data_type": "str"
                },
                "CourseUniformRequirements": {
                    "use": "Optional",
                    "data_type": "str"
                },
                "CourseWaiverAuthority": {
                    "use": "Optional",
                    "data_type": "str"
                },
                "AccreditedBy": {
                    "use": "Required"
                }
            }
        }

        # self.sourceSchema = SchemaLedger(schema_name="test_name",
        #                                  schema_iri="test_name_1.2.3",
        #                                  metadata=self.metadata,
        #                                  status="published",
        #                                  version="1.2.3")
        # self.targetSchema = SchemaLedger(schema_name="test_name_1",
        #                                  schema_iri="test_name_1_1.2.4",
        #                                  metadata=self.metadata,
        #                                  status="published",
        #                                  version="1.2.4")
        # self.sourceSchema.save()
        # self.targetSchema.save()
        # self.sourceTS = TermSet(iri=self.sourceSchema.schema_iri)
        # self.targetTS = TermSet(iri=self.targetSchema.schema_iri)
        # self.schema_mapping = {
        #     "Course": {
        #         "CourseProviderName":
        #         "Course.CourseProviderName"
        #     }
        # }

        # self.mapping = TransformationLedger(source_schema=self.sourceTS,
        #                                     target_schema=self.targetTS,
        #                                     schema_mapping=self.schema_mapping,
        #                                     status="published")
        # self.schema_name = "test_name"
        # self.schema_iri = "schema_iri"
        # self.status = "published"
        # self.version = "1.2.3"
        # self.source_schema = "sourceNm"
        # self.target_schema = "targetNm"
        # self.source_schema_version = "sourceVrs"
        # self.target_schema_version = "targetVrs"

        return super().setUp()

    def tearDown(self):
        return super().tearDown()
