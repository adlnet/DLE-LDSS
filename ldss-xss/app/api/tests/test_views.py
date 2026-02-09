import pytest
import json
from unittest.mock import patch, MagicMock
from django.http import JsonResponse
from api import views

# Import the functions to test

@pytest.fixture(autouse=True)
def patch_strip_bad_characters_and_is_sane_utf8(monkeypatch):
    # Patch strip_bad_characters to return the input string unchanged
    monkeypatch.setattr(views, "strip_bad_characters", lambda s: s)
    # Patch is_sane_utf8 to always return True
    monkeypatch.setattr(views, "is_sane_utf8", lambda s: True)

def test__parse_entity_ids_valid(monkeypatch):
    body = json.dumps({"source": "abc", "target": "def"}).encode()
    result = views._parse_entity_ids(body)
    assert result == ("abc", "def")

def test__parse_entity_ids_missing_source(monkeypatch):
    body = json.dumps({"target": "def"}).encode()
    with pytest.raises(ValueError) as excinfo:
        views._parse_entity_ids(body)
    assert "Both 'source' and 'target' fields are required." in str(excinfo.value)

def test__parse_entity_ids_missing_target(monkeypatch):
    body = json.dumps({"source": "abc"}).encode()
    with pytest.raises(ValueError) as excinfo:
        views._parse_entity_ids(body)
    assert "Both 'source' and 'target' fields are required." in str(excinfo.value)

def test__parse_entity_ids_invalid_json(monkeypatch):
    body = b"{not valid json}"
    with pytest.raises(ValueError) as excinfo:
        views._parse_entity_ids(body)
    assert "Invalid JSON format." in str(excinfo.value)

def test__parse_entity_ids_invalid_type(monkeypatch):
    body = json.dumps({"source": 123, "target": "def"}).encode()
    with pytest.raises(ValueError) as excinfo:
        views._parse_entity_ids(body)
    assert "Both 'source' and 'target' fields are required." in str(excinfo.value)

def test__parse_entity_ids_invalid_utf8(monkeypatch):
    # Patch is_sane_utf8 to return False
    monkeypatch.setattr(views, "is_sane_utf8", lambda s: False)
    body = json.dumps({"source": "abc", "target": "def"}).encode()
    resp = views._parse_entity_ids(body)
    assert isinstance(resp, JsonResponse)
    assert resp.status_code == 400
    assert "Invalid characters" in resp.content.decode()

def test__run_mapping_generation_success(monkeypatch):
    # Patch generate_local_mappings to return a success message
    monkeypatch.setattr(views, "generate_local_mappings", lambda s, t: {"status": "success", "message": "Created 3 mappings"})
    result = views._run_mapping_generation("src", "tgt")
    assert result == {"status": "success", "created": 3}

def test__run_mapping_generation_error(monkeypatch):
    monkeypatch.setattr(views, "generate_local_mappings", lambda s, t: {"status": "error", "message": "fail", "code": 400})
    result = views._run_mapping_generation("src", "tgt")
    assert result == {"status": "error", "message": "fail", "code": 400}

def test__run_mapping_generation_exception(monkeypatch):
    monkeypatch.setattr(views, "generate_local_mappings", lambda s, t: 1/0)
    result = views._run_mapping_generation("src", "tgt")
    assert result["status"] == "error"
    assert result["code"] == 500

def test_generate_local_mappings_no_terms(monkeypatch):
    class DummyNeoTerm:
        nodes = MagicMock()
    DummyNeoTerm.nodes.filter.return_value = []
    monkeypatch.setattr(views, "NeoTerm", DummyNeoTerm)
    result = views.generate_local_mappings("src", "tgt")
    assert result["status"] == "error"
    assert result["code"] == 404

def test_generate_local_mappings_success(monkeypatch):
    # Setup mocks for all called functions
    term = MagicMock()
    term.definition.single.return_value = MagicMock(definition="def", embedding=[1,2,3])
    term.alias.all.return_value = [MagicMock(alias="alias1")]
    DummyNeoTerm = MagicMock()
    DummyNeoTerm.nodes.filter.return_value = [term]
    monkeypatch.setattr(views, "NeoTerm", DummyNeoTerm)
    monkeypatch.setattr(views, "_get_definition", lambda t: term.definition.single())
    monkeypatch.setattr(views, "_find_best_definition_text", lambda d, t: "best_def")
    monkeypatch.setattr(views, "_get_target_term", lambda d, t: MagicMock())
    monkeypatch.setattr(views, "_create_mapping", lambda *a, **k: True)
    result = views.generate_local_mappings("src", "tgt")
    assert result["status"] == "success"
    assert "Created" in result["message"]

def test_generate_local_mappings_exception(monkeypatch):
    DummyNeoTerm = MagicMock()
    DummyNeoTerm.nodes.filter.side_effect = Exception("fail")
    monkeypatch.setattr(views, "NeoTerm", DummyNeoTerm)
    result = views.generate_local_mappings("src", "tgt")
    assert result["status"] == "error"
    assert result["code"] == 500

def test__get_definition_success(monkeypatch):
    term = MagicMock()
    node = MagicMock()
    term.definition.single.return_value = node
    assert views._get_definition(term) == node

def test__get_definition_missing(monkeypatch):
    term = MagicMock()
    term.uid_chain = "chain"
    term.definition.single.return_value = None
    assert views._get_definition(term) is None

def test__get_definition_exception(monkeypatch):
    term = MagicMock()
    term.uid_chain = "chain"
    term.definition.single.side_effect = Exception("fail")
    assert views._get_definition(term) is None

def test__find_best_definition_text(monkeypatch):
    def_node = MagicMock()
    def_node.embedding = [1,2,3]
    def_node.definition = "abc"
    # Patch find_similar_text_by_embedding to return candidates
    monkeypatch.setattr(views, "find_similar_text_by_embedding", lambda *a, **k: [("abc", 0.9), ("xyz", 0.7)])
    monkeypatch.setattr(views, "antonyms_in_definition", lambda a, b: False)
    result = views._find_best_definition_text(def_node, "target")
    assert result == "abc"

def test__find_best_definition_text_no_candidates(monkeypatch):
    def_node = MagicMock()
    def_node.embedding = [1,2,3]
    def_node.definition = "abc"
    monkeypatch.setattr(views, "find_similar_text_by_embedding", lambda *a, **k: [])
    result = views._find_best_definition_text(def_node, "target")
    assert result is None

def test__find_best_definition_text_antonym(monkeypatch):
    def_node = MagicMock()
    def_node.embedding = [1,2,3]
    def_node.definition = "abc"
    monkeypatch.setattr(views, "find_similar_text_by_embedding", lambda *a, **k: [("abc", 0.9)])
    monkeypatch.setattr(views, "antonyms_in_definition", lambda a, b: True)
    result = views._find_best_definition_text(def_node, "target")
    assert result is None

def test__find_best_definition_text_exception(monkeypatch):
    def_node = MagicMock()
    def_node.embedding = [1,2,3]
    def_node.definition = "abc"
    monkeypatch.setattr(views, "find_similar_text_by_embedding", lambda *a, **k: 1/0)
    result = views._find_best_definition_text(def_node, "target")
    assert result is None

def test__get_target_term_success(monkeypatch):
    def_node = MagicMock()
    term_node = MagicMock()
    def_node.get_term_node.return_value = term_node
    DummyNeoDefinition = MagicMock()
    DummyNeoDefinition.nodes.get_or_none.return_value = def_node
    monkeypatch.setattr(views, "NeoDefinition", DummyNeoDefinition)
    result = views._get_target_term("def", "target")
    assert result == term_node

def test__get_target_term_no_def_node(monkeypatch):
    DummyNeoDefinition = MagicMock()
    DummyNeoDefinition.nodes.get_or_none.return_value = None
    monkeypatch.setattr(views, "NeoDefinition", DummyNeoDefinition)
    result = views._get_target_term("def", "target")
    assert result is None

def test__get_target_term_no_term_node(monkeypatch):
    def_node = MagicMock()
    def_node.get_term_node.return_value = None
    DummyNeoDefinition = MagicMock()
    DummyNeoDefinition.nodes.get_or_none.return_value = def_node
    monkeypatch.setattr(views, "NeoDefinition", DummyNeoDefinition)
    result = views._get_target_term("def", "target")
    assert result is None

def test__get_target_term_exception(monkeypatch):
    DummyNeoDefinition = MagicMock()
    DummyNeoDefinition.nodes.get_or_none.side_effect = Exception("fail")
    monkeypatch.setattr(views, "NeoDefinition", DummyNeoDefinition)
    result = views._get_target_term("def", "target")
    assert result is None

def test__create_mapping_success(monkeypatch):
    source_term = MagicMock()
    source_term.uid_chain = "chain"
    source_term.lcvid = "lcvid"
    source_term.uid = "uid"
    target_term = MagicMock()
    DummyNeoMapping = MagicMock()
    DummyNeoMapping.create_node.return_value = MagicMock(set_relationships=MagicMock())
    monkeypatch.setattr(views, "NeoMapping", DummyNeoMapping)
    result = views._create_mapping(source_term, "def", ["alias"], target_term)
    assert result is True

def test__create_mapping_exception(monkeypatch):
    source_term = MagicMock()
    source_term.uid_chain = "chain"
    source_term.lcvid = "lcvid"
    source_term.uid = "uid"
    target_term = MagicMock()
    DummyNeoMapping = MagicMock()
    DummyNeoMapping.create_node.side_effect = Exception("fail")
    monkeypatch.setattr(views, "NeoMapping", DummyNeoMapping)
    result = views._create_mapping(source_term, "def", ["alias"], target_term)
    assert result is False
