import unittest
from unittest import mock
from django.test import tag
import os
import sys
import tempfile
import shutil

from common.model_loader import reassemble_chunked_files, initialize_models, get_semantic_model

sys.modules['sentence_transformers'] = mock.MagicMock()
sys.modules['nltk'] = mock.MagicMock()

@tag('unit')
class ModelLoaderTestCase(unittest.TestCase):
    """Test case for the common.model_loader module functions."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

        self.init_patcher = mock.patch('common.model_loader._initialized', False)
        self.sem_model_patcher = mock.patch('common.model_loader._semantic_model', None)
        self.init_patcher.start()
        self.sem_model_patcher.start()

        self.os_patcher = mock.patch('common.model_loader.os')
        self.mock_os = self.os_patcher.start()
        self.re_patcher = mock.patch('common.model_loader.re')
        self.mock_re = self.re_patcher.start()
        self.nltk_patcher = mock.patch('common.model_loader.nltk')
        self.mock_nltk = self.nltk_patcher.start()
        self.st_patcher = mock.patch('common.model_loader.SentenceTransformer')
        self.mock_st = self.st_patcher.start()

        self.settings_patcher = mock.patch('common.model_loader.settings')
        self.mock_settings = self.settings_patcher.start()

        self.mock_os.path.abspath.return_value = '/mock/root/dir'
        self.mock_os.path.dirname.return_value = '/mock/dir'
        self.mock_os.path.join.side_effect = os.path.join
        self.mock_os.path.isdir.return_value = True
        self.mock_os.path.isfile.return_value = True

        mock_pattern = mock.MagicMock()
        self.mock_re.compile.return_value = mock_pattern

    def tearDown(self):
        """Clean up after each test."""
        shutil.rmtree(self.temp_dir)
        mock.patch.stopall()

    def test_reassemble_chunked_files_with_no_chunks(self):
        self.mock_os.listdir.return_value = ['file1.txt', 'file2.pdf']
        mock_regex = self.mock_re.compile.return_value
        mock_regex.match.return_value = None

        reassemble_chunked_files(self.temp_dir, os.path.dirname(self.temp_dir))

        self.mock_os.listdir.assert_called_once_with(self.temp_dir)
        mock_regex.match.assert_any_call('file1.txt')
        mock_regex.match.assert_any_call('file2.pdf')
        self.mock_os.remove.assert_not_called()

    def test_reassemble_chunked_files_with_chunks(self):
        self.mock_os.listdir.return_value = ['file.txt.part1', 'file.txt.part2', 'other.pdf']
        mock_regex = self.mock_re.compile.return_value
        match1 = mock.MagicMock()
        match1.group.side_effect = lambda n: 'file.txt' if n==1 else '1'
        match2 = mock.MagicMock()
        match2.group.side_effect = lambda n: 'file.txt' if n==1 else '2'
        mock_regex.match.side_effect = lambda fname: match1 if 'part1' in fname else (match2 if 'part2' in fname else None)

        mock_out = mock.mock_open()
        mock_part = mock.mock_open(read_data=b'data')
        def open_side_effect(path, mode='rb'):
            return mock_part() if 'part' in path else mock_out()
        with mock.patch('builtins.open', side_effect=open_side_effect):
            reassemble_chunked_files(self.temp_dir, os.path.dirname(self.temp_dir))

        self.assertTrue(mock_out().write.called)
        self.mock_os.remove.assert_called()

    def test_initialize_models_already_initialized(self):
        with mock.patch('common.model_loader._initialized', True):
            initialize_models()
            self.mock_os.makedirs.assert_not_called()
            self.mock_st.assert_not_called()

    # def test_initialize_models_with_user_path(self):
    #     self.mock_settings.SEMANTIC_MODEL_PATH = '/user/path'
    #     self.mock_os.path.isdir.return_value = True
    #     self.mock_os.listdir.return_value = ['config.json']
    #     self.mock_os.path.isfile.side_effect = lambda p: p.endswith('config.json')
    #     fake_model = mock.MagicMock(name='fake_model')
    #     self.mock_st.return_value = fake_model
    #     result = initialize_models()
    #     self.mock_os.makedirs.assert_called_once_with('/user/path', exist_ok=True)
    #     self.mock_st.assert_called_once_with('/user/path')
    #     self.mock_nltk.data.path.append.assert_called_once_with(
    #         self.mock_settings.NLTK_DATA_PATH
    #     )
    #     self.assertIs(result, fake_model)

    def test_initialize_models_default_path(self):
        self.mock_settings.SEMANTIC_MODEL_PATH = None
        self.mock_os.path.isfile.side_effect = lambda p: 'config.json' in p
        self.mock_os.listdir.return_value = ['config.json']
        mock_model = mock.MagicMock()
        self.mock_st.return_value = mock_model

        initialize_models()

        expected = os.path.join('/mock/root/dir', 'models', 'all-mpnet-base-v2')
        self.mock_st.assert_called_once_with(expected)

    def test_initialize_models_with_chunks(self):
        self.mock_settings.SEMANTIC_MODEL_PATH = None
        self.mock_os.path.isfile.side_effect = lambda p: 'config.json' in p
        self.mock_os.listdir.return_value = ['model.bin.part1', 'model.bin.part2', 'config.json']
        mock_reass = mock.patch('common.model_loader.reassemble_chunked_files').start()
        mock_model = mock.MagicMock() 
        self.mock_st.return_value = mock_model

        initialize_models()

        mock_reass.assert_called_once()
        self.mock_st.assert_called()

    def test_initialize_models_no_model_found(self):
        self.mock_settings.SEMANTIC_MODEL_PATH = None
        self.mock_os.path.isfile.return_value = False
        self.mock_os.listdir.return_value = []
        with self.assertRaises(FileNotFoundError):
            initialize_models()

    def test_get_semantic_model_not_initialized(self):
        mock_model = mock.MagicMock()
        with mock.patch('common.model_loader._initialized', False), \
             mock.patch('common.model_loader._semantic_model', mock_model) as sem_mod, \
             mock.patch('common.model_loader.initialize_models') as init_mod:
            result = get_semantic_model()
        init_mod.assert_called_once()
        self.assertEqual(result, mock_model)

    def test_get_semantic_model_initialized(self):
        mock_model = mock.MagicMock()
        with mock.patch('common.model_loader._initialized', True), \
             mock.patch('common.model_loader.initialize_models') as init_mod, \
             mock.patch('common.model_loader._semantic_model', mock_model):
            result = get_semantic_model()
        init_mod.assert_not_called()
        self.assertEqual(result, mock_model)
