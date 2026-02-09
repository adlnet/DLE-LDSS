import json
import unittest
from unittest.mock import patch, MagicMock
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.test import tag, RequestFactory, TestCase
from uid.views import db

from uid.views import (
    generate_uid_node,
    # create_provider,
    generate_report,
    report_generated_uids,
    api_generate_uid,
    UIDRepoViewSet,
    api_terms,
    api_terms_slim,
    fetch_slim_terms
)

# pylint: disable=protected-access

# Helper: set the request body (HttpRequest.body is read-only)
def set_request_body(request, body_bytes):
    request._body = body_bytes
    type(request).body = property(lambda self: self._body)

# Dummy type for NeoTerm so that isinstance(neoterm, NeoTerm) passes.
class DummyNeoTerm:
    pass

# When we need an instance, we subclass DummyNeoTerm.
class DummyNeoTermInstance(DummyNeoTerm):
    pass
@tag('unit')
class TestUIDViews(unittest.TestCase):
    def setUp(self):
        # Patch built-in time.sleep.
        self.sleep_patch = patch("time.sleep", return_value=None)
        self.mock_sleep = self.sleep_patch.start()
        # Patch db and GeneratedUIDLog.objects in uid.views.
        self.db_patch = patch("uid.views.db")
        self.mock_db = self.db_patch.start()
        self.genuidlog_patch = patch("uid.views.GeneratedUIDLog.objects")
        self.mock_genuidlog = self.genuidlog_patch.start()
        # Patch NeoTerm in uid.views with our dummy type.
        self.neo_patch = patch("uid.views.NeoTerm", new=DummyNeoTerm)
        self.neo_patch.start()

        self.factory = RequestFactory()

    def tearDown(self):
        patch.stopall()

    def test_generate_uid_node(self):
        dummy_request = HttpRequest()
        dummy_request.method = "POST"
        payload = {"parent_uid": "dummy_parent"}
        set_request_body(dummy_request, json.dumps(payload).encode("utf-8"))
        fake_node = MagicMock()
        fake_node.uid = "0x12345678"
        with patch("uid.views.UIDNode.create_node", return_value=fake_node) as mock_create:
            response = generate_uid_node(dummy_request)
            self.assertIsInstance(response, HttpResponse)
            self.assertIn("0x12345678", response.content.decode())
            mock_create.assert_called_with("dummy_parent")

    # def test_create_provider_get(self):
    #     dummy_request = HttpRequest()
    #     dummy_request.method = "GET"
    #     fake_form = MagicMock()
    #     fake_response = MagicMock(spec=HttpResponse)
    #     with patch("uid.views.ProviderForm", return_value=fake_form):
    #         with patch("uid.views.render", return_value=fake_response) as mock_render:
                
    #             response = create_provider(dummy_request)
    #             mock_render.assert_called_with(dummy_request, "create_provider.html", {"form": fake_form})
    #             self.assertEqual(response, fake_response)

    # def test_create_provider_post_valid(self):
    #     dummy_request = HttpRequest()
    #     dummy_request.method = "POST"
    #     dummy_request.POST = {"name": "TestProvider"}
    #     fake_provider = MagicMock()
    #     fake_provider.save = MagicMock()
    #     fake_form = MagicMock()
    #     fake_form.is_valid.return_value = True
    #     fake_form.save.return_value = fake_provider
    #     with patch("uid.views.ProviderForm", return_value=fake_form):
    #         fake_redirect = MagicMock(spec=HttpResponse)
    #         with patch("uid.views.redirect", return_value=fake_redirect) as mock_redirect:
    #             response = create_provider(dummy_request)
    #             fake_form.is_valid.assert_called_once()
    #             fake_form.save.assert_called_once()
    #             fake_provider.save.assert_called()  # Called in view.
    #             mock_redirect.assert_called_with("uid:success")
    #             self.assertEqual(response, fake_redirect)

    def test_generate_report_root(self):
        dummy_request = HttpRequest()
        dummy_request.method = "GET"
        with patch("uid.views.report_all_uids", return_value=["uid1", "uid2"]) as mock_report:
            response = generate_report(dummy_request, "root")
            data = json.loads(response.content.decode())
            self.assertEqual(data, {"uids": ["uid1", "uid2"]})
            mock_report.assert_called_once()

    def test_generate_report_non_root(self):
        dummy_request = HttpRequest()
        dummy_request.method = "GET"
        with patch("uid.views.report_uids_by_echelon", return_value=["uidA", "uidB"]) as mock_report:
            response = generate_report(dummy_request, "level2")
            data = json.loads(response.content.decode())
            self.assertEqual(data, {"uids": ["uidA", "uidB"]})
            mock_report.assert_called_once_with("level2")

    def test_UIDRepoViewSet_list(self):
        fake_log1 = MagicMock()
        fake_log1.uid = "uid1"
        fake_log1.generated_at = "2025-01-01"
        fake_log1.generator_id = "gen1"
        fake_log2 = MagicMock()
        fake_log2.uid = "uid2"
        fake_log2.generated_at = "2025-01-02"
        fake_log2.generator_id = "gen2"
        self.mock_genuidlog.all.return_value = [fake_log1, fake_log2]
        viewset = UIDRepoViewSet()
        dummy_request = HttpRequest()
        # Patch Response (from rest_framework.response) so that it returns an HttpResponse directly.
        with patch("uid.views.Response", new=lambda data, **kwargs: HttpResponse(json.dumps(data), content_type="application/json", status=200)):
            response = viewset.list(dummy_request)
            # Our patched Response returns an HttpResponse, so we don't need to call render().
            data = json.loads(response.content.decode())
            expected = [
                {"uid": "uid1", "generated_at": "2025-01-01", "generator_id": "gen1"},
                {"uid": "uid2", "generated_at": "2025-01-02", "generator_id": "gen2"},
            ]
            self.assertEqual(data, expected)

    def test_report_generated_uids_get(self):
        dummy_request = HttpRequest()
        dummy_request.method = "GET"
        with patch("uid.views.report_all_generated_uids", return_value=[{"uid": "uidX"}]) as mock_report:
            response = report_generated_uids(dummy_request)
            data = json.loads(response.content.decode())
            self.assertEqual(data, [{"uid": "uidX"}])
            mock_report.assert_called_once()

    def test_api_generate_uid_method_not_post(self):
        dummy_request = HttpRequest()
        dummy_request.method = "GET"
        response = api_generate_uid(dummy_request)
        self.assertIsInstance(response, HttpResponse)
        self.assertIn("", response.content.decode())

    def test_api_generate_uid_missing_provider(self):
        dummy_request = HttpRequest()
        dummy_request.method = "POST"
        payload = {}
        set_request_body(dummy_request, json.dumps(payload).encode("utf-8"))
        response = api_generate_uid(dummy_request)
        data = json.loads(response.content.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn("must specify a 'provider_name'", data["message"])

    def test_api_generate_uid_invalid_provider_type(self):
        dummy_request = HttpRequest()
        dummy_request.method = "POST"
        payload = {"provider_name": 123}
        set_request_body(dummy_request, json.dumps(payload).encode("utf-8"))
        response = api_generate_uid(dummy_request)
        data = json.loads(response.content.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn("must be a string", data["message"])

    def test_api_generate_uid_provider_too_long(self):
        dummy_request = HttpRequest()
        dummy_request.method = "POST"
        payload = {"provider_name": "x" * 100}
        set_request_body(dummy_request, json.dumps(payload).encode("utf-8"))
        response = api_generate_uid(dummy_request)
        data = json.loads(response.content.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn("less than 100 characters", data["message"])

    def test_api_generate_uid_bulk_invalid_type(self):
        dummy_request = HttpRequest()
        dummy_request.method = "POST"
        payload = {"provider_name": "prov", "bulk": "not_an_int"}
        set_request_body(dummy_request, json.dumps(payload).encode("utf-8"))
        response = api_generate_uid(dummy_request)
        data = json.loads(response.content.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn("bulk", data["message"])

    def test_api_generate_uid_bulk_out_of_range(self):
        for bulk in [0, 101]:
            dummy_request = HttpRequest()
            dummy_request.method = "POST"
            payload = {"provider_name": "prov", "bulk": bulk}
            set_request_body(dummy_request, json.dumps(payload).encode("utf-8"))
            response = api_generate_uid(dummy_request)
            self.assertEqual(response.status_code, 400)

    def test_api_generate_uid_single_valid(self):
        dummy_request = HttpRequest()
        dummy_request.method = "POST"
        payload = {"provider_name": "prov"}
        set_request_body(dummy_request, json.dumps(payload).encode("utf-8"))
        fake_req = MagicMock()
        fake_req.token = "token1"
        fake_req.default_uid = "uid1"
        fake_req.default_uid_chain = "chain1"
        # Patch the correct target from the models.
        with patch("uid.models.UIDRequestNode.create_requested_uid", return_value=fake_req) as mock_create:
            response = api_generate_uid(dummy_request)
            data = json.loads(response.content.decode())
            self.assertEqual(data, {"token": "token1", "uid": "uid1", "uid_chain": "chain1"})
            mock_create.assert_called_once_with("prov")

    # def test_UIDTermViewSet_list(self):
    #     fake_term_data = ["term1", "term2"]
    #     with patch("uid.views.report_all_term_uids", return_value=fake_term_data) as mock_report:
    #         viewset = UIDTermViewSet()
    #         dummy_request = HttpRequest()
    #         # Patch JsonResponse so that it directly wraps our data.
    #         with patch("uid.views.JsonResponse", new=lambda data, **kwargs: HttpResponse(data, content_type="application/json", status=200)):
    #             response = viewset.list(dummy_request)
    #             data = json.loads(response.content.decode())
    #             self.assertEqual(data, fake_term_data)
    #             mock_report.assert_called_once()

    def test_api_terms_empty(self):
        dummy_request = HttpRequest()
        dummy_request.method = "GET"
        with patch("uid.views.NeoTerm") as mock_neoterm:
            mock_neoterm.nodes.all.return_value = []
            with patch("uid.views.messages.error") as mock_messages:
                response = api_terms(dummy_request)
                data = json.loads(response.content.decode())
                self.assertEqual(data, [])
                self.assertEqual(response.status_code, 200)
                mock_messages.assert_called_once_with(dummy_request, "There is no data to export.")

    def test_api_terms_with_data(self):
        # Create a fake NeoTerm instance as an instance of DummyNeoTerm.
        class FakeNeoTermInstance(DummyNeoTerm):
            pass
        dummy_neoterm = FakeNeoTermInstance()
        dummy_neoterm.uid = "term_uid"
        dummy_neoterm.uid_chain = "chain1"
        dummy_neoterm.term = "SampleTerm"
        alias = MagicMock()
        alias.alias = "alias1"
        dummy_neoterm.alias = MagicMock()
        dummy_neoterm.alias.all.return_value = [alias]
        definition = MagicMock()
        definition.definition = "def1"
        dummy_neoterm.definition = MagicMock()
        dummy_neoterm.definition.all.return_value = [definition]
        context_obj = MagicMock()
        context_obj.context = "context1"
        context_desc = MagicMock()
        context_desc.context_description = "desc1"
        context_obj.context_description = MagicMock()
        context_obj.context_description.all.return_value = [context_desc]
        dummy_neoterm.context = MagicMock()
        dummy_neoterm.context.all.return_value = [context_obj]
        with patch("uid.views.NeoTerm") as mock_neoterm:
            mock_neoterm.nodes.all.return_value = [dummy_neoterm]
            dummy_request = HttpRequest()
            dummy_request.method = "GET"
            response = api_terms(dummy_request)
            data = json.loads(response.content.decode())
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 1)
            term = data[0]
            self.assertEqual(term["uid"], "term_uid")
            self.assertEqual(term["uid_chain"], "chain1")
            self.assertEqual(term["term"], "SampleTerm")
            self.assertEqual(term["aliases"], ["alias1"])
            self.assertEqual(term["definition"], "def1")
            self.assertEqual(term["contexts"][0]["context"], "context1")
            self.assertEqual(term["contexts"][0]["context_description"], "desc1")

    # def test_api_terms_slim(self):
    #     fake_results = [("ctx_val", "def_val", "chain_val", "alias_val")]
    #     self.mock_db.cypher_query.return_value = (fake_results, None)
    #     dummy_request = HttpRequest()
    #     dummy_request.method = "GET"
    #     response = api_terms_slim(dummy_request)
    #     data = json.loads(response.content.decode())
    #     self.assertIsInstance(data, list)
    #     self.assertEqual(len(data), 1)
    #     output_item = data[0]
    #     self.assertEqual(output_item["contexts"]["context"], "ctx_val")
    #     self.assertEqual(output_item["contexts"]["contextDescription"], "ctx_val")
    #     self.assertEqual(output_item["definition"], "def_val")
    #     self.assertEqual(output_item["uid_chain"], "chain_val")
    #     self.assertEqual(output_item["aliases"], ["alias_val"])
    #     self.mock_db.cypher_query.assert_called_once()
@tag('unit')
class TestSlimTerms(unittest.TestCase):
    def setUp(self):
        patcher = patch('uid.views.db')
        self.mock_db = patcher.start()
        self.addCleanup(patcher.stop)

    def test_fetch_slim_terms(self):
        fake_results = [("ctx_val", "def_val", "chain_val", "alias_val")]
        self.mock_db.cypher_query.return_value = (fake_results, None)

        output = fetch_slim_terms("PREFIX")

        self.assertIsInstance(output, list)
        self.assertEqual(len(output), 1)

        item = output[0]
        self.assertEqual(item["contexts"]["context"], "ctx_val")
        self.assertEqual(item["contexts"]["contextDescription"], "ctx_val")
        self.assertEqual(item["definition"], "def_val")
        self.assertEqual(item["uid_chain"], "chain_val")
        self.assertEqual(item["aliases"], ["alias_val"])

        self.mock_db.cypher_query.assert_called_once()
        args, kwargs = self.mock_db.cypher_query.call_args
        self.assertIn("MATCH (term:NeoTerm)", args[0])
        # self.assertEqual(kwargs['params'], {"prefix": "PREFIX"})

    def test_api_terms_slim_success(self):
        fake_results = [("ctx_val", "def_val", "chain_val", "alias_val")]
        self.mock_db.cypher_query.return_value = (fake_results, None)

        request = HttpRequest()
        request.method = "GET"
        request.GET = {"prefix": "PRE"}

        response = api_terms_slim(request)
        data = json.loads(response.content.decode())

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="terms.json"')

        out = data[0]
        self.assertEqual(out["contexts"]["context"], "ctx_val")
        self.assertEqual(out["contexts"]["contextDescription"], "ctx_val")
        self.assertEqual(out["definition"], "def_val")
        self.assertEqual(out["uid_chain"], "chain_val")
        self.assertEqual(out["aliases"], ["alias_val"])

        self.mock_db.cypher_query.assert_called_once()

    def test_api_terms_slim_no_prefix(self):
        request = HttpRequest()
        request.method = "GET"
        request.GET = {}

        response = api_terms_slim(request)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode())
        self.assertEqual(data, [])

    @patch('uid.views.fetch_slim_terms', side_effect=RuntimeError("DB down"))
    def test_api_terms_slim_internal_error(self, mock_fetch):
        request = HttpRequest()
        request.method = "GET"
        request.GET = {"prefix": "X"}
        response = api_terms_slim(request)
        self.assertEqual(response.status_code, 500)
        err = json.loads(response.content.decode())
        self.assertEqual(err, {"error": "Internal error fetching terms"})
        