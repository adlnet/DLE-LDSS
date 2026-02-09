import unittest
from unittest.mock import patch, MagicMock
from django.core.exceptions import ValidationError
from django.test import tag

# Import the functions to test from your module.
from deconfliction_service.node_utils import (
    generate_embedding,
    get_terms_with_multiple_definitions,
    show_current_vector_indeces,
    create_vector_index,
    find_similar_text_by_embedding,
    # find_similar_text_by_node_field,
    find_colliding_definition_nodes,
    evaluate_deconfliction_status,
    is_duplicate,
    is_collision,
    is_unique,
)

# ------------------------
# Test for generate_embedding
# ------------------------
@tag('unit')
class TestGenerateEmbedding(unittest.TestCase):
    def setUp(self):
        patcher = patch("deconfliction_service.node_utils.get_semantic_model")
        self.mock_get_semantic_model = patcher.start()
        self.addCleanup(patcher.stop)
        # Create a fake semantic model with an encode method.
        self.fake_semantic_model = MagicMock()
        # encode returns an object with tolist() method.
        fake_embedding = [0.1, 0.2, 0.3]
        self.fake_semantic_model.encode.return_value.tolist.return_value = fake_embedding
        self.mock_get_semantic_model.return_value = self.fake_semantic_model

    def tearDown(self):
        pass

    def test_generate_embedding_valid(self):
        text = "This is a test."
        result = generate_embedding(text)
        self.assertEqual(result, [0.1, 0.2, 0.3])
        self.fake_semantic_model.encode.assert_called_with(text, normalize_embeddings=True)

    def test_generate_embedding_invalid_input(self):
        with self.assertRaises(ValueError):
            generate_embedding("")  # empty string should raise ValueError
        with self.assertRaises(ValueError):
            generate_embedding(123)  # non-string input

    def test_generate_embedding_unexpected_exception(self):
        # Simulate an exception during encoding.
        self.fake_semantic_model.encode.side_effect = Exception("Encoding error")
        with self.assertRaises(RuntimeError) as context:
            generate_embedding("sample")
        self.assertIn("Failed to generate embedding", str(context.exception))

# ------------------------
# Test for get_terms_with_multiple_definitions
# ------------------------
@tag('unit')
class TestGetTermsWithMultipleDefinitions(unittest.TestCase):
    def setUp(self):
        patcher = patch("deconfliction_service.node_utils.db.cypher_query")
        self.mock_cypher_query = patcher.start()
        self.addCleanup(patcher.stop)
        # Prepare a fake return value: (results, None)
        self.fake_results = [{"term_uid": "uid123", "count": 2}]
        self.mock_cypher_query.return_value = (self.fake_results, None)

    def tearDown(self):
        pass

    def test_get_terms_with_multiple_definitions(self):
        results = get_terms_with_multiple_definitions()
        self.mock_cypher_query.assert_called()
        self.assertEqual(results, self.fake_results)

# ------------------------
# Test for show_current_vector_indeces
# ------------------------
@tag('unit')
class TestShowCurrentVectorIndeces(unittest.TestCase):
    def setUp(self):
        patcher = patch("deconfliction_service.node_utils.db.cypher_query")
        self.mock_cypher_query = patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        pass

    def test_show_current_vector_indeces_success(self):
        # Simply call the function and assert that db.cypher_query was called.
        show_current_vector_indeces()
        self.mock_cypher_query.assert_called()

    def test_show_current_vector_indeces_exception(self):
        self.mock_cypher_query.side_effect = Exception("DB error")
        with self.assertRaises(Exception):
            show_current_vector_indeces()

# ------------------------
# Test for create_vector_index
# ------------------------
@tag('unit')
class TestCreateVectorIndex(unittest.TestCase):
    def setUp(self):
        patcher_db = patch("deconfliction_service.node_utils.db.cypher_query")
        self.mock_cypher_query = patcher_db.start()
        self.addCleanup(patcher_db.stop)
        # Also patch show_current_vector_indeces to avoid its real call.
        patcher_show = patch("deconfliction_service.node_utils.show_current_vector_indeces")
        self.mock_show_current = patcher_show.start()
        self.addCleanup(patcher_show.stop)

    def tearDown(self):
        pass

    def test_create_vector_index_success(self):
        # Simulate a successful creation.
        self.mock_cypher_query.return_value = (["result"], None)
        create_vector_index("test_index", "NeoTerm")
        # Ensure cypher_query and show_current_vector_indeces were called.
        self.mock_cypher_query.assert_called()
        self.mock_show_current.assert_called()

    def test_create_vector_index_exception(self):
        self.mock_cypher_query.side_effect = Exception("Create error")
        with self.assertRaises(Exception):
            create_vector_index("test_index", "NeoTerm")

# ------------------------
# Test for find_similar_text_by_embedding
# ------------------------
@tag('unit')
class TestFindSimilarTextByEmbedding(unittest.TestCase):
    def setUp(self):
        patcher = patch("deconfliction_service.node_utils.db.cypher_query")
        self.mock_cypher_query = patcher.start()
        self.addCleanup(patcher.stop)
        self.fake_results = [("Text A", 0.98), ("Text B", 0.85)]
        self.mock_cypher_query.return_value = (self.fake_results, None)

    def tearDown(self):
        pass

    def test_find_similar_text_by_embedding_valid(self):
        input_embedding = [0.1, 0.2, 0.3]
        result = find_similar_text_by_embedding(input_embedding, "term", "test_id")
        self.assertEqual(result, self.fake_results)

    def test_find_similar_text_by_embedding_no_results(self):
        self.mock_cypher_query.return_value = ([], None)
        input_embedding = [0.1, 0.2, 0.3]
        result = find_similar_text_by_embedding(input_embedding, "term", "test_id")
        self.assertEqual(result, [])

    def test_find_similar_text_by_embedding_invalid_input(self):
        # Input embedding is not a list of numbers.
        result = find_similar_text_by_embedding("invalid", "term", "test_id")
        self.assertIn("error", result)
        self.assertIn("Invalid input_embedding", result["error"])

    def test_find_similar_text_by_embedding_unexpected_exception(self):
        self.mock_cypher_query.side_effect = Exception("DB error")
        input_embedding = [0.1, 0.2, 0.3]
        result = find_similar_text_by_embedding(input_embedding, "term", "test_id")
        self.assertIn("error", result)
        self.assertIn("Unexpected error occurred", result["error"])

# # ------------------------
# # Test for find_similar_text_by_node_field
# # ------------------------
# @tag('unit')
# class TestFindSimilarTextByNodeField(unittest.TestCase):
#     def setUp(self):
#         patcher = patch("deconfliction_service.node_utils.db.cypher_query")
#         self.mock_cypher_query = patcher.start()
#         self.addCleanup(patcher.stop)
#         self.fake_results = [("Text A", 0.90), ("Text B", 0.80)]
#         self.mock_cypher_query.return_value = (self.fake_results, None)

#     def tearDown(self):
#         pass

#     def test_find_similar_text_by_node_field(self):
#         result = find_similar_text_by_node_field("NeoTerm", "embedding", "term", "test_index")
#         self.mock_cypher_query.assert_called()
#         self.assertEqual(result, self.fake_results)

# ------------------------
# Test for find_colliding_definition_nodes
# ------------------------
@tag('unit')
class TestFindCollidingDefinitionNodes(unittest.TestCase):
    def setUp(self):
        patcher = patch("deconfliction_service.node_utils.db.cypher_query")
        self.mock_cypher_query = patcher.start()
        self.addCleanup(patcher.stop)
        self.fake_results = [{"collision": {"definition_1": "A", "id_1": 1, "definition_2": "B", "id_2": 2}}]
        self.mock_cypher_query.return_value = (self.fake_results, None)

    def tearDown(self):
        pass

    def test_find_colliding_definition_nodes(self):
        result = find_colliding_definition_nodes()
        self.mock_cypher_query.assert_called()
        self.assertEqual(result, self.fake_results)

# ------------------------
# Test for evaluate_deconfliction_status and related helpers
# ------------------------
@tag('unit')
class TestEvaluateDeconflictionStatus(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_evaluate_empty_results(self):
        result = evaluate_deconfliction_status([])
        self.assertEqual(result, ('unique', None, None))

    def test_evaluate_unique(self):
        # Highest score below 0.83.
        similarity_results = [("Text A", 0.80), ("Text B", 0.75)]
        result = evaluate_deconfliction_status(similarity_results)
        self.assertEqual(result, ('unique', None, None))

    def test_evaluate_duplicate(self):
        # Highest score >= 0.95.
        similarity_results = [("Text A", 0.96), ("Text B", 0.90)]
        result = evaluate_deconfliction_status(similarity_results)
        self.assertEqual(result[0], 'duplicate')
        self.assertEqual(result[1], "Text A")
        self.assertEqual(result[2], 0.96)

    def test_evaluate_collision(self):
        # Highest score between 0.83 and 0.92.
        similarity_results = [("Text A", 0.88), ("Text B", 0.80)]
        result = evaluate_deconfliction_status(similarity_results)
        self.assertEqual(result[0], 'collision')
        self.assertEqual(result[1], "Text A")
        self.assertEqual(result[2], 0.88)

@tag('unit')
class TestHelperFunctions(unittest.TestCase):
    def test_is_duplicate(self):
        self.assertTrue(is_duplicate(0.95))
        self.assertFalse(is_duplicate(0.94))

    def test_is_collision(self):
        self.assertTrue(is_collision(0.90))
        self.assertFalse(is_collision(0.95))
        self.assertFalse(is_collision(0.80))

    def test_is_unique(self):
        self.assertTrue(is_unique(0.80))
        self.assertFalse(is_unique(0.85))
        