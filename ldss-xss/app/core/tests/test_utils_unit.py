from unittest.mock import patch, MagicMock
import unittest

from core.utils import run_node_creation, run_unique_definition_creation, run_duplicate_definition_creation, run_collision_definition_creation, run_mapping, find_most_similar_text, is_sane_utf8
from core.models import NeoAlias, NeoContext, NeoContextDescription, NeoDefinition, NeoMapping, NeoTerm
# from ddt import data, ddt, unpack
from django.test import tag

# from ..management.utils.signals_utils import (create_child_termset,
#                                               create_terms, term_object,
#                                               termset_object, update_status)
# from ..management.utils.xss_helper import bleach_data_to_json, sort_version
# from ..models import ChildTermSet, TermSet
# from .test_setup import TestSetUp


# @tag('unit')
# @ddt
# class UtilsTests(TestSetUp):

    # def test_create_child_termset(self):
    #     """Test function creating child termsets"""
    #     self.termset.save()
    #     termset_name = 'test1'
    #     termset = TermSet.objects.get(name=self.schema_name)
    #     return_val = create_child_termset(termset_name, termset,
    #                                       self.status, self.user)

    #     self.assertEqual(return_val.parent_term_set, termset)
    #     self.assertEqual(return_val.name, termset_name)
    #     self.assertEqual(return_val.status, self.status)

    # def test_create_terms(self):
    #     """Test function to create/save terms"""
    #     self.termset.save()
    #     termset = TermSet.objects.get(name=self.schema_name)
    #     return_val = create_terms(self.metadata["test"]["test1"], "test1",
    #                               termset, self.status, self.user)

    #     self.assertEqual(return_val.term_set, termset)
    #     self.assertEqual(return_val.name, "test1")
    #     self.assertEqual(return_val.use, "Required")
    #     self.assertEqual(return_val.type, "int")

    # @data(({'key': {'key1': {'key2': 'val'}}}, {'key1': {'key2': 'val'}}))
    # @unpack
    # def test_save_metadata(self, data1, data2):
    #     """Test Function to flatten/normalize data dictionary"""
    #     with patch('core.management.utils.signals_utils.'
    #                'create_child_termset') as mock_create_child_termset, \
    #             patch('core.management.utils.signals_utils.'
    #                   'termset_object') as mock_termset_object, \
    #             patch('core.management.utils.'
    #                   'signals_utils.term_object') as mock_term_object:
    #         termset_object(data1, self.schema_iri, self.status, self.user)

    #         self.assertEqual(mock_create_child_termset.call_count, 1)
    #         self.assertEqual(mock_termset_object.call_count, 1)

    #         termset_object(data2, self.schema_iri, self.status, self.user)

    #         self.assertEqual(mock_term_object.call_count, 1)

    # def test_term_object(self):
    #     """Test function to update flattened object to dict variable"""
    #     with patch('core.management.utils.signals_utils.'
    #                'create_terms') as mock_create_terms:
    #         term_object('term_obj', 'term_name', 'parent_iri',
    #                     'status', self.user)
    #         self.assertEqual(mock_create_terms.call_count, 1)

    # def test_update_status(self):
    #     """Test function to update the status of children terms/termsets"""
    #     self.schema.save()
    #     termset = TermSet.objects.get(name='test_name')
    #     update_status(termset, "Retired", self.user)
    #     child_termset = ChildTermSet.objects.get(parent_term_set=termset)

    #     self.assertEqual(child_termset.status, "Retired")

    # def test_sort_version(self):
    #     """Test function to sort TermSets by version"""
    #     one = TermSet(name="one", version="1.1.1")
    #     two = TermSet(name="two", version="2.2.2")
    #     three = TermSet(name="three", version="2.2.3")
    #     ts_list = [one, three, two]

    #     sort_version(ts_list, reverse_order=True)
    #     self.assertEqual(ts_list, [three, two, one])

    #     sort_version(ts_list)
    #     self.assertEqual(ts_list, [one, two, three])

    # def test_bleach(self):
    #     """Test function to bleach dicts"""
    #     html = "<em>test</em></br>string"
    #     clean = "teststring"

    #     bad_dict = {'outer': {'inner': html}}
    #     clean_dict = {'outer': {'inner': clean}}

    #     returned_dict = bleach_data_to_json(bad_dict)

    #     self.assertEqual(returned_dict, bad_dict)
    #     self.assertDictEqual(clean_dict, returned_dict)

@tag('unit')
class CoreUtilsTests(unittest.TestCase):
    def setUp(self):
        # Patch the external dependencies as imported in core.utils:
        self.patcher_run_deconfliction = patch("core.utils.run_deconfliction")
        self.mock_run_deconfliction = self.patcher_run_deconfliction.start()

        self.patcher_generate_embedding = patch("core.utils.generate_embedding")
        self.mock_generate_embedding = self.patcher_generate_embedding.start()

        self.patcher_find_similar = patch("core.utils.find_similar_text_by_embedding")
        self.mock_find_similar = self.patcher_find_similar.start()

        self.patcher_antonyms = patch("core.utils.antonyms_in_definition")
        self.mock_antonyms = self.patcher_antonyms.start()

        self.patcher_preprocess = patch("core.utils.preprocess_definition")
        self.mock_preprocess = self.patcher_preprocess.start()

        # Patch the model class methods to avoid database interactions:
        self.patcher_NeoAlias_get_or_create = patch.object(NeoAlias, "get_or_create", return_value=(MagicMock(), True))
        self.mock_NeoAlias_get_or_create = self.patcher_NeoAlias_get_or_create.start()

        self.patcher_NeoDefinition_get_or_create = patch.object(NeoDefinition, "get_or_create", return_value=(MagicMock(), True))
        self.mock_NeoDefinition_get_or_create = self.patcher_NeoDefinition_get_or_create.start()

        self.patcher_NeoContext_get_or_create = patch.object(NeoContext, "get_or_create", return_value=(MagicMock(), True))
        self.mock_NeoContext_get_or_create = self.patcher_NeoContext_get_or_create.start()

        self.patcher_NeoContextDescription_get_or_create = patch.object(NeoContextDescription, "get_or_create", return_value=(MagicMock(), True))
        self.mock_NeoContextDescription_get_or_create = self.patcher_NeoContextDescription_get_or_create.start()

        self.patcher_NeoMapping_create_node = patch.object(NeoMapping, "create_node", return_value=MagicMock())
        self.mock_NeoMapping_create_node = self.patcher_NeoMapping_create_node.start()

        self.patcher_get_term_node = patch.object(NeoDefinition, "get_term_node", return_value=MagicMock())
        self.mock_get_term_node = self.patcher_get_term_node.start()

        self.patcher_NeoTerm_create_new_term = patch.object(NeoTerm, "create_new_term", return_value=MagicMock())
        self.mock_NeoTerm_create_new_term = self.patcher_NeoTerm_create_new_term.start()

        # Patch the internal functions and logger in core.utils:
        self.patcher_run_unique_definition_creation = patch("core.utils.run_unique_definition_creation")
        self.mock_run_unique_definition_creation = self.patcher_run_unique_definition_creation.start()

        self.patcher_run_duplicate_definition_creation = patch("core.utils.run_duplicate_definition_creation")
        self.mock_run_duplicate_definition_creation = self.patcher_run_duplicate_definition_creation.start()

        self.patcher_run_collision_definition_creation = patch("core.utils.run_collision_definition_creation")
        self.mock_run_collision_definition_creation = self.patcher_run_collision_definition_creation.start()

        self.patcher_logger = patch("core.utils.logger")
        self.mock_logger = self.patcher_logger.start()

    def tearDown(self):
        self.patcher_run_deconfliction.stop()
        self.patcher_generate_embedding.stop()
        self.patcher_find_similar.stop()
        self.patcher_antonyms.stop()
        self.patcher_preprocess.stop()
        self.patcher_NeoAlias_get_or_create.stop()
        self.patcher_NeoDefinition_get_or_create.stop()
        self.patcher_NeoContext_get_or_create.stop()
        self.patcher_NeoContextDescription_get_or_create.stop()
        self.patcher_NeoMapping_create_node.stop()
        self.patcher_get_term_node.stop()
        self.patcher_NeoTerm_create_new_term.stop()
        self.patcher_run_unique_definition_creation.stop()
        self.patcher_run_duplicate_definition_creation.stop()
        self.patcher_run_collision_definition_creation.stop()
        self.patcher_logger.stop()

    def test_run_node_creation_unique(self):
        # Simulate run_deconfliction returning a "unique" scenario.
        self.mock_run_deconfliction.return_value = ("dummy_embedding", "unique", "irrelevant", 0.0)
        run_node_creation("def1", "context1", "contextdesc1", alias="alias1", entity_id="entity_id")
        self.mock_run_unique_definition_creation.assert_called_once_with(
            definition="def1", context="context1", context_description="contextdesc1",
            definition_embedding="dummy_embedding", alias="alias1", entity_id="entity_id"
        )

    def test_run_node_creation_duplicate(self):
        self.mock_run_deconfliction.return_value = ("dummy_embedding", "duplicate", "most_similar_text", 0.0)
        run_node_creation("def1", "context1", "contextdesc1", alias="alias1", entity_id="entity_id")
        self.mock_run_duplicate_definition_creation.assert_called_once_with(
            alias="alias1", definition="most_similar_text", context="context1", context_description="contextdesc1", entity_id="entity_id"
        )

    def test_run_node_creation_collision(self):
        self.mock_run_deconfliction.return_value = ("dummy_embedding", "collision", "most_similar_text", 0.95)
        run_node_creation("def1", "context1", "contextdesc1", alias="alias1", entity_id="entity_id")
        self.mock_run_collision_definition_creation.assert_called_once_with(
            "alias1", "most_similar_text", "def1", "context1", "contextdesc1", "dummy_embedding", entity_id="entity_id"
        )

    def test_run_unique_definition_creation_success(self):
        dummy_term = MagicMock()
        dummy_alias = MagicMock()
        dummy_definition = MagicMock()
        dummy_context = MagicMock()
        dummy_context_desc = MagicMock()
        # Set up the specific return values for these model calls:
        self.mock_NeoTerm_create_new_term.return_value = dummy_term
        self.mock_NeoAlias_get_or_create.return_value = (dummy_alias, True)
        self.mock_NeoDefinition_get_or_create.return_value = (dummy_definition, True)
        self.mock_NeoContext_get_or_create.return_value = (dummy_context, True)
        self.mock_NeoContextDescription_get_or_create.return_value = (dummy_context_desc, True)
        run_unique_definition_creation("def1", "context1", "contextdesc1", "dummy_embedding", alias="alias1", entity_id="entity_id_1")
        dummy_term.set_relationships.assert_called_once_with(
            alias_node=dummy_alias, definition_node=dummy_definition, context_node=dummy_context
        )
        dummy_context.set_relationships.assert_called_once_with(
            term_node=dummy_term, alias_node=dummy_alias, definition_node=dummy_definition, context_description_node=dummy_context_desc
        )
        dummy_definition.set_relationships.assert_called_once_with(
            term_node=dummy_term, context_node=dummy_context, context_description_node=dummy_context_desc
        )
        dummy_context_desc.set_relationships.assert_called_once_with(
            definition_node=dummy_definition, context_node=dummy_context
        )
        dummy_alias.set_relationships.assert_called_once_with(
            term_node=dummy_term, context_node=dummy_context
        )

    def test_run_duplicate_definition_creation_collision(self):
        dummy_alias = MagicMock()
        dummy_context = MagicMock()
        dummy_context_desc = MagicMock()
        dummy_definition = MagicMock()
        dummy_definition.get_term_node.return_value = None
        self.mock_NeoAlias_get_or_create.return_value = (dummy_alias, True)
        self.mock_NeoContext_get_or_create.return_value = (dummy_context, True)
        self.mock_NeoContextDescription_get_or_create.return_value = (dummy_context_desc, True)
        self.mock_NeoDefinition_get_or_create.return_value = (dummy_definition, True)
        run_duplicate_definition_creation(alias="alias1", definition="def_dup", context="context1", context_description="contextdesc1", entity_id="entity_id_1")
        dummy_alias.set_relationships.assert_called()
        dummy_context.set_relationships.assert_called()
        dummy_definition.set_relationships.assert_called()
        dummy_context_desc.set_relationships.assert_called()

    def test_run_duplicate_definition_creation_unique(self):
        dummy_alias = MagicMock()
        dummy_context = MagicMock()
        dummy_context_desc = MagicMock()
        dummy_definition = MagicMock()
        dummy_term = MagicMock()
        dummy_definition.get_term_node.return_value = dummy_term
        self.mock_NeoAlias_get_or_create.return_value = (dummy_alias, True)
        self.mock_NeoContext_get_or_create.return_value = (dummy_context, True)
        self.mock_NeoContextDescription_get_or_create.return_value = (dummy_context_desc, True)
        self.mock_NeoDefinition_get_or_create.return_value = (dummy_definition, True)
        run_duplicate_definition_creation(alias="alias1", definition="def_dup", context="context1", context_description="contextdesc1", entity_id="entity_id_1")
        dummy_term.set_relationships.assert_called_once_with(
            alias_node=dummy_alias, definition_node=dummy_definition
        )
        dummy_context.set_relationships.assert_called_once_with(
            term_node=dummy_term, alias_node=dummy_alias, definition_node=dummy_definition, context_description_node=dummy_context_desc
        )
        dummy_definition.set_relationships.assert_called_once_with(
            term_node=dummy_term, context_node=dummy_context, context_description_node=dummy_context_desc
        )
        dummy_context_desc.set_relationships.assert_called_once_with(
            definition_node=dummy_definition, context_node=dummy_context
        )
        dummy_alias.set_relationships.assert_called()

    def test_run_collision_definition_creation_success(self):
        dummy_alias = MagicMock()
        dummy_existing_definition = MagicMock()
        dummy_colliding_definition = MagicMock()
        dummy_context = MagicMock()
        dummy_context_desc = MagicMock()
        self.mock_NeoAlias_get_or_create.return_value = (dummy_alias, True)
        # Simulate two separate calls: one for the existing definition and one for the colliding definition.
        self.mock_NeoDefinition_get_or_create.side_effect = [
            (dummy_existing_definition, True),
            (dummy_colliding_definition, True)
        ]
        self.mock_NeoContext_get_or_create.return_value = (dummy_context, True)
        self.mock_NeoContextDescription_get_or_create.return_value = (dummy_context_desc, True)
        run_collision_definition_creation("alias1", "most_similar_def", "def1", "context1", "contextdesc1", "dummy_embedding", entity_id="entity_id")
        dummy_alias.set_relationships.assert_called_once_with(
            context_node=dummy_context, collided_definition=dummy_colliding_definition
        )
        dummy_context.set_relationships.assert_called_once_with(
            context_description_node=dummy_context_desc, definition_node=dummy_colliding_definition
        )
        dummy_context_desc.set_relationships.assert_called_once_with(
            definition_node=dummy_colliding_definition
        )
        dummy_colliding_definition.set_relationships.assert_called_once_with(
            context_node=dummy_context, context_description_node=dummy_context_desc,
            collision_alias=dummy_alias, collision=dummy_existing_definition
        )

    def test_run_mapping_no_match(self):
        self.mock_preprocess.return_value = "preprocessed_def"
        self.mock_generate_embedding.return_value = "dummy_embedding"
        self.mock_find_similar.return_value = []
        result = run_mapping("def1", "uid_chain1", "lcvid1", "uid1", ["alias1"])
        self.assertEqual(result["status"], "no_match")
        self.assertEqual(result["message"], "No similar definition found")

    def test_run_mapping_success(self):
        self.mock_preprocess.return_value = "preprocessed_def"
        self.mock_generate_embedding.return_value = "dummy_embedding"
        self.mock_find_similar.return_value = [("similar_def", 0.85)]
        self.mock_antonyms.return_value = False

        dummy_definition = MagicMock()
        dummy_term = MagicMock()
        dummy_definition.get_term_node.return_value = dummy_term

        # Patch get_by_definition in core.utils to avoid DB access.
        with patch("core.utils.NeoDefinition.get_by_definition", return_value=dummy_definition):
            dummy_mapping = MagicMock()
            self.mock_NeoMapping_create_node.return_value = dummy_mapping
            result = run_mapping("def1", "uid_chain1", "lcvid1", "uid1", ["alias1"])
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["mapped_definition"], "similar_def")
            dummy_mapping.set_relationships.assert_called_once_with(term_node=dummy_term)

    def test_run_mapping_term_missing(self):
        self.mock_preprocess.return_value = "preprocessed_def"
        self.mock_generate_embedding.return_value = "dummy_embedding"
        self.mock_find_similar.return_value = [("similar_def", 0.85)]
        self.mock_antonyms.return_value = False

        dummy_definition = MagicMock()
        dummy_definition.get_term_node.return_value = None

        with patch("core.utils.NeoDefinition.get_by_definition", return_value=dummy_definition):
            result = run_mapping("def1", "uid_chain1", "lcvid1", "uid1", ["alias1"])
            self.assertEqual(result["status"], "error")
            self.assertIn("Term node missing", result["message"])

    def test_run_mapping_definition_node_not_found(self):
        self.mock_preprocess.return_value = "preprocessed_def"
        self.mock_generate_embedding.return_value = "dummy_embedding"
        self.mock_find_similar.return_value = [("similar_def", 0.85)]
        self.mock_antonyms.return_value = False

        with patch("core.utils.NeoDefinition.get_by_definition", return_value=None):
            result = run_mapping("def1", "uid_chain1", "lcvid1", "uid1", ["alias1"])
            self.assertEqual(result["status"], "error")
            self.assertIn("Definition node not found", result["message"])

    def test_find_most_similar_text_none(self):
        result = find_most_similar_text([])
        self.assertIsNone(result)

    def test_find_most_similar_text_success(self):
        similarity_results = [("text1", 0.80), ("text2", 0.90), ("text3", 0.85)]
        result = find_most_similar_text(similarity_results)
        self.assertEqual(result, "text2")

    def test_find_most_similar_text_below_threshold(self):
        similarity_results = [("text1", 0.80), ("text2", 0.70)]
        result = find_most_similar_text(similarity_results)
        self.assertIsNone(result)

    def test_are_foreign_chars_allowed(self):

        valid_strings = [
            "こんにちは、世界！私はAIです。"
            "¡Hola! ¿Cómo estás? Estoy bien, gracias.",
            "Tôi tên là Trí. Rất vui được gặp bạn!",
            "Привет, как дела? Всё хорошо.",
            "안녕하세요. 만나서 반갑습니다!",
            "नमस्ते, आप कैसे हैं?",
        ]

        for valid_string in valid_strings:
            self.assertIs(True, is_sane_utf8(valid_string))

    def test_are_stupid_chars_rejected(self):

        invalid_strings = [
            "\x00hi there\x01",
            "h⃞    i⃞     t⃞    h⃞    e⃞    r⃞    e⃞"
        ]

        for invalid_string in invalid_strings:
            self.assertIs(False, is_sane_utf8(invalid_string))
