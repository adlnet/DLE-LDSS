import io
import json
import unittest
from unittest.mock import patch, Mock, MagicMock
import tempfile
import csv
import os
import requests

from types import SimpleNamespace
from django.test import tag, RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ObjectDoesNotExist, BadRequest
from rest_framework import status

from .test_setup import TestSetUp

from api.views import check_neo4j_status, Instances, DataIngest, INTERNAL_SERVER_ERROR_MESSAGE, upload_csv, TermCreationError, MissingRowsError, MissingColumnsError, create_local_mappings, get_catalog, api_mapped_nodes, check_status, create_mapping_entry, scan_with_clamav_or_400, _run_mapping_generation, run_mapping, generate_local_mappings, _get_definition, _find_best_definition_text


@tag('unit')
class GenerateLocalMappingsTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)
        self.mock_logger = patch("api.views.logger").start()
        self.mock_neo = patch("api.views.NeoTerm").start()

    def test_no_source_terms_returns_404(self):
        self.mock_neo.nodes.filter.return_value = []
        out = generate_local_mappings("src123", "tgt456")
        self.assertEqual(out, {"status": "error", "message": "No matching terms found.", "code": 404})

    def test_success_counts_created(self):
        term1 = MagicMock()
        term1.alias.all.return_value = [SimpleNamespace(alias="s1"), SimpleNamespace(alias="s2")]
        term2 = MagicMock()
        term2.alias.all.return_value = [SimpleNamespace(alias="s3")]
        self.mock_neo.nodes.filter.return_value = [term1, term2]

        def1 = SimpleNamespace(definition="def1", embedding=[0.1])
        def2 = SimpleNamespace(definition="def2", embedding=[0.2])
        patch("api.views._get_definition", side_effect=[def1, def2]).start()
        patch("api.views._find_best_definition_text", side_effect=["best1", "best2"]).start()
        patch("api.views._get_target_term", side_effect=["tgtTerm1", "tgtTerm2"]).start()
        patch("api.views._create_mapping", side_effect=[True, False]).start()

        out = generate_local_mappings("src123", "tgt456")
        self.assertEqual(out, {"status": "success", "message": "Created 1 mappings"})

    def test_unexpected_exception_returns_500(self):
        self.mock_neo.nodes.filter.side_effect = Exception("boom")
        with patch("api.views.INTERNAL_SERVER_ERROR_MESSAGE", new="Internal server error"):
            out = generate_local_mappings("src", "tgt")
        self.assertEqual(out, {"status": "error", "message": "Internal server error", "code": 500})

@tag('unit')
class GetDefinitionTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)
        self.mock_logger = patch("api.views.logger").start()

    def test_returns_node_when_present(self):
        term = MagicMock(uid_chain="u.chain")
        node = MagicMock()
        term.definition.single.return_value = node
        out = _get_definition(term)
        self.assertIs(out, node)

    def test_logs_and_returns_none_when_missing(self):
        term = MagicMock(uid_chain="u.chain")
        term.definition.single.return_value = None
        out = _get_definition(term)
        self.assertIsNone(out)

    def test_logs_and_returns_none_on_exception(self):
        term = MagicMock(uid_chain="u.chain")
        term.definition.single.side_effect = Exception("oops")
        out = _get_definition(term)
        self.assertIsNone(out)


@tag('unit')
class FindBestDefinitionTextTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)
        self.mock_logger = patch("api.views.logger").start()
        self.mock_find = patch("api.views.find_similar_text_by_embedding").start()
        self.mock_ant = patch("api.views.antonyms_in_definition").start()

    def test_returns_none_on_embedding_exception(self):
        self.mock_find.side_effect = Exception("es fail")
        def_node = SimpleNamespace(definition="alpha", embedding=[0.1])
        out = _find_best_definition_text(def_node, "tgtX")
        self.assertIsNone(out)

    def test_returns_none_when_no_candidates_meet_threshold_or_antonym_check(self):
        self.mock_find.return_value = [("t1", 0.79), ("t2", 0.5)]
        self.mock_ant.return_value = False
        def_node = SimpleNamespace(definition="alpha", embedding=[0.1])
        out = _find_best_definition_text(def_node, "tgtX")
        self.assertIsNone(out)

        self.mock_find.return_value = [("t1", 0.85)]
        self.mock_ant.return_value = True
        out = _find_best_definition_text(def_node, "tgtX")
        self.assertIsNone(out)

    def test_picks_highest_scoring_valid_candidate(self):
        self.mock_find.return_value = [("good", 0.82), ("better", 0.91), ("ok", 0.80)]
        self.mock_ant.side_effect = lambda base, cand: False
        def_node = SimpleNamespace(definition="alpha", embedding=[0.2])

        out = _find_best_definition_text(def_node, "tgtY")
        self.assertEqual(out, "better")
        self.mock_find.assert_called_once_with(input_embedding=def_node.embedding, index_name="definitions", entity_id="tgtY")

@tag('unit')
class RunMappingGenerationTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)
        patch("api.views.logger").start()

    @patch("api.views.generate_local_mappings")
    def test_success_with_created_count(self, mock_gen):
        mock_gen.return_value = {"status": "success", "message": "Created 5 mappings"}
        out = _run_mapping_generation("src", "tgt")
        self.assertEqual(out, {"status": "success", "created": 5})

    @patch("api.views.generate_local_mappings")
    def test_success_without_created_keyword(self, mock_gen):
        mock_gen.return_value = {"status": "success", "message": "No new mappings"}
        out = _run_mapping_generation("src", "tgt")
        self.assertEqual(out, {"status": "success", "created": 0})

    @patch("api.views.generate_local_mappings")
    def test_non_success_passthrough(self, mock_gen):
        mock_gen.return_value = {"status": "error", "message": "bad input", "code": 400}
        out = _run_mapping_generation("src", "tgt")
        self.assertEqual(out, {"status": "error", "message": "bad input", "code": 400})

    @patch("api.views.INTERNAL_SERVER_ERROR_MESSAGE", "Internal server error")
    @patch("api.views.generate_local_mappings", side_effect=Exception("boom"))
    def test_exception_returns_500_and_logs(self, mock_gen):
        out = _run_mapping_generation("src", "tgt")
        self.assertEqual(out, {
            "status": "error",
            "message": "Internal server error",
            "code": 500,
        })

@tag('unit')
class ScanWithClamAVTests(unittest.TestCase):
    @patch("api.views.clamd.ClamdNetworkSocket")
    def test_ok_result_rewinds_file(self, mock_socket_cls):
        # Mock clamd client to return an OK result
        mock_client = MagicMock()
        mock_client.instream.return_value = {"stream": ("OK",)}
        mock_socket_cls.return_value = mock_client

        f = io.BytesIO()
        f.write(b"csv contents")  # pointer at end

        scan_with_clamav_or_400(f, host="127.0.0.1", port=3310)

        # File should be rewound
        self.assertEqual(f.tell(), 0)
        mock_socket_cls.assert_called_once_with(host="127.0.0.1", port=3310)
        mock_client.instream.assert_called_once_with(f)

    @patch("api.views.logger")
    @patch("api.views.clamd.ClamdNetworkSocket")
    def test_non_ok_result_raises_badrequest(self, mock_socket_cls, mock_logger):
        # Mock clamd client to return a non-OK result
        mock_client = MagicMock()
        mock_client.instream.return_value = {"stream": ("FOUND", "Eicar-Test-Signature")}
        mock_socket_cls.return_value = mock_client

        f = io.BytesIO(b"bad csv")

        with self.assertRaises(BadRequest):
            scan_with_clamav_or_400(f, host="127.0.0.1", port=3310)

        mock_logger.error.assert_called()  

@tag('unit')
class CreateMappingEntryTests(unittest.TestCase):
    def setUp(self):
        self.source = {"aliases": ["src_alias"], "definition": "src_def"}
        self.target = {"aliases": ["tgt_alias"], "definition": "tgt_def"}

    def test_only_source_term(self):
        entry = create_mapping_entry(self.source, None)
        self.assertIn("source", entry)
        self.assertNotIn("target", entry)
        self.assertNotIn("relationship", entry)
        self.assertEqual(entry["source"], {
            "alias": "src_alias",
            "definition": "src_def"
        })

    def test_only_target_term(self):
        entry = create_mapping_entry(None, self.target)
        self.assertIn("target", entry)
        self.assertNotIn("source", entry)
        self.assertNotIn("relationship", entry)
        self.assertEqual(entry["target"], {
            "alias": "tgt_alias",
            "definition": "tgt_def"
        })

    def test_both_terms(self):
        entry = create_mapping_entry(self.source, self.target)
        self.assertIn("source", entry)
        self.assertIn("target", entry)
        self.assertIn("relationship", entry)
        self.assertTrue(entry["relationship"])

@tag('unit')
class CheckNeo4jStatusTests(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('api.views.db.cypher_query')
    def test_check_neo4j_status_successful(self, mock_cypher_query):
        fake_results = [{'result': 1}]

        fake_meta = {}

        mock_cypher_query.return_value = (fake_results, fake_meta)

        request = self.factory.get('/api/neo4j-health-check/')

        response = check_neo4j_status(request)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data.get('status'), "OK")
        self.assertEqual(data.get('message'), "Connection to Neo4j successful.")

    @patch('api.views.db.cypher_query')
    def test_check_neo4j_status_generic_exception(self, mock_cypher_query):
        mock_cypher_query.side_effect = Exception("Some other error")

        request = self.factory.get('/api/neo4j-health-check/')

        response = check_neo4j_status(request)

        self.assertEqual(response.status_code, 503)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data.get('status'), "ERROR")
        self.assertEqual(data.get('message'), "Neo4j connection failed.")
@tag('unit')
class GetMappingsTests(unittest.TestCase):
    @patch('api.views.db.cypher_query')
    def test_get_valid_results(self, mock_cypher_query):
        mock_cypher_query.return_value = ([{'source': 'source', 'target': 'target'}], {})
@tag('unit')
class InstancesTests(unittest.TestCase):
    def setUp(self,):
        self.instances = Instances()

    def test_get_dict_by_name_found(self):
        expected_jko = {"url": "https://lcv-a.ldss.tla.adlnet.gov/uid/api/terms", "name": "jko"}
        expected_coursera = {"url": "https://lcv-b.ldss.tla.adlnet.gov/uid/api/terms", "name": "coursera"}
        expected_p2881 = {"url": "https://ccv.ldss.tla.adlnet.gov/uid/api/terms", "name": "p2881"}

        self.assertEqual(self.instances.get_dict_by_name("jko"), expected_jko)
        self.assertEqual(self.instances.get_dict_by_name("coursera"), expected_coursera)
        self.assertEqual(self.instances.get_dict_by_name("p2881"), expected_p2881)

    def test_get_dict_by_name_not_found(self):

        self.assertIsNone(self.instances.get_dict_by_name("not_found"))
        self.assertIsNone(self.instances.get_dict_by_name(""))
        self.assertIsNone(self.instances.get_dict_by_name(None))

@tag('unit')
class CheckStatusTests(unittest.TestCase):
    def test_returns_queryset_when_published_exists(self):
        messages = []
        queryset = MagicMock()
        filtered_qs = MagicMock()
        queryset.filter.return_value = filtered_qs
        filtered_qs.__bool__.return_value = True  # make it truthy

        result = check_status(messages, queryset)

        self.assertIs(result, filtered_qs)
        self.assertEqual(messages, [])
        queryset.filter.assert_called_once_with(status="published")

    @patch("api.views.logger")
    def test_raises_when_no_published(self, mock_logger):
        messages = []
        queryset = MagicMock()
        filtered_qs = MagicMock()
        queryset.filter.return_value = filtered_qs
        filtered_qs.__bool__.return_value = False  # make it falsy

        with self.assertRaises(ObjectDoesNotExist):
            check_status(messages, queryset)

        expected_message = (
            "Error fetching record, no published record with required parameters"
        )
        self.assertIn(expected_message, messages)
        mock_logger.error.assert_called_once_with(expected_message)

@tag('unit')
class DataIngestViewTests(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = DataIngest()

    def test_non_post_method_returns_405(self):
        request = self.factory.get('/data-ingest/')
        # Even though we're calling .post(), the view checks request.method
        response = self.view.post(request)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(json.loads(response.content), {
            "error": "Only POST requests are allowed"
        })

    def test_invalid_json_returns_400(self):
        request = self.factory.post(
            '/data-ingest/',
            data='not a json',
            content_type='application/json'
        )
        response = self.view.post(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {
            "error": "Invalid JSON format"
        })

    def test_non_list_json_returns_400(self):
        payload = {"foo": "bar"}
        request = self.factory.post(
            '/data-ingest/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        response = self.view.post(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {
            "error": "Expected a list of objects"
        })

    @patch('api.views.run_mapping')
    def test_missing_required_fields_appends_error_and_skips_run_mapping(self, mock_run_mapping):
        data = [
            # missing uid_chain
            {"definition": "def text", "lcvid": "p1", "uid": "u1"}
        ]
        request = self.factory.post(
            '/data-ingest/',
            data=json.dumps(data),
            content_type='application/json'
        )

        response = self.view.post(request)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            json.loads(response.content),
            {"results": [
                {"uid": "u1", "status": "error", "message": "Missing required fields"}
            ]}
        )
        mock_run_mapping.assert_not_called()

    @patch('api.views.run_mapping')
    def test_run_mapping_successful_item(self, mock_run_mapping):
        expected = {"uid": "u1", "status": "mapped", "foo": "bar"}
        mock_run_mapping.return_value = expected

        data = [{
            "definition": "def text",
            "uid_chain": "chain-123",
            "lcvid": "p1",
            "uid": "u1",
            "aliases": ["alias1", "alias2"]
        }]
        request = self.factory.post(
            '/data-ingest/',
            data=json.dumps(data),
            content_type='application/json'
        )

        response = self.view.post(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"results": [expected]})
        mock_run_mapping.assert_called_once_with(
            "def text", "chain-123", "p1", "u1", ["alias1", "alias2"]
        )

    @patch('api.views.run_mapping')
    def test_run_mapping_raises_exception_appends_error(self, mock_run_mapping):
        mock_run_mapping.side_effect = RuntimeError("boom!")

        item = {
            "definition": "def text",
            "uid_chain": "chain-123",
            "lcvid": "p1",
            "uid": "u1",
            "aliases": []
        }
        request = self.factory.post(
            '/data-ingest/',
            data=json.dumps([item]),
            content_type='application/json'
        )

        response = self.view.post(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            {"results": [
                {"uid": "u1", "status": "error", "message": "Unexpected error while processing this item"}
            ]}
        )
        mock_run_mapping.assert_called_once()

    @patch('api.views.json.loads', side_effect=Exception("unexpected"))
    def test_unexpected_outer_exception_returns_500(self, mock_loads):
        request = self.factory.post(
            '/data-ingest/',
            data='[]',
            content_type='application/json'
        )

        response = self.view.post(request)
        self.assertEqual(response.status_code, 500)

        # don't call json.loads (it's patched) — compare raw bytes instead
        expected_bytes = json.dumps({"error": INTERNAL_SERVER_ERROR_MESSAGE}).encode('utf-8')
        self.assertEqual(response.content, expected_bytes)

@tag('unit')
class UploadCsvTests(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = '/upload-csv/'

    def make_file(self, name='test.csv', content=b'a,b\n1,2'):
        return SimpleUploadedFile(name, content, content_type='text/csv')

    def test_no_file_uploaded(self):

        request = self.factory.post(self.url, data={'entity_id': 'E1'})
        response = upload_csv(request, use_clamav=False)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content),
            {"error": "No file uploaded. Missing field: csv_file"}
        )

    def test_missing_entity_id(self):
        csv_file = self.make_file()
        request = self.factory.post(self.url, data={'csv_file': csv_file}, format='multipart')
        response = upload_csv(request, use_clamav=False)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content),
            {"error": "Missing entity_id in request."}
        )

    def test_invalid_file_type(self):
        bad_file = self.make_file(name='not_csv.txt')
        request = self.factory.post(
            self.url,
            data={'csv_file': bad_file, 'entity_id': 'E1'},
            format='multipart'
        )
        response = upload_csv(request, use_clamav=False)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content),
            {"error": "Invalid file type. Only CSV files are allowed."}
        )

    @patch('api.views.validate_csv_file', side_effect=MissingColumnsError(missing_columns=['c1','c2']))
    def test_missing_columns_error(self, mock_validate):
        csv_file = self.make_file()
        request = self.factory.post(
            self.url,
            data={'csv_file': csv_file, 'entity_id': 'E1'},
            format='multipart'
        )
        response = upload_csv(request, use_clamav=False)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content),
            {"error": "Missing required columns: c1, c2"}
        )

    def test_missing_rows_error(self):
        csv_file = self.make_file()
        # prepare mocks
        df_dummy = object()
        mr = MissingRowsError(missing_rows=[{'row': 42}])
        with patch('api.views.validate_csv_file', return_value={'data_frame': df_dummy}), \
             patch('api.views.create_terms_from_csv', side_effect=mr), \
             patch('api.views.create_missing_row_message', return_value='Row 42 is missing required data'):
            request = self.factory.post(
                self.url,
                data={'csv_file': csv_file, 'entity_id': 'E1'},
                format='multipart'
            )
            response = upload_csv(request, use_clamav=False)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content),
            {"error": "Row 42 is missing required data"}
        )

    @patch('api.views.create_terms_from_csv', side_effect=TermCreationError())
    @patch('api.views.validate_csv_file', return_value={'data_frame': object()})
    def test_term_creation_error(self, mock_validate, mock_create):
        csv_file = self.make_file()
        request = self.factory.post(
            self.url,
            data={'csv_file': csv_file, 'entity_id': 'E1'},
            format='multipart'
        )
        response = upload_csv(request, use_clamav=False)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content),
            {"error": "Error creating terms from CSV file."}
        )

    @patch('api.views.validate_csv_file', side_effect=Exception('boom'))
    def test_unexpected_exception(self, mock_validate):
        csv_file = self.make_file()
        request = self.factory.post(
            self.url,
            data={'csv_file': csv_file, 'entity_id': 'E1'},
            format='multipart'
        )
        response = upload_csv(request, use_clamav=False)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            json.loads(response.content),
            {"error": "Error processing file."}
        )

    @patch('api.views.create_terms_from_csv')
    @patch('api.views.validate_csv_file', return_value={'data_frame': object()})
    def test_successful_upload(self, mock_validate, mock_create):
        csv_file = self.make_file()
        request = self.factory.post(
            self.url,
            data={'csv_file': csv_file, 'entity_id': 'E1'},
            format='multipart'
        )
        response = upload_csv(request, use_clamav=False)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            {"message": "CSV file processed successfully."}
        )
@tag('unit')
class CreateLocalMappingsTests(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = '/create-local-mappings/'

    def make_request(self, body_dict):
        return self.factory.post(
            self.url,
            data=json.dumps(body_dict),
            content_type='application/json'
        )

    @patch('api.views._parse_entity_ids', side_effect=ValueError("Bad JSON"))
    def test_invalid_json_body(self, mock_parse):
        req = self.make_request({'foo': 'bar'})
        response = create_local_mappings(req)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content),
            {"error": "Bad JSON"}
        )

    @patch('api.views._parse_entity_ids', return_value=('S','T'))
    @patch('api.views._run_mapping_generation', return_value={"status":"error","message":"oops","code":418})
    def test_service_error(self, mock_run, mock_parse):
        req = self.make_request({'source':'S','target':'T'})
        response = create_local_mappings(req)
        self.assertEqual(response.status_code, 418)
        self.assertEqual(
            json.loads(response.content),
            {"error": "oops"}
        )

    @patch('api.views._parse_entity_ids', return_value=('X','Y'))
    @patch('api.views._run_mapping_generation', return_value={"status":"success","created":1})
    def test_success_single(self, mock_run, mock_parse):
        req = self.make_request({'source':'X','target':'Y'})
        response = create_local_mappings(req)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            {
                "status": "success",
                "created": 1,
                "message": "Successfully created 1 mapping."
            }
        )

    @patch('api.views._parse_entity_ids', return_value=('A','B'))
    @patch('api.views._run_mapping_generation', return_value={"status":"success","created":5})
    def test_success_plural(self, mock_run, mock_parse):
        req = self.make_request({'source':'A','target':'B'})
        response = create_local_mappings(req)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content),
            {
                "status": "success",
                "created": 5,
                "message": "Successfully created 5 mappings."
            }
        )

@tag('unit')
class GetCatalogTests(TestCase):
    def setUp(self):
        #Gain access to a temp catalog csv
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv', newline='') as tmp:
            self.temp_jko_file = tmp
            self.temp_catalog_jko_file = tmp.name

            # Write sample csv content while the file is still open
            writer = csv.writer(tmp)
            writer.writerow([
                'LearningResourceIdentifier', 'Instance', 'DeliveryMode',
                'LearningResourceName', 'LearningResourceDescription',
                'Duration', 'CatalogURL'
            ])
            writer.writerow([1, 123, 'Test Delivery Mode', 'Test Resource',
                            'Test Description', 0.1, 'https://jko.test.mil'])
            writer.writerow([2, 456, 'Test Delivery Mode', 'Test Resource',
                            'Test Description', 0.1, 'https://jko.test.mil'])
            tmp.flush()

        # Simulate what would be returned from the API as JSON
        self.mock_catalog_data = {
            "entity_id": "jko",
            "data": [
                {
                    'id': '1',
                    'LearningResourceIdentifier': '1',
                    'Instance': '123',
                    'DeliveryMode': 'Test Delivery Mode',
                    'LearningResourceName': 'Test Resource',
                    'LearningResourceDescription': 'Test Description',
                    'Duration': '0.1',
                    'CatalogURL': 'https://jko.test.mil'
                },
                {
                    'id': '2',
                    'LearningResourceIdentifier': '2',
                    'Instance': '456',
                    'DeliveryMode': 'Test Delivery Mode',
                    'LearningResourceName': 'Test Resource',
                    'LearningResourceDescription': 'Test Description',
                    'Duration': '0.1',
                    'CatalogURL': 'https://jko.test.mil'
                }
            ]
        }
    
    def tearDown(self):
        os.unlink(self.temp_catalog_jko_file)

    def test_get_catalog_no_xia(self):
        xia_data = get_catalog('test')
        self.assertEqual(xia_data, {})
    
    @patch('api.views.requests.get')
    @patch('api.views.logging.getLogger')
    def test_get_catalog_wrong_endpoint(self, mock_get_logger, mock_get):
        # Create mock logger
        mock_logger = mock_get_logger.return_value
        
        # Simulate an exception when requests.get is called
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        with patch('api.views.XIA_URLS', ['https://xia-jko.ldss.tla.adlnet.gov']), \
            patch('api.views.XIA_CATALOG_PATH', '/api/catalog'):
             
            result = get_catalog('jko')

        self.assertIn("_errors", result)
        self.assertIsInstance(result["_errors"], list)
        self.assertTrue(any("Oops! Bad Request" in msg for msg in result["_errors"]))

        expected_url = 'https://xia-jko.ldss.tla.adlnet.gov/api/catalog'
        mock_get.assert_called_once_with(expected_url, timeout=10)
        
    @patch('api.views.requests.get')
    @patch('api.views.XIA_URLS', ['https://xia-jko.ldss.tla.adlnet.gov'])
    @patch('api.views.XIA_CATALOG_PATH', '/api/catalog')
    def test_get_catalog(self, mock_requests_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_catalog_data
        mock_requests_get.return_value = mock_response

        result = get_catalog('jko')

        expected_url = 'https://xia-jko.ldss.tla.adlnet.gov/api/catalog'
        mock_requests_get.assert_called_once_with(expected_url, timeout=10)

        self.assertIn("jko", result)
        self.assertEqual(len(result["jko"]), 2)
        self.assertEqual(result["jko"][0]["Instance"], '123')
    
    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_api_get_catalog_wrong_params(self):
        url = reverse('api:catalog-all')
        response = self.client.get(url, data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), "You must include 'provider' query argument")

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_api_get_catalog_none(self):
        with patch('api.views.get_catalog', return_value={}):
            url = reverse('api:catalog-all')
            response = self.client.get(url, data={"provider": "jko"})
            self.assertEqual(response.status_code, 404)
            self.assertJSONEqual(
                response.content, {"error": "No catalogs found for the specified provider."}
            )
    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_api_get_catalog_entry_wrong_params(self):
        url = reverse('api:catalog-entry')
        response = self.client.get(url, data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), "You must include 'provider' and 'course_id' query arguments")
        
    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_api_get_catalog_entry_not_found(self):
        with patch('api.views.get_catalog', return_value={}):
            url = reverse('api:catalog-entry')
            response = self.client.get(url, data={"provider": "jko", "course_id": '789'})
            self.assertEqual(response.status_code, 404)
            self.assertJSONEqual(
                response.content, {"error": "Catalog entry not found"}
            )

    # def test_api_get_catalog_entry_found(self):
    #     with patch('api.views.get_catalog', return_value=self.mock_catalog_data):
    #         url = reverse('api:catalog-entry')
    #         response = self.client.get(url, data={"provider": "jko", "course_id": '1'})
    #         self.assertEqual(response.status_code, 200)
    #         self.assertJSONEqual(
    #             response.content, 
    #             {   
    #                 'id': '1',
    #                 'LearningResourceIdentifier': '1',
    #                 'Instance': '123',
    #                 'DeliveryMode': 'Test Delivery Mode',
    #                 'LearningResourceName': 'Test Resource',
    #                 'LearningResourceDescription': 'Test Description',
    #                 'Duration': '0.1',
    #                 'CatalogURL': 'https://jko.test.mil'
    #             }
    #         )

@tag('unit')
class TestApiMappedNodes(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('api.views.get_terms_for_instance', return_value=[])
    def test_no_terms_returns_404(self, mock_get_terms):
        request = self.factory.get(
            '/api/mapped-nodes',
            {'source': 'SRC', 'target': 'TGT'}
        )

        response = api_mapped_nodes(request)

        # status and content-type
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = json.loads(response.content)
        self.assertEqual(
            data,
            {"error": "No terms found for the given source or target."}
        )
