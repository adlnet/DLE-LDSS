import json
from unittest.mock import mock_open, patch, MagicMock
import unittest
# from clamd import EICAR
# from django.core.exceptions import ValidationError
# from django.core.files.base import ContentFile
from django.test import tag
# from core.models import (ChildTermSet, SchemaLedger, Term, TermSet,
#                          TransformationLedger, validate_version, NeoTerm, 
#                          NeoMapping, NeoAlias, NeoContext, 
#                          NeoContextDescription, NeoDefinition)
from core.models import (NeoTerm, 
                         NeoMapping, NeoAlias, NeoContext, 
                         NeoContextDescription, NeoDefinition)
from uid.models import UIDNode, ProviderDjangoModel
from neomodel import exceptions
# from .test_setup import TestSetUp

# @tag('unit')
# class ModelTests(TestSetUp):

    # def test_schema_ledger(self):
    #     """Test that creating a SchemaLedger is successful"""

    #     schema_name = 'test_name'
    #     schema_iri = 'test_iri'
    #     metadata = {
    #         'test': 'test'
    #     }
    #     status = 'published'
    #     version = '1.0.1'
    #     major_version = 1
    #     minor_version = 0
    #     patch_version = 1

    #     schema = SchemaLedger(schema_name=schema_name,
    #                           schema_iri=schema_iri,
    #                           metadata=metadata,
    #                           status=status,
    #                           version=version,
    #                           major_version=major_version,
    #                           minor_version=minor_version,
    #                           patch_version=patch_version)

    #     self.assertEqual(schema.schema_name, schema_name)
    #     self.assertEqual(schema.schema_iri, schema_iri)
    #     self.assertEqual(schema.status, status)
    #     self.assertEqual(schema.metadata, metadata)
    #     self.assertEqual(schema.version, version)
    #     self.assertEqual(schema.major_version, major_version)
    #     self.assertEqual(schema.minor_version, minor_version)
    #     self.assertEqual(schema.patch_version, patch_version)

    # def test_schema_ledger_virus(self):
    #     """Test that creating a SchemaLedger with a virus fails"""

    #     schema_name = 'test_name'
    #     schema_iri = 'test_iri'
    #     status = 'published'
    #     version = '1.0.1'
    #     major_version = 1
    #     minor_version = 0
    #     patch_version = 1
    #     file = ContentFile(EICAR, 'virus')

    #     schema = SchemaLedger(schema_name=schema_name,
    #                           schema_iri=schema_iri,
    #                           status=status,
    #                           major_version=major_version,
    #                           minor_version=minor_version,
    #                           patch_version=patch_version,
    #                           schema_file=file)

    #     with patch('core.models.logger') as log,\
    #             patch('core.models.clamd') as clam:
    #         clam.instream.return_value = {'stream': ('BAD', 'EICAR')}
    #         clam.ClamdNetworkSocket.return_value = clam

    #         self.assertEqual(schema.version, '')
    #         self.assertEqual(schema.schema_file.size, len(EICAR))
    #         schema.clean()
    #         self.assertEqual(schema.version, version)
    #         self.assertEqual(schema.schema_file, None)
    #         self.assertGreater(log.error.call_count, 0)
    #         self.assertIn('EICAR', log.error.call_args[0][2])
    #         self.assertGreater(clam.instream.call_count, 0)
    #         self.assertEqual(file, clam.instream.call_args[0][0])
    #         self.assertIsNone(schema.metadata)

    # def test_schema_ledger_non_json(self):
    #     """Test that creating a SchemaLedger with a non json file fails"""

    #     schema_name = 'test_name'
    #     schema_iri = 'test_iri'
    #     status = 'published'
    #     version = '1.0.1'
    #     major_version = 1
    #     minor_version = 0
    #     patch_version = 1
    #     file_contents = b'test string'
    #     file = ContentFile(file_contents, 'not json')

    #     schema = SchemaLedger(schema_name=schema_name,
    #                           schema_iri=schema_iri,
    #                           status=status,
    #                           major_version=major_version,
    #                           minor_version=minor_version,
    #                           patch_version=patch_version,
    #                           schema_file=file)

    #     with patch('core.models.logger') as log,\
    #             patch('core.models.clamd') as clam,\
    #             patch('builtins.open', mock_open()),\
    #             patch('core.models.magic') as magic,\
    #             patch('core.models.os'):
    #         magic.from_file.return_value = 'text/plain'
    #         clam.instream.return_value = {'stream': ('OK', 'OKAY')}
    #         clam.ClamdNetworkSocket.return_value = clam

    #         self.assertEqual(schema.version, '')
    #         self.assertEqual(schema.schema_file.size, len(file_contents))
    #         schema.clean()
    #         self.assertEqual(schema.version, version)
    #         self.assertEqual(schema.schema_file, None)
    #         self.assertGreater(log.error.call_count, 0)
    #         self.assertIn('text/plain',
    #                       log.error.call_args[0][1])
    #         self.assertIsNone(schema.metadata)

    # def test_schema_ledger_bleach(self):
    #     """Test that creating a SchemaLedger with a valid file passes"""

    #     schema_name = 'test_name'
    #     schema_iri = 'test_iri'
    #     status = 'published'
    #     version = '1.0.1'
    #     major_version = 1
    #     minor_version = 0
    #     patch_version = 1
    #     file_contents = json.dumps({'test': '<em>test</em>'}).encode('ascii')
    #     file = ContentFile(file_contents, 'with html tags')
    #     metadata = {'test': 'test'}

    #     schema = SchemaLedger(schema_name=schema_name,
    #                           schema_iri=schema_iri,
    #                           status=status,
    #                           major_version=major_version,
    #                           minor_version=minor_version,
    #                           patch_version=patch_version,
    #                           schema_file=file)

    #     with patch('core.models.logger') as log,\
    #             patch('core.models.clamd') as clam,\
    #             patch('builtins.open', mock_open()),\
    #             patch('core.models.magic') as magic,\
    #             patch('core.models.os'):
    #         magic.from_file.return_value = 'application/json'
    #         clam.instream.return_value = {'stream': ('OK', 'OKAY')}
    #         clam.ClamdNetworkSocket.return_value = clam

    #         self.assertEqual(schema.version, '')
    #         self.assertEqual(schema.schema_file.size, len(file_contents))
    #         schema.clean()
    #         self.assertEqual(schema.version, version)
    #         self.assertEqual(schema.schema_file, None)
    #         self.assertEqual(log.error.call_count, 0)
    #         self.assertDictEqual(schema.metadata, metadata)

    # def test_transformation_ledger(self):
    #     """Test that creating a transformationLedger is successful"""

    #     with patch('core.signals.termset_map'):
    #         self.termset.save()

    #         source_schema_name = self.termset
    #         target_schema_name = self.termset
    #         schema_mapping = {
    #             "test": "test"
    #         }
    #         status = "published"

    #         mapping = \
    #             TransformationLedger(source_schema=source_schema_name,
    #                                  target_schema=target_schema_name,
    #                                  schema_mapping=schema_mapping,
    #                                  status=status)

    #         mapping.save()

    #         self.assertEqual(mapping.source_schema, source_schema_name)
    #         self.assertEqual(mapping.target_schema, target_schema_name)
    #         self.assertEqual(mapping.schema_mapping, schema_mapping)
    #         self.assertEqual(mapping.status, status)

    # def test_transformation_ledger_virus(self):
    #     """Test that creating a TransformationLedger with a virus fails"""
    #     self.termset.save()

    #     source_schema_name = self.termset
    #     target_schema_name = self.termset
    #     file = ContentFile(EICAR, 'virus')
    #     status = "published"

    #     mapping = \
    #         TransformationLedger(source_schema=source_schema_name,
    #                              target_schema=target_schema_name,
    #                              schema_mapping_file=file,
    #                              status=status)

    #     with patch('core.models.logger') as log,\
    #             patch('core.models.clamd') as clam:
    #         clam.instream.return_value = {'stream': ('BAD', 'EICAR')}
    #         clam.ClamdNetworkSocket.return_value = clam

    #         self.assertEqual(mapping.schema_mapping_file.size, len(EICAR))
    #         mapping.clean()
    #         self.assertEqual(mapping.schema_mapping_file, None)
    #         self.assertGreater(log.error.call_count, 0)
    #         self.assertIn('EICAR', log.error.call_args[0][2])
    #         self.assertGreater(clam.instream.call_count, 0)
    #         self.assertEqual(file, clam.instream.call_args[0][0])
    #         self.assertIsNone(mapping.schema_mapping)

    # def test_transformation_ledger_non_json(self):
    #     """Test that creating a TransformationLedger with a non json file fails
    #     """
    #     self.termset.save()

    #     source_schema_name = self.termset
    #     target_schema_name = self.termset
    #     file_contents = b'test string'
    #     file = ContentFile(file_contents, 'not json')
    #     status = "published"

    #     mapping = \
    #         TransformationLedger(source_schema=source_schema_name,
    #                              target_schema=target_schema_name,
    #                              schema_mapping_file=file,
    #                              status=status)

    #     with patch('core.models.logger') as log,\
    #             patch('core.models.clamd') as clam,\
    #             patch('builtins.open', mock_open()),\
    #             patch('core.models.magic') as magic,\
    #             patch('core.models.os'):
    #         magic.from_file.return_value = 'text/plain'
    #         clam.instream.return_value = {'stream': ('OK', 'OKAY')}
    #         clam.ClamdNetworkSocket.return_value = clam

    #         self.assertEqual(mapping.schema_mapping_file.size,
    #                          len(file_contents))
    #         mapping.clean()
    #         self.assertEqual(mapping.schema_mapping_file, None)
    #         self.assertGreater(log.error.call_count, 0)
    #         self.assertIn('text/plain',
    #                       log.error.call_args[0][1])
    #         self.assertIsNone(mapping.schema_mapping)

    # def test_transformation_ledger_bleach(self):
    #     """Test that creating a TransformationLedger with a valid file passes
    #     """
    #     self.termset.save()

    #     source_schema_name = self.termset
    #     target_schema_name = self.termset
    #     tagged_metadata = {'test': '<em>test</em>'}
    #     file_contents = json.dumps(tagged_metadata).encode('ascii')
    #     file = ContentFile(file_contents, 'with html tags')
    #     metadata = {'test': 'test'}
    #     status = "published"

    #     mapping = \
    #         TransformationLedger(source_schema=source_schema_name,
    #                              target_schema=target_schema_name,
    #                              schema_mapping_file=file,
    #                              status=status)

    #     with patch('core.models.logger') as log,\
    #             patch('core.models.clamd') as clam,\
    #             patch('builtins.open', mock_open()),\
    #             patch('core.models.magic') as magic,\
    #             patch('core.models.os'):
    #         magic.from_file.return_value = 'application/json'
    #         clam.instream.return_value = {'stream': ('OK', 'OKAY')}
    #         clam.ClamdNetworkSocket.return_value = clam

    #         self.assertEqual(mapping.schema_mapping_file.size,
    #                          len(file_contents))
    #         mapping.clean()
    #         self.assertEqual(mapping.schema_mapping_file, None)
    #         self.assertEqual(log.error.call_count, 0)
    #         self.assertDictEqual(mapping.schema_mapping, metadata)

    # def test_term_set(self):
    #     """Test that creating a TermSet is successful"""
    #     ts_name = "test_name"
    #     ts_version = "0.0.1"
    #     ts_status = TermSet.STATUS_CHOICES[0][0]

    #     expected_iri = "xss:" + ts_version + "@" + ts_name

    #     ts = TermSet(name=ts_name, version=ts_version, status=ts_status)

    #     ts.save()

    #     self.assertEquals(ts.iri, expected_iri)
    #     self.assertEquals(ts.name, ts_name)
    #     self.assertEquals(ts.version, ts_version)
    #     self.assertEquals(ts.status, ts_status)

    # def test_child_term_set(self):
    #     """Test that creating a ChildTermSet is successful"""
    #     cts_name = "test_name"
    #     cts_status = TermSet.STATUS_CHOICES[0][0]
    #     cts_parent = self.ts

    #     expected_iri = "xss:" + cts_parent.version + \
    #         "@" + cts_parent.name + "/" + cts_name

    #     cts = ChildTermSet(name=cts_name, status=cts_status,
    #                        parent_term_set=cts_parent)

    #     cts.save()

    #     self.assertEquals(cts.iri, expected_iri)
    #     self.assertEquals(cts.name, cts_name)
    #     self.assertEquals(cts.version, cts_parent.version)
    #     self.assertEquals(cts.status, cts_status)

    # def test_term(self):
    #     """Test that creating a Term is successful"""
    #     t_name = "test_name"
    #     t_description = "test description"
    #     t_data_type = "string"
    #     t_use = Term.USE_CHOICES[0][0]
    #     t_source = "source"
    #     t_ts = self.ts
    #     t_status = "published"
    #     expected_iri = "xss:" + t_ts.version + "@" + t_ts.name + "?" + t_name
    #     expected_export = {'use': t_use, 'data_type': t_data_type,
    #                        'source': t_source, 'description': t_description}
    #     term = Term(name=t_name, description=t_description,
    #                 data_type=t_data_type, use=t_use,
    #                 source=t_source, term_set=t_ts, status=t_status)
    #     term.save()
    #     self.assertEquals(term.iri, expected_iri)
    #     self.assertEquals(term.name, t_name)
    #     self.assertEquals(term.data_type, t_data_type)
    #     self.assertEquals(term.use, t_use)
    #     self.assertEquals(term.source, t_source)
    #     self.assertEquals(term.term_set, t_ts)
    #     self.assertEquals(term.status, t_status)
    #     self.assertDictEqual(term.export(), expected_export,
    #                          "Incorrect Term export")

    # def test_validate_version_pass(self):
    #     """Test that validate version passes correct formats"""
    #     validate_version("0.0.1")
    #     self.assertTrue(True)

    # def test_validate_version_fail(self):
    #     """Test that validate version fails bad formats"""
    #     self.assertRaises(ValidationError, validate_version, "0.0..1")

@tag('unit')
class NeoTermTests(unittest.TestCase):

    def setUp(self):
        self.patcher_connect = patch("neomodel.sync_.relationship_manager.RelationshipManager.connect", return_value=None)
        self.mock_connect = self.patcher_connect.start()
        self.patcher_create_node = patch.object(UIDNode, "create_node", return_value=MagicMock(uid="mocked-uid"))
        self.mock_create_node = self.patcher_create_node.start()
        self.patcher_provider = patch.object(ProviderDjangoModel, "ensure_provider_exists", return_value=MagicMock(default_uid="mocked-provider-uid", uid=MagicMock()))
        self.mock_ensure_provider = self.patcher_provider.start()
        self.patcher_save = patch.object(NeoTerm, "save", return_value=None)
        self.mock_save = self.patcher_save.start()
        self.patcher_settings = patch("core.models.settings.INSTANCE_ID", new="TEST")
        self.mock_settings_instance_id = self.patcher_settings.start()
        self. patcher_neoterm_nodes = patch.object(NeoTerm, "nodes", autospec=True)
        self.mock_neoterm_nodes = self.patcher_neoterm_nodes.start()

    def tearDown(self):
        self.patcher_connect.stop()
        self.patcher_create_node.stop()
        self.patcher_provider.stop()
        self.patcher_save.stop()
        self.patcher_settings.stop()
        self.patcher_neoterm_nodes.stop()

    # def test_create_new_term_no_lcvid(self):
    #     term = NeoTerm.create_new_term()
    #     self.assertIsNone(term.lcvid)
    #     self.assertEqual(term.uid, "mocked-uid")
    #     self.assertEqual(term.uid_chain, "TEST-mocked-provider-uid-mocked-uid")

    def test_create_new_term_with_lcvid(self):
        term = NeoTerm.create_new_term(lcvid="test-lcvid")
        self.assertEqual(term.lcvid, "test-lcvid")
        self.assertEqual(term.uid, "mocked-uid")
    
    def test_create_uid_node_exception(self):
        self.mock_create_node.side_effect = Exception("UID create failed")
        with self.assertRaises(Exception) as context:
            NeoTerm.create_new_term()
        self.assertIn("UID create failed", str(context.exception))
    
    def test_create_new_term_provider_exception(self):
        self.mock_ensure_provider.side_effect = Exception("Provider failed")
        with self.assertRaises(Exception) as context:
            NeoTerm.create_new_term("custom-lcvid")
        self.assertIn("Provider failed", str(context.exception))
    
    def test_create_new_term_save_exception(self):
        self.mock_save.side_effect = Exception("Save failed")
        with self.assertRaises(Exception) as context:
            NeoTerm.create_new_term("custom-lcvid")
        self.assertIn("Save failed", str(context.exception))

    def test_get_by_uid(self):
        node = MagicMock()
        self.mock_neoterm_nodes.get.return_value = node
        result  = NeoTerm.get_by_uid("test-uid")
        self.assertEqual(result, node)
        self.mock_neoterm_nodes.get.assert_called_once_with(uid="test-uid")
    
    def test_get_by_uid_not_found(self,):
        self.mock_neoterm_nodes.get.return_value = None
        result = NeoTerm.get_by_uid("uid-123")
        self.assertIsNone(result)
        self.mock_neoterm_nodes.get.assert_called_once_with(uid="uid-123")
@tag('unit')
class NeoAliasTests(unittest.TestCase):
    def setUp(self):
        self.nodes_patcher = patch.object(NeoAlias, 'nodes', new_callable=MagicMock)
        self.mock_nodes = self.nodes_patcher.start()
        self.logger_patcher = patch("core.models.logger")
        self.mock_logger = self.logger_patcher.start()
        self.save_patcher = patch("core.models.NeoAlias.save", autospec=True)
        self.mock_save = self.save_patcher.start()
        self.alias_instance = NeoAlias()
        self.alias_instance.alias = "test_alias"
        self.alias_instance.term = MagicMock()
        self.alias_instance.context = MagicMock()
        self.alias_instance.collided_definition = MagicMock()

    def tearDown(self):
        self.nodes_patcher.stop()
        self.logger_patcher.stop()
        self.save_patcher.stop()

    def test_get_or_create_existing(self):
        existing_alias = MagicMock(spec=NeoAlias)
        self.mock_nodes.get_or_none.return_value = existing_alias
        result, created = NeoAlias.get_or_create("existing_alias")
        self.assertEqual(result, existing_alias)
        self.assertFalse(created)
        self.mock_nodes.get_or_none.assert_called_once_with(alias="existing_alias")

    def test_get_or_create_new(self):
        self.mock_nodes.get_or_none.return_value = None
        result, created = NeoAlias.get_or_create("new_alias")
        self.assertTrue(created)
        self.assertEqual(result.alias, "new_alias")
        self.assertTrue(self.mock_save.called)

    def test_get_or_create_neomodel_exception(self):
        self.mock_nodes.get_or_none.side_effect = exceptions.NeomodelException("Error on get_or_none")
        with self.assertRaises(exceptions.NeomodelException) as context:
            NeoAlias.get_or_create("alias_exception")
        self.assertEqual(str(context.exception), "Error on get_or_none")
        self.mock_logger.error.assert_called_once()
        log_msg = self.mock_logger.error.call_args[0][0]
        self.assertIn("NeoModel-related error while getting or creating alias", log_msg)

    def test_get_or_create_generic_exception(self):
        self.mock_nodes.get_or_none.side_effect = Exception("Generic error")
        with self.assertRaises(Exception) as context:
            NeoAlias.get_or_create("alias_generic")
        self.assertEqual(str(context.exception), "Generic error")
        self.mock_logger.error.assert_called_once()
        log_msg = self.mock_logger.error.call_args[0][0]
        self.assertIn("Unexpected error in get_or_create for alias", log_msg)

    def test_set_relationships_all(self):
        term_node = MagicMock()
        context_node = MagicMock()
        collided_definition = MagicMock()
        self.alias_instance.set_relationships(
            term_node=term_node,
            context_node=context_node,
            collided_definition=collided_definition
        )
        self.alias_instance.term.connect.assert_called_once_with(term_node)
        self.alias_instance.context.connect.assert_called_once_with(context_node)
        self.alias_instance.collided_definition.connect.assert_called_once_with(collided_definition)

    def test_set_relationships_partial(self):
        term_node = MagicMock()
        self.alias_instance.set_relationships(term_node=term_node)
        self.alias_instance.term.connect.assert_called_once_with(term_node)
        self.alias_instance.context.connect.assert_not_called()
        self.alias_instance.collided_definition.connect.assert_not_called()

    def test_set_relationships_neomodel_exception(self):
        term_node = MagicMock()
        self.alias_instance.term.connect.side_effect = exceptions.NeomodelException("Term connection error")
        with self.assertRaises(exceptions.NeomodelException) as context:
            self.alias_instance.set_relationships(term_node=term_node)
        self.assertEqual(str(context.exception), "Term connection error")
        self.mock_logger.error.assert_called_once()
        log_msg = self.mock_logger.error.call_args[0][0]
        self.assertIn("NeoModel-related error while connecting relationships for alias", log_msg)

    def test_set_relationships_generic_exception(self):
        term_node = MagicMock()
        self.alias_instance.term.connect.side_effect = Exception("Generic error in connection")
        with self.assertRaises(Exception) as context:
            self.alias_instance.set_relationships(term_node=term_node)
        self.assertEqual(str(context.exception), "Generic error in connection")
        self.mock_logger.error.assert_called_once()
        log_msg = self.mock_logger.error.call_args[0][0]
        self.assertIn("Unexpected error while connecting relationships for alias", log_msg)

    def test_handle_collision_with_context(self):
        definition_node = MagicMock()
        context_node = MagicMock()
        self.alias_instance.handle_collision(definition_node, context_node=context_node)
        self.alias_instance.context.connect.assert_called_once_with(context_node)
        self.alias_instance.collided_definition.connect.assert_called_once_with(definition_node)

    def test_handle_collision_without_context(self):
        definition_node = MagicMock()
        self.alias_instance.handle_collision(definition_node)
        self.alias_instance.context.connect.assert_not_called()
        self.alias_instance.collided_definition.connect.assert_called_once_with(definition_node)
@tag('unit')
class NeoContextTests(unittest.TestCase):
    def setUp(self):
        self.nodes_patcher = patch.object(NeoContext, 'nodes', new_callable=MagicMock)
        self.mock_nodes = self.nodes_patcher.start()
        self.logger_patcher = patch("core.models.logger")
        self.mock_logger = self.logger_patcher.start()
        self.save_patcher = patch("core.models.NeoContext.save", autospec=True)
        self.mock_save = self.save_patcher.start()
        self.context_instance = NeoContext()
        self.context_instance.context = "sample_context"
        self.context_instance.term = MagicMock()
        self.context_instance.alias = MagicMock()
        self.context_instance.definition = MagicMock()
        self.context_instance.context_description = MagicMock()

    def tearDown(self):
        self.nodes_patcher.stop()
        self.logger_patcher.stop()
        self.save_patcher.stop()

    def test_get_or_create_existing(self):
        existing_instance = MagicMock(spec=NeoContext)
        self.mock_nodes.get_or_none.return_value = existing_instance
        result, created = NeoContext.get_or_create("existing_context")
        self.assertEqual(result, existing_instance)
        self.assertFalse(created)
        self.mock_nodes.get_or_none.assert_called_once_with(context="existing_context")

    def test_get_or_create_new(self):
        self.mock_nodes.get_or_none.return_value = None
        result, created = NeoContext.get_or_create("new_context")
        self.assertTrue(created)
        self.assertEqual(result.context, "new_context")
        self.assertTrue(self.mock_save.called)

    def test_get_or_create_empty_context(self):
        with self.assertRaises(ValueError) as cm:
            NeoContext.get_or_create("")
        self.assertEqual(str(cm.exception),
                        "Could not get or create the requested context node w/ context: ")

    def test_get_or_create_neomodel_exception(self):
        self.mock_nodes.get_or_none.side_effect = exceptions.NeomodelException("Error on get_or_none")
        with self.assertRaises(exceptions.NeomodelException) as context:
            NeoContext.get_or_create("exception_context")
        self.assertEqual(str(context.exception), "Error on get_or_none")
        self.mock_logger.error.assert_called_once()
        log_msg = self.mock_logger.error.call_args[0][0]
        self.assertIn("NeoModel-related error while getting or creating context", log_msg)

    def test_get_or_create_generic_exception(self):
        self.mock_nodes.get_or_none.side_effect = Exception("Generic error")
        with self.assertRaises(Exception) as context:
            NeoContext.get_or_create("generic_context")
        self.assertEqual(str(context.exception), "Generic error")
        self.mock_logger.error.assert_called_once()
        log_msg = self.mock_logger.error.call_args[0][0]
        self.assertIn("Unexpected error in get_or_create for context", log_msg)

    def test_set_relationships_all(self):
        term_node = MagicMock()
        alias_node = MagicMock()
        definition_node = MagicMock()
        context_description_node = MagicMock()
        self.context_instance.set_relationships(
            term_node=term_node,
            alias_node=alias_node,
            definition_node=definition_node,
            context_description_node=context_description_node
        )
        self.context_instance.term.connect.assert_called_once_with(term_node)
        self.context_instance.alias.connect.assert_called_once_with(alias_node)
        self.context_instance.definition.connect.assert_called_once_with(definition_node)
        self.context_instance.context_description.connect.assert_called_once_with(context_description_node)

    def test_set_relationships_partial(self):
        term_node = MagicMock()
        self.context_instance.set_relationships(term_node=term_node)
        self.context_instance.term.connect.assert_called_once_with(term_node)
        self.context_instance.alias.connect.assert_not_called()
        self.context_instance.definition.connect.assert_not_called()
        self.context_instance.context_description.connect.assert_not_called()

    def test_set_relationships_neomodel_exception(self):
        term_node = MagicMock()
        self.context_instance.term.connect.side_effect = exceptions.NeomodelException("Term connection error")
        with self.assertRaises(exceptions.NeomodelException) as context:
            self.context_instance.set_relationships(term_node=term_node)
        self.assertEqual(str(context.exception), "Term connection error")
        self.mock_logger.error.assert_called_once()
        log_msg = self.mock_logger.error.call_args[0][0]
        self.assertIn("NeoModel-related error while connecting relationships for context", log_msg)

    def test_set_relationships_generic_exception(self):
        term_node = MagicMock()
        self.context_instance.term.connect.side_effect = Exception("Generic connection error")
        with self.assertRaises(Exception) as context:
            self.context_instance.set_relationships(term_node=term_node)
        self.assertEqual(str(context.exception), "Generic connection error")
        self.mock_logger.error.assert_called_once()
        log_msg = self.mock_logger.error.call_args[0][0]
        self.assertIn("Unexpected error while connecting relationships for context", log_msg)

@tag('unit')
class NeoContextDescriptionTests(unittest.TestCase):
    def setUp(self):
        self.logger_patcher = patch("core.models.logger")
        self.mock_logger = self.logger_patcher.start()
        self.save_patcher = patch("core.models.NeoContextDescription.save", autospec=True)
        self.mock_save = self.save_patcher.start()
        self.context_description_instance = NeoContextDescription()
        self.context_description_instance.context_description = "sample_description"
        self.context_description_instance.definition = MagicMock()
        self.context_description_instance.context = MagicMock()

    def tearDown(self):
        self.logger_patcher.stop()
        self.save_patcher.stop()

    def test_get_or_create_existing(self):
        dummy_existing = MagicMock(spec=NeoContextDescription)
        dummy_existing.context_description = "existing_description"
        context_node = MagicMock()
        context_node.context_description.all.return_value = [dummy_existing]
        result, created = NeoContextDescription.get_or_create("existing_description", context_node)
        self.assertEqual(result, dummy_existing)
        self.assertFalse(created)
        context_node.context_description.all.assert_called_once()

    def test_get_or_create_new_with_context_node(self):
        context_node = MagicMock()
        context_node.context_description.all.return_value = []
        result, created = NeoContextDescription.get_or_create("new_description", context_node)
        self.assertTrue(created)
        self.assertEqual(result.context_description, "new_description")
        self.assertTrue(self.mock_save.called)

    def test_get_or_create_new_without_context_node(self):
        result, created = NeoContextDescription.get_or_create("new_description", None)
        self.assertTrue(created)
        self.assertEqual(result.context_description, "new_description")
        self.assertTrue(self.mock_save.called)

    def test_get_or_create_neomodel_exception(self):
        context_node = MagicMock()
        context_node.context_description.all.side_effect = exceptions.NeomodelException("Error in all")
        with self.assertRaises(exceptions.NeomodelException) as context:
            NeoContextDescription.get_or_create("desc", context_node)
        self.assertEqual(str(context.exception), "Error in all")
        self.mock_logger.error.assert_called_once()
        log_msg = self.mock_logger.error.call_args[0][0]
        self.assertIn("NeoModel-related error while getting or creating context_description", log_msg)

    def test_get_or_create_generic_exception(self):
        context_node = MagicMock()
        context_node.context_description.all.side_effect = Exception("Generic error in all")
        with self.assertRaises(Exception) as context:
            NeoContextDescription.get_or_create("desc", context_node)
        self.assertEqual(str(context.exception), "Generic error in all")
        self.mock_logger.error.assert_called_once()
        log_msg = self.mock_logger.error.call_args[0][0]
        self.assertIn("Unexpected error in get_or_create for context_description", log_msg)

    def test_set_relationships_all(self):
        definition_node = MagicMock()
        context_node = MagicMock()
        self.context_description_instance.set_relationships(definition_node=definition_node, context_node=context_node)
        self.context_description_instance.definition.connect.assert_called_once_with(definition_node)
        self.context_description_instance.context.connect.assert_called_once_with(context_node)

    def test_set_relationships_partial_definition_only(self):
        definition_node = MagicMock()
        self.context_description_instance.set_relationships(definition_node=definition_node)
        self.context_description_instance.definition.connect.assert_called_once_with(definition_node)
        self.context_description_instance.context.connect.assert_not_called()

    def test_set_relationships_partial_context_only(self):
        context_node = MagicMock()
        self.context_description_instance.set_relationships(context_node=context_node)
        self.context_description_instance.context.connect.assert_called_once_with(context_node)
        self.context_description_instance.definition.connect.assert_not_called()

    def test_set_relationships_neomodel_exception(self):
        definition_node = MagicMock()
        self.context_description_instance.definition.connect.side_effect = exceptions.NeomodelException("Definition error")
        with self.assertRaises(exceptions.NeomodelException) as context:
            self.context_description_instance.set_relationships(definition_node=definition_node)
        self.assertEqual(str(context.exception), "Definition error")
        self.mock_logger.error.assert_called_once()
        log_msg = self.mock_logger.error.call_args[0][0]
        self.assertIn("NeoModel-related error while connecting relationships for context_description", log_msg)

    def test_set_relationships_generic_exception(self):
        definition_node = MagicMock()
        self.context_description_instance.definition.connect.side_effect = Exception("Generic error")
        with self.assertRaises(Exception) as context:
            self.context_description_instance.set_relationships(definition_node=definition_node)
        self.assertEqual(str(context.exception), "Generic error")
        self.mock_logger.error.assert_called_once()
        log_msg = self.mock_logger.error.call_args[0][0]
        self.assertIn("Unexpected error while connecting relationships for context_description", log_msg)
@tag('unit')
class NeoDefinitionTests(unittest.TestCase):
    def setUp(self):
        self.nodes_patcher = patch.object(NeoDefinition, 'nodes', new_callable=MagicMock)
        self.mock_nodes = self.nodes_patcher.start()
        self.logger_patcher = patch("core.models.logger")
        self.mock_logger = self.logger_patcher.start()
        self.save_patcher = patch("core.models.NeoDefinition.save", autospec=True)
        self.mock_save = self.save_patcher.start()
        self.definition_instance = NeoDefinition()
        self.definition_instance.definition = "sample_definition"
        self.definition_instance.term = MagicMock()
        self.definition_instance.context = MagicMock()
        self.definition_instance.context_description = MagicMock()
        self.definition_instance.collision = MagicMock()
        self.definition_instance.collision_alias = MagicMock()

    def tearDown(self):
        self.nodes_patcher.stop()
        self.logger_patcher.stop()
        self.save_patcher.stop()

    def test_get_or_create_existing(self):
        existing_instance = MagicMock(spec=NeoDefinition)
        self.mock_nodes.get_or_none.return_value = existing_instance
        result, created = NeoDefinition.get_or_create("existing_def", "existing_entity_id")
        self.assertEqual(result, existing_instance)
        self.assertFalse(created)
        self.mock_nodes.get_or_none.assert_called_once_with(definition="existing_def", entity_id="existing_entity_id")

    def test_get_or_create_new(self):
        self.mock_nodes.get_or_none.return_value = None
        result, created = NeoDefinition.get_or_create("new_def", definition_embedding=[0.1, 0.2], entity_id="new_entity_id")
        self.assertTrue(created)
        self.assertEqual(result.definition, "new_def")
        self.assertEqual(result.embedding, [0.1, 0.2])
        self.assertTrue(self.mock_save.called)

    def test_get_or_create_exception(self):
        self.mock_nodes.get_or_none.side_effect = Exception("Generic error in get_or_create")
        with self.assertRaises(Exception) as context:
            NeoDefinition.get_or_create("error_def", "error_entity_id")
        self.assertEqual(str(context.exception), "Generic error in get_or_create")
        self.mock_logger.error.assert_called_once()
        log_msg = self.mock_logger.error.call_args[0][0]
        self.assertIn("Error in get for NeoDefinition", log_msg)

    def test_get_by_definition_success(self):
        expected_instance = MagicMock(spec=NeoDefinition)
        self.mock_nodes.get.return_value = expected_instance
        result = NeoDefinition.get_by_definition("some_def")
        self.assertEqual(result, expected_instance)
        self.mock_nodes.get.assert_called_once_with(definition="some_def")

    def test_get_by_definition_does_not_exist(self):
        with patch.object(exceptions.DoesNotExist, '__init__', lambda self, *args, **kwargs: None):
            does_not_exist_exception = exceptions.DoesNotExist("Not found")
            does_not_exist_exception.__str__ = lambda self: "Not found"
            self.mock_nodes.get.side_effect = does_not_exist_exception
            with self.assertRaises(exceptions.DoesNotExist) as context:
                NeoDefinition.get_by_definition("nonexistent_def")
            self.assertEqual(str(context.exception), "Not found")
            self.mock_logger.error.assert_called_once()
            log_msg = self.mock_logger.error.call_args[0][0]
            self.assertIn("NeoModel-related error while getting definition", log_msg)

    def test_get_by_definition_generic_exception(self):
        self.mock_nodes.get.side_effect = Exception("Generic error in get_by_definition")
        with self.assertRaises(Exception) as context:
            NeoDefinition.get_by_definition("error_def")
        self.assertEqual(str(context.exception), "Generic error in get_by_definition")
        self.mock_logger.error.assert_called_once()
        log_msg = self.mock_logger.error.call_args[0][0]
        self.assertIn("Unexpected error while getting definition", log_msg)

    def test_get_term_node_success(self):
        term_node_result = MagicMock()
        self.definition_instance.term.single.return_value = term_node_result
        result = self.definition_instance.get_term_node()
        self.assertEqual(result, term_node_result)
        self.definition_instance.term.single.assert_called_once()

    def test_get_term_node_no_term(self):
        self.definition_instance.term = None
        result = self.definition_instance.get_term_node()
        self.assertIsNone(result)

    def test_get_term_node_exception(self):
        self.definition_instance.term.single.side_effect = exceptions.NeomodelException("Term error")
        with self.assertRaises(exceptions.NeomodelException) as context:
            self.definition_instance.get_term_node()
        self.assertEqual(str(context.exception), "Term error")
        self.mock_logger.error.assert_called_once()
        log_msg = self.mock_logger.error.call_args[0][0]
        self.assertIn("NeoModel-related error while getting term node for definition", log_msg)

    def test_set_relationships_all(self):
        term_node = MagicMock()
        context_node = MagicMock()
        context_description_node = MagicMock()
        collision_node = MagicMock()
        collision_alias_node = MagicMock()
        self.definition_instance.set_relationships(
            term_node=term_node,
            context_node=context_node,
            context_description_node=context_description_node,
            collision=collision_node,
            collision_alias=collision_alias_node
        )
        self.definition_instance.term.connect.assert_called_once_with(term_node)
        self.definition_instance.context.connect.assert_called_once_with(context_node)
        self.definition_instance.context_description.connect.assert_called_once_with(context_description_node)
        self.definition_instance.collision.connect.assert_called_once_with(collision_node)
        self.definition_instance.collision_alias.connect.assert_called_once_with(collision_alias_node)

    def test_set_relationships_partial(self):
        term_node = MagicMock()
        self.definition_instance.set_relationships(term_node=term_node)
        self.definition_instance.term.connect.assert_called_once_with(term_node)
        self.definition_instance.context.connect.assert_not_called()
        self.definition_instance.context_description.connect.assert_not_called()
        self.definition_instance.collision.connect.assert_not_called()
        self.definition_instance.collision_alias.connect.assert_not_called()

    def test_set_relationships_neomodel_exception(self):
        term_node = MagicMock()
        self.definition_instance.term.connect.side_effect = exceptions.NeomodelException("Connect error")
        with self.assertRaises(exceptions.NeomodelException) as context:
            self.definition_instance.set_relationships(term_node=term_node)
        self.assertEqual(str(context.exception), "Connect error")
        self.mock_logger.error.assert_called_once()
        log_msg = self.mock_logger.error.call_args[0][0]
        self.assertIn("NeoModel-related error while connecting relationships for definition", log_msg)

    def test_set_relationships_generic_exception(self):
        term_node = MagicMock()
        self.definition_instance.term.connect.side_effect = Exception("Generic connect error")
        with self.assertRaises(Exception) as context:
            self.definition_instance.set_relationships(term_node=term_node)
        self.assertEqual(str(context.exception), "Generic connect error")
        self.mock_logger.error.assert_called_once()
        log_msg = self.mock_logger.error.call_args[0][0]
        self.assertIn("Unexpected error while connecting relationships for definition", log_msg)
@tag('unit')
class NeoMappingTests(unittest.TestCase):
    def setUp(self):
        self.patcher_save = patch("core.models.NeoMapping.save")
        self.mock_save = self.patcher_save.start()

    def tearDown(self):
        self.patcher_save.stop()
        
    @patch("core.models.NeoMapping.save")
    def test_create_node(self, mock_save):
        lcvid="0x00000001" #should be a hex string
        uid_chain = "0x00000001-0x00000002" #should be a hex string
        lcv_uid="0x00000002" #should be a hex string
        aliases = ["alias1", "alias2"]
        definition="test definition"
        new_neo_mapping = NeoMapping.create_node(uid_chain, lcvid, lcv_uid, definition, aliases)
        self.assertEqual(new_neo_mapping.lcvid, lcvid)
        # self.assertEqual(new_neo_mapping.lcv_downstream_id, lcv_downstream_id)
        self.assertEqual(new_neo_mapping.uid, lcv_uid)
        self.assertEqual(new_neo_mapping.aliases, aliases)
        self.assertEqual(new_neo_mapping.definition, definition)
        self.assertTrue(mock_save.called)

    @patch("core.models.NeoMapping.save", side_effect=exceptions.NeomodelException("Save failed"))
    def test_create_node_exception(self, mock_save):
        with self.assertRaises(exceptions.NeomodelException):
            NeoMapping.create_node("0x00000001", 1, "0x00000002", "test definition")

    @patch.object(NeoMapping, 'nodes', new_callable=MagicMock)
    def test_get_node_success(self, mock_nodes):
        # Simulate a successful lookup.
        dummy_node = MagicMock(spec=NeoMapping)
        mock_nodes.get.return_value = dummy_node
        result = NeoMapping.get_node("chain", "uid")
        self.assertEqual(result, dummy_node)
        mock_nodes.get.assert_called_once_with(uid_chain="chain", uid="uid")

    @patch.object(NeoMapping, 'nodes', new_callable=MagicMock)
    @patch("core.models.logger")
    def test_get_node_does_not_exist(self, mock_logger, mock_nodes):
        # Patch __init__ of exceptions.DoesNotExist to avoid setup errors.
        with patch.object(exceptions.DoesNotExist, '__init__', lambda self, *args, **kwargs: None):
            # Create an instance with a known string representation.
            does_not_exist_exception = exceptions.DoesNotExist("Not found")
            does_not_exist_exception.__str__ = lambda self: "Not found"
            # Simulate nodes.get raising a DoesNotExist exception.
            mock_nodes.get.side_effect = does_not_exist_exception
            with self.assertRaises(exceptions.DoesNotExist) as cm:
                NeoMapping.get_node("chain", "uid")
            mock_logger.error.assert_called_once()
            log_msg = mock_logger.error.call_args[0][0]
            self.assertIn("NeoModel-related error while getting mapping", log_msg)

    @patch.object(NeoMapping, 'nodes', new_callable=MagicMock)
    @patch("core.models.logger")
    def test_get_node_unexpected_exception(self, mock_logger, mock_nodes):
        # Simulate an unexpected exception from the database.
        mock_nodes.get.side_effect = Exception("Unexpected error")
        with self.assertRaises(Exception) as context:
            NeoMapping.get_node("chain", "uid")
        self.assertEqual(str(context.exception), "Unexpected error")
        mock_logger.error.assert_called_once()
        log_msg = mock_logger.error.call_args[0][0]
        self.assertIn("Unexpected error while getting mapping", log_msg)
    
    @patch("core.models.logger")
    def test_set_relationships_success(self, mock_logger):
        # Create a dummy mapping instance and inject mocks.
        mapping = NeoMapping()
        mapping.lcvid = "dummy_lcvid"
        mapping.neoterm_node = MagicMock()
        mapping.save = MagicMock()
        term_node = MagicMock()
        term_node.uid = "term_uid"
        mapping.set_relationships(term_node)
        mapping.neoterm_node.connect.assert_called_once_with(term_node)
        mapping.save.assert_called_once()

    def test_set_relationships_value_error(self):
        mapping = NeoMapping()
        mapping.lcvid = "dummy_lcvid"
        mapping.neoterm_node = MagicMock()
        mapping.save = MagicMock()
        with self.assertRaises(ValueError) as context:
            mapping.set_relationships(None)
        self.assertEqual(str(context.exception), "neoterm_node is None")

    @patch("core.models.logger")
    def test_set_relationships_neomodel_exception(self, mock_logger):
        mapping = NeoMapping()
        mapping.lcvid = "dummy_lcvid"
        mapping.neoterm_node = MagicMock()
        mapping.save = MagicMock()
        term_node = MagicMock()
        term_node.uid = "term_uid"
        # Simulate an exception when connecting.
        mapping.neoterm_node.connect.side_effect = exceptions.NeomodelException("connection error")
        with self.assertRaises(exceptions.NeomodelException) as context:
            mapping.set_relationships(term_node)
        self.assertEqual(str(context.exception), "connection error")
        mock_logger.error.assert_called_once()
        log_msg = mock_logger.error.call_args[0][0]
        self.assertIn("NeoModel-related error while connecting relationships", log_msg)
