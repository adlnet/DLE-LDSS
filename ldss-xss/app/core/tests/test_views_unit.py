import csv
import json 
from io import StringIO
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.test import RequestFactory, tag
from django.contrib.messages.storage.fallback import FallbackStorage
from unittest.mock import patch, MagicMock
import unittest

from core.views import (
    export_terms_as_csv,
    export_terms_as_json,
    execute_neo4j_query,
    search,
)
from core.models import NeoTerm

def add_session_and_messages(request):
    from django.contrib.sessions.middleware import SessionMiddleware
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    request.session.save()
    setattr(request, '_messages', FallbackStorage(request))
    return request

@tag('unit')
class ExportTermsAsCsvTests(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.db_patch = patch('core.views.db.cypher_query')
        self.mock_cypher_query = self.db_patch.start()
    def tearDown(self):
        self.db_patch.stop()
    def test_export_csv_no_data(self):
        self.mock_cypher_query.return_value = ([(0,)], None)
        request = add_session_and_messages(self.factory.get('/export/csv'))
        request.META['HTTP_REFERER'] = '/previous-page/'
        response = export_terms_as_csv(request)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, '/previous-page/')
    def test_export_csv_success(self):
        count_result = ([(1,)], None)
        data_result = ([("uid123", "lcvid456", ["alias1", "alias2"], ["def1", "def2"], "Context A", "Context Desc")], None)
        self.mock_cypher_query.side_effect = [count_result, data_result]
        request = add_session_and_messages(self.factory.get('/export/csv'))
        response = export_terms_as_csv(request)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="terms_export.csv"')
        content = response.content.decode('utf-8')
        reader = csv.reader(StringIO(content))
        rows = list(reader)
        self.assertEqual(rows[0], ['UID', 'Parent ID', 'Aliases', 'Definitions', 'Context', 'Context Description'])
        self.assertEqual(rows[1][0], "uid123")
        self.assertEqual(rows[1][1], "lcvid456")
        self.assertEqual(rows[1][2], "alias1; alias2")
        self.assertEqual(rows[1][3], "def1; def2")
        self.assertEqual(rows[1][4], "Context A")
        self.assertEqual(rows[1][5], "Context Desc")

@tag('unit')
class ExportTermsAsJsonTests(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
    @patch('core.views.NeoTerm')
    def test_export_json_no_nodes(self, mock_NeoTerm):
        mock_NeoTerm.nodes.all.return_value = []
        request = add_session_and_messages(self.factory.get('/export/json'))
        request.META['HTTP_REFERER'] = '/prev/'
        response = export_terms_as_json(request)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, '/prev/')
    @patch('core.views.NeoTerm')
    def test_export_json_success(self, mock_NeoTerm):
        dummy_term = MagicMock()
        dummy_term.uid = "uid123"
        dummy_term.uid_chain = "chain123"
        dummy_term.term = "Test Term"
        dummy_alias = MagicMock() 
        dummy_alias.alias = "alias1"
        dummy_definition = MagicMock()
        dummy_definition.definition = "def1"
        dummy_context = MagicMock()
        dummy_context.context = "Context A"
        dummy_context_desc = MagicMock()
        dummy_context_desc.context_description = "Desc A"
        dummy_context.context_description.all.return_value = [dummy_context_desc]
        dummy_term.alias.all.return_value = [dummy_alias]
        dummy_term.definition.all.return_value = [dummy_definition]
        dummy_term.context.all.return_value = [dummy_context]
        mock_NeoTerm.nodes.all.return_value = [dummy_term]
        request = add_session_and_messages(self.factory.get('/export/json'))
        response = export_terms_as_json(request)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="terms.json"')
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 1)
        term_data = data[0]
        self.assertEqual(term_data['uid'], "uid123")
        self.assertEqual(term_data['uid_chain'], "chain123")
        self.assertEqual(term_data['term'], "Test Term")
        self.assertEqual(term_data['aliases'], ["alias1"])
        self.assertEqual(term_data.get('definition'), "def1")
        self.assertEqual(len(term_data['contexts']), 1)
        self.assertEqual(term_data['contexts'][0]['context'], "Context A")
        self.assertEqual(term_data['contexts'][0]['context_description'], "Desc A")

@tag('unit')
class ExecuteNeo4jQueryTests(unittest.TestCase):
    def setUp(self):
        self.query = "MATCH (n) RETURN n"
        self.params = {"search_term": "test"}
    @patch('core.views.db.cypher_query')
    def test_execute_query_success(self, mock_cypher_query):
        dummy_results = [("result1",)]
        mock_cypher_query.return_value = (dummy_results, None)
        results = execute_neo4j_query(self.query, self.params)
        self.assertEqual(results, dummy_results)
    @patch('core.views.db.cypher_query')
    def test_execute_query_failure(self, mock_cypher_query):
        mock_cypher_query.side_effect = Exception("DB error")
        results = execute_neo4j_query(self.query, self.params)
        self.assertIsNone(results)

@tag('unit')
class SearchViewTests(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.render_patch = patch('core.views.render')
        self.mock_render = self.render_patch.start()
        self.mock_render.return_value = HttpResponse("rendered")
    def tearDown(self):
        self.render_patch.stop()
    def test_search_get(self):
        request = add_session_and_messages(self.factory.get('/search'))
        search(request)
        args, _ = self.mock_render.call_args
        context = args[2]
        self.assertIn('form', context)
        self.assertIn('results', context)
        self.assertEqual(context['results'], [])
    @patch('core.views.execute_neo4j_query')
    def test_search_get_valid(self, mock_execute_query):
        # Use GET data instead of POST data
        get_data = {'search_term': 'test', 'search_type': 'alias'}
        request = add_session_and_messages(self.factory.get('/search', data=get_data))
        dummy_raw_results = [
            ("LCVID1", "alias1", "def1", "Context A"),
            ("LCVID2", "alias2", "def2", "Context B")
        ]
        mock_execute_query.return_value = dummy_raw_results
        search(request)
        # Ensure render was called and unpack its arguments correctly
        args, kwargs = self.mock_render.call_args
        context = args[2]
        self.assertIn('results', context)
        self.assertIn('data', context['results'])
        self.assertEqual(len(context['results']['data']), 2)

    def test_search_get_invalid_form(self):
        # Use GET with empty data to simulate an invalid form
        get_data = {}
        request = add_session_and_messages(self.factory.get('/search', data=get_data))
        search(request)
        args, kwargs = self.mock_render.call_args
        context = args[2]
        # When no GET data is provided, the view returns an empty results list
        self.assertEqual(context.get('results', []), [])
