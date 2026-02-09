# from unittest.mock import patch

# from django.test import tag

# from ..models import SchemaLedger, TermSet, TransformationLedger
# from .test_setup import TestSetUp


# @tag('unit')
# class SignalTests(TestSetUp):

#     def test_create_term_set(self):
#         """Function to check create postsave of schema ledger
#         in termsets and terms"""

#         with patch('core.signals.termset_object'):
#             self.schema.save()
#             termset = TermSet.objects.get(name=self.schema_name)

#             self.assertEqual(termset.name, self.schema_name)
#             self.assertEqual(termset.version, self.version)
#             self.assertEqual(termset.status, self.status)

#     def test_update_term_set(self):
#         """Function to check update postsave of schema ledger
#         in termsets and terms"""

#         with patch('core.signals.update_status'), \
#                 patch('core.signals.create_term_set'):

#             self.schema.save()

#             schemaledger = \
#                 SchemaLedger.objects.get(schema_name=self.schema_name)
#             schemaledger.status = 'retired'
#             schemaledger.save()

#             termset = TermSet.objects.get(name=self.schema_name)
#             self.assertEqual(termset.status, 'retired')

#     def test_map_term_sets(self):
#         """Test to verify mappings are kicked off"""

#         with patch('core.signals.termset_map') as map,\
#                 patch('core.signals.create_term_set'), \
#                 patch('core.signals.update_term_set'):
#             source = TermSet(name='source', version='1.0.0')
#             source.save()
#             target = TermSet(name='target', version='0.0.1')
#             target.save()

#             TransformationLedger(source_schema=source, target_schema=target,
#                                  status=TransformationLedger.
#                                  SCHEMA_STATUS_CHOICES[0][0],
#                                  schema_mapping="").save()
#             source.delete()
#             target.delete()
#             map.assert_called_once()
