import unittest
from unittest.mock import patch, MagicMock
from common.utils import antonyms_in_definition, preprocess_definition
from django.test import tag

@tag('unit')
class UtilsTests(unittest.TestCase):
    def setUp(self):
        self.patcher_tokenize = patch("common.utils.word_tokenize")
        self.mock_tokenize = self.patcher_tokenize.start()

        self.patcher_lemmatizer = patch("common.utils.WordNetLemmatizer")
        self.mock_lemmatizer_class = self.patcher_lemmatizer.start()
        self.mock_lemmatizer_instance = MagicMock()
        self.mock_lemmatizer_instance.lemmatize.side_effect = lambda token: token
        self.mock_lemmatizer_class.return_value = self.mock_lemmatizer_instance

        self.patcher_wn = patch("common.utils.wn", new=MagicMock())
        self.mock_wn = self.patcher_wn.start()

    def tearDown(self):
        patch.stopall()

    def test_antonyms_in_definition_returns_true(self):
        self.mock_tokenize.side_effect = lambda text: text.split()
        fake_synset = MagicMock()
        fake_lemma = MagicMock()
        fake_antonym = MagicMock()
        fake_antonym.name.return_value = "cold"
        fake_synset.lemmas.return_value = [fake_lemma]
        fake_lemma.antonyms.return_value = [fake_antonym]
        self.mock_wn.synsets.return_value = [fake_synset]

        result = antonyms_in_definition("hot", "cold")
        self.assertTrue(result)

    def test_antonyms_in_definition_returns_false(self):
        self.mock_tokenize.side_effect = lambda text: text.split()
        self.mock_wn.synsets.return_value = []

        result = antonyms_in_definition("happy", "joyful")
        self.assertFalse(result)

    def test_preprocess_definition_valid(self):
        input_text = "HeLLo WoRLD!"
        result = preprocess_definition(input_text)
        self.assertEqual(result, input_text.lower())

    def test_preprocess_definition_empty_raises(self):
        with self.assertRaises(ValueError) as context:
            preprocess_definition("")
        self.assertEqual(
            str(context.exception),
            "Invalid input: Definition must be a non-empty string."
        )

    def test_preprocess_definition_non_string_raises(self):
        with self.assertRaises(ValueError) as context:
            preprocess_definition(123)
        self.assertEqual(
            str(context.exception),
            "Invalid input: Definition must be a non-empty string."
        )
