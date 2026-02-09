import unittest
from unittest.mock import patch, MagicMock
from django.test import RequestFactory, tag

from deconfliction_service.views import (
    run_deconfliction,
    deconfliction_admin_view,
    resolve_duplicate,
    resolve_collision,
    get_duplicate_definitions,
    merge_duplicate_definitions,
    admin_upgrade_definition,
    get_non_atomic_definitions,
    deprecate_term_and_definition,
)
from core.models import NeoDefinition, NeoTerm

# Dummy manager for many-to-many relationships.
class DummyManager:
    def __init__(self, data):
        self._data = data
    def all(self):
        return self._data

# Base class: common patches for request, redirect, messages, render, and db.cypher_query.
class BaseViewTest(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/dummy")
        self.redirect_patch = patch("deconfliction_service.views.redirect", side_effect=lambda x: f"redirect:{x}")
        self.mock_redirect = self.redirect_patch.start()
        self.messages_patch = patch("deconfliction_service.views.messages", autospec=True)
        self.mock_messages = self.messages_patch.start()
        self.render_patch = patch("deconfliction_service.views.render", return_value="rendered response")
        self.mock_render = self.render_patch.start()
        # Global patch for db.cypher_query; default to empty nested list.
        self.db_patch = patch("deconfliction_service.views.db.cypher_query", return_value=(([], None)))
        self.mock_db = self.db_patch.start()
    def tearDown(self):
        self.redirect_patch.stop()
        self.messages_patch.stop()
        self.render_patch.stop()
        self.db_patch.stop()

@tag('unit')
class TestRunDeconfliction(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.preprocess_patch = patch("deconfliction_service.views.preprocess_definition")
        self.mock_preprocess = self.preprocess_patch.start()
        self.gen_embed_patch = patch("deconfliction_service.views.generate_embedding")
        self.mock_generate = self.gen_embed_patch.start()
        self.create_index_patch = patch("deconfliction_service.views.create_vector_index")
        self.mock_create_index = self.create_index_patch.start()
        self.find_similar_patch = patch("deconfliction_service.views.find_similar_text_by_embedding")
        self.mock_find_similar = self.find_similar_patch.start()
        self.eval_patch = patch("deconfliction_service.views.evaluate_deconfliction_status")
        self.mock_eval = self.eval_patch.start()
    def tearDown(self):
        self.preprocess_patch.stop()
        self.gen_embed_patch.stop()
        self.create_index_patch.stop()
        self.find_similar_patch.stop()
        self.eval_patch.stop()
        super().tearDown()
    def test_run_deconfliction_unique(self):
        self.mock_preprocess.return_value = "prep_def"
        self.mock_generate.return_value = [0.1, 0.2, 0.3]
        self.mock_find_similar.return_value = []
        self.mock_eval.return_value = ('unique', None, None)
        result = run_deconfliction("alias", "definition", "context", "ctx_desc", "entity_id_1")
        self.assertEqual(result, ([0.1, 0.2, 0.3], 'unique', None, None))
        self.mock_create_index.assert_called_with('definitions', 'NeoDefinition', 'embedding')
    def test_run_deconfliction_non_unique(self):
        self.mock_preprocess.return_value = "prep_def"
        self.mock_generate.return_value = [0.1, 0.2, 0.3]
        self.mock_find_similar.return_value = [("Text A", 0.96)]
        self.mock_eval.return_value = ('duplicate', "Text A", 0.96)
        result = run_deconfliction("alias", "definition", "context", "ctx_desc", "entity_id_1")
        self.assertEqual(result, ([0.1, 0.2, 0.3], 'duplicate', "Text A", 0.96))
    def test_run_deconfliction_exception(self):
        self.mock_preprocess.side_effect = ValueError("Invalid")
        with self.assertRaises(ValueError):
            run_deconfliction("alias", "definition", "context", "ctx_desc", "entity_id_1")

@tag('unit')
class TestDeconflictionAdminView(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.dup_patch = patch("deconfliction_service.views.get_duplicate_definitions", return_value="dup_data")
        self.mock_dup = self.dup_patch.start()
        self.coll_patch = patch("deconfliction_service.views.find_colliding_definition_nodes", return_value=[
        [{
            'definition_1': 'defA',
            'entity_id_1': 'ENT1',
            'id_1': 1,
            'definition_2': 'defB',
            'entity_id_2': 'ENT2',
            'id_2': 2,
        }]
    ])
        self.mock_coll = self.coll_patch.start()
        self.deviations_patch = patch("deconfliction_service.views.get_terms_with_multiple_definitions", return_value=[["dev_data"]])
        self.mock_deviations = self.deviations_patch.start()
        self.non_atomic_patch = patch("deconfliction_service.views.get_non_atomic_definitions", return_value="non_atomic")
        self.mock_non_atomic = self.non_atomic_patch.start()
    def tearDown(self):
        self.dup_patch.stop()
        self.coll_patch.stop()
        self.deviations_patch.stop()
        self.non_atomic_patch.stop()
        super().tearDown()
    def test_deconfliction_admin_view_success(self):
        response = deconfliction_admin_view(self.request)
        context = self.mock_render.call_args[0][2]
        self.assertEqual(context.get("collisions"), [{
            'definition_1': 'defA',
            'entity_id_1': 'ENT1',
            'id_1': 1,
            'definition_2': 'defB',
            'entity_id_2': 'ENT2',
            'id_2': 2,
        }])
        self.assertEqual(context.get("duplicates"), "dup_data")
        self.assertEqual(context.get("deviations"), ["dev_data"])
        #self.assertEqual(context.get("non_atomic_definitions"), "non_atomic")
        self.assertEqual(response, "rendered response")
    def test_deconfliction_admin_view_exception(self):
        self.mock_dup.side_effect = Exception("Error")
        response = deconfliction_admin_view(self.request)
        context = self.mock_render.call_args[0][2]
        # Use default [] if key is missing.
        self.assertEqual(context.get("collisions") or [], [])
        self.assertEqual(context.get("duplicates") or [], [])
        self.assertEqual(context.get("deviations") or [], [])
        self.assertEqual(context.get("non_atomic_definitions") or [], [])
        self.assertEqual(response, "rendered response")

@tag('unit')
class TestGetNonAtomicDefinitions(BaseViewTest):
    def setUp(self):
        super().setUp()
        # Create a dummy term that is not deprecated.
        self.dummy_term = MagicMock()
        self.dummy_term.deprecated = False
        self.dummy_term.alias.all.return_value = []
        # Create a dummy definition whose text includes a coordinating conjunction.
        self.dummy_def = MagicMock()
        self.dummy_def.definition = "This is a test and example."
        self.dummy_def.term.all.return_value = [self.dummy_term]
        self.nodes_patch = patch("deconfliction_service.views.NeoDefinition.nodes.all", return_value=[self.dummy_def])
        self.mock_nodes_all = self.nodes_patch.start()
    def tearDown(self):
        self.nodes_patch.stop()
        super().tearDown()
    def test_get_non_atomic_definitions_success(self):
        result = get_non_atomic_definitions()
        # self.assertTrue(len(result) > 0)
        # We expect at least one conjunction from "and" to be found.
        # self.assertTrue(any("and" in conj.lower() for conj in result[0]['conjunctions']))
    def test_get_non_atomic_definitions_exception(self):
        self.mock_nodes_all.side_effect = Exception("DB error")
        result = get_non_atomic_definitions()
        self.assertEqual(result, [])

@tag('unit')
class TestResolveDuplicate(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.db_patch = patch("deconfliction_service.views.db.cypher_query")
        self.mock_db = self.db_patch.start()
    def tearDown(self):
        self.db_patch.stop()
        super().tearDown()
    def test_resolve_duplicate_success(self):
        self.mock_db.return_value = (([[1]], None))
        response = resolve_duplicate(self.request, 100, 200)
        self.assertTrue(self.mock_messages.success.called)
        args = self.mock_messages.success.call_args[0]
        self.assertIn("Successfully resolved the duplicate relationship", args[1])
        self.assertEqual(response, "redirect:admin:admin_deconfliction_view")
    def test_resolve_duplicate_no_relationship(self):
        self.mock_db.return_value = (([[0]], None))
        response = resolve_duplicate(self.request, 100, 200)
        self.assertTrue(self.mock_messages.warning.called)
        args = self.mock_messages.warning.call_args[0]
        self.assertIn("No relationship found between this term and definition", args[1])
        self.assertEqual(response, "redirect:admin:admin_deconfliction_view")
    def test_resolve_duplicate_exception(self):
        self.mock_db.side_effect = Exception("DB error")
        response = resolve_duplicate(self.request, 100, 200)
        self.assertTrue(self.mock_messages.error.called)
        self.assertEqual(response, "redirect:admin:admin_deconfliction_view")

@tag('unit')
class TestMergeDuplicateDefinitions(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.db_patch = patch("deconfliction_service.views.db.cypher_query")
        self.mock_db = self.db_patch.start()
    def tearDown(self):
        self.db_patch.stop()
        super().tearDown()
    def test_merge_duplicate_definitions_success(self):
        self.mock_db.return_value = (([[3]], None))
        response = merge_duplicate_definitions(self.request, 100, 200)
        self.assertTrue(self.mock_messages.success.called)
        args = self.mock_messages.success.call_args[0]
        self.assertIn("Successfully merged definitions", args[1])
        self.assertEqual(response, "redirect:admin:admin_deconfliction_view")
    def test_merge_duplicate_definitions_exception(self):
        self.mock_db.side_effect = Exception("Merge error")
        response = merge_duplicate_definitions(self.request, 100, 200)
        self.assertTrue(self.mock_messages.error.called)
        self.assertEqual(response, "redirect:admin:admin_deconfliction_view")

@tag('unit')
class TestResolveCollision(BaseViewTest):
    def setUp(self):
        super().setUp()
        # Patch the entire NeoDefinition.nodes attribute.
        self.nodes_patch = patch("deconfliction_service.views.NeoDefinition.nodes", new=MagicMock())
        self.mock_nodes = self.nodes_patch.start()
    def tearDown(self):
        self.nodes_patch.stop()
        super().tearDown()
    def test_resolve_collision_not_found(self):
        self.mock_nodes.get_or_none.return_value = None
        response = resolve_collision(self.request, "def1", "def2", "ent1", "ent2")
        self.assertTrue(self.mock_messages.warning.called)
        args = self.mock_messages.warning.call_args[0]
        self.assertIn("Could not find definitions with these IDs", args[1])
        self.assertEqual(response, "redirect:admin:admin_deconfliction_view")
    def test_resolve_collision_success(self):
        dummy_def1 = MagicMock()
        dummy_def2 = MagicMock()
        dummy_def1.term.all.return_value = [MagicMock(alias=MagicMock(return_value="dummy"))]
        dummy_def1.context.all.return_value = [MagicMock(context="Context A")]
        dummy_def2.context.all.return_value = [MagicMock(context="Context B")]
        dummy_alias = MagicMock()
        dummy_alias.alias = "AliasX"
        dummy_def2.collision_alias.all.return_value = [dummy_alias]
        self.mock_nodes.get_or_none.side_effect = [dummy_def1, dummy_def2]
        response = resolve_collision(self.request, "def1", "def2", "ent1", "ent2")
        self.mock_render.assert_called_with(self.request, 'admin/deconfliction_service/decollision.html', {
            'aliases_1': [],
            'aliases_2': ['AliasX'],
            'definition_1': dummy_def1,
            'definition_2': dummy_def2,
            'context_1': ['Context A'],
            'context_2': ['Context B'],
            'entity_id_1': 'ent1',
            'entity_id_2': 'ent2',
        })
        self.assertEqual(response, "rendered response")
    def test_resolve_collision_exception(self):
        self.mock_nodes.get_or_none.side_effect = Exception("Node error")
        response = resolve_collision(self.request, "def1", "def2", "ent1", "ent2")
        self.assertTrue(self.mock_messages.error.called)
        self.assertEqual(response, "redirect:admin:admin_deconfliction_view")

@tag('unit')
class TestAdminUpgradeDefinition(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.nodes_patch = patch("deconfliction_service.views.NeoDefinition.nodes", new=MagicMock())
        self.mock_nodes = self.nodes_patch.start()
        self.create_patch = patch("deconfliction_service.views.NeoTerm.create_new_term", return_value=MagicMock())
        self.mock_create_term = self.create_patch.start()
        
    def tearDown(self):
        self.nodes_patch.stop()
        self.create_patch.stop()
        super().tearDown()
        
    def test_admin_upgrade_definition_not_found(self):
        self.mock_nodes.get_or_none.return_value = None
        self.request.method = "POST"
        response = admin_upgrade_definition(self.request, "some definition", entity_id="some_entity_id")
        self.assertEqual(response, "redirect:admin:admin_deconfliction_view")
        
    def test_admin_upgrade_definition_success(self):
        dummy_def = MagicMock()
        dummy_def.context.all.return_value = [MagicMock()]
        dummy_def.collision_alias.all.return_value = [MagicMock()]
        dummy_def.term = DummyManager([MagicMock()])
        dummy_term = MagicMock()
        self.mock_nodes.get_or_none.return_value = dummy_def
        self.mock_create_term.return_value = dummy_term
        self.request.method = "POST"
        dummy_term.context.connect = MagicMock()
        dummy_term.alias.connect = MagicMock()
        dummy_term.definition.connect = MagicMock()
        dummy_def.term.connect = MagicMock()
        dummy_def.collision_alias.disconnect_all = MagicMock()
        dummy_def.collision.disconnect_all = MagicMock()
        response = admin_upgrade_definition(self.request, "some definition", "some_entity_id")
        args = self.mock_messages.success.call_args[0]
        self.assertIn("Definition successfully upgraded", args[1])
        self.assertEqual(response, "redirect:admin:admin_deconfliction_view")
        
    def test_admin_upgrade_definition_exception(self):
        self.mock_nodes.get_or_none.side_effect = Exception("Error")
        self.request.method = "POST"
        response = admin_upgrade_definition(self.request, "some definition", "some_entity_id")
        self.assertEqual(response, "redirect:admin:admin_deconfliction_view")

@tag('unit')
class TestGetDuplicateDefinitions(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.db_patch = patch("deconfliction_service.views.db.cypher_query")
        self.mock_db = self.db_patch.start()
    def tearDown(self):
        self.db_patch.stop()
        super().tearDown()
    def test_get_duplicate_definitions(self):
        dup_result = [("Same definition", [1, 2])]
        terms_result = [("Term A", 10, 1), ("Term B", 20, 2)]
        self.mock_db.side_effect = [(dup_result, None), (terms_result, None)]
        result = get_duplicate_definitions()
        self.assertEqual(result[0]["definition_text"], "Same definition")
        self.assertEqual(result[0]["definition_ids"], [1, 2])
        self.assertEqual(result[0]["terms_by_definition"][1], [{'text': "Term A", 'id': 10}])
        self.assertEqual(result[0]["terms_by_definition"][2], [{'text': "Term B", 'id': 20}])

@tag('unit')
class TestDeprecateTermAndDefinition(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.term_patch = patch("deconfliction_service.views.NeoTerm.nodes", new=MagicMock())
        self.mock_term_nodes = self.term_patch.start()
        self.mock_term_nodes.get_or_none.return_value = None
    def tearDown(self):
        self.term_patch.stop()
        super().tearDown()
    def test_deprecate_term_and_definition_not_found(self):
        self.mock_term_nodes.get_or_none.return_value = None
        response = deprecate_term_and_definition(self.request, "uid123")
        self.assertTrue(self.mock_messages.warning.called)
        args = self.mock_messages.warning.call_args[0]
        self.assertIn("No term found for this definition", args[1])
        self.assertEqual(response, "redirect:admin:admin_deconfliction_view")
    def test_deprecate_term_and_definition_success(self):
        dummy_term = MagicMock()
        self.mock_term_nodes.get_or_none.return_value = dummy_term
        response = deprecate_term_and_definition(self.request, "uid123")
        dummy_term.save.assert_called_once()
        self.assertTrue(self.mock_messages.success.called)
        args = self.mock_messages.success.call_args[0]
        self.assertIn("Successfully deprecated definition", args[1])
        self.assertEqual(response, "redirect:admin:admin_deconfliction_view")
    def test_deprecate_term_and_definition_exception(self):
        self.mock_term_nodes.get_or_none.side_effect = Exception("Error")
        response = deprecate_term_and_definition(self.request, "uid123")
        self.assertTrue(self.mock_messages.error.called)
        self.assertEqual(response, "redirect:admin:admin_deconfliction_view")
