import unittest
from unittest.mock import patch, MagicMock
from neomodel import NodeSet
from django.test import tag
from uid.models import (
    Provider,
    UIDRequestToken,
    UIDRequestNode,
    UIDCounter,
    UIDNode,
    report_uids_by_echelon,
    report_all_uids,
    report_all_generated_uids
)

class FakeNodeSet(list, NodeSet):
    pass

class DummyUIDRequestNode:
    def __init__(self, token, default_uid, default_uid_chain):
        self.token = token
        self.default_uid = default_uid
        self.default_uid_chain = default_uid_chain
    def save(self):
        pass
@tag('unit')
class TestUIDModels(unittest.TestCase):
    def setUp(self):
        self.db_patch = patch('uid.models.db')
        self.mock_db = self.db_patch.start()
        self.sleep_patch = patch('uid.models.time.sleep', return_value=None)
        self.mock_sleep = self.sleep_patch.start()
        self.fake_node_set = FakeNodeSet()
        self.uidcounter_nodes_patch = patch.object(UIDCounter, 'nodes', self.fake_node_set)
        self.uidnode_nodes_patch = patch.object(UIDNode, 'nodes', self.fake_node_set)
        self.provider_nodes_patch = patch.object(Provider, 'nodes', self.fake_node_set)
        self.uidcounter_nodes_patch.start()
        self.uidnode_nodes_patch.start()
        self.provider_nodes_patch.start()
        self.genuidlog_patch = patch('uid.models.GeneratedUIDLog.objects')
        self.mock_genuidlog_objects = self.genuidlog_patch.start()
        self.uidcounter_save_patch = patch.object(UIDCounter, 'save', lambda self, *args, **kwargs: None)
        self.uidnode_save_patch = patch.object(UIDNode, 'save', lambda self, *args, **kwargs: None)
        self.uidrequestnode_save_patch = patch.object(UIDRequestNode, 'save', lambda self, *args, **kwargs: None)
        self.uidrequesttoken_save_patch = patch.object(UIDRequestToken, 'save', lambda self, *args, **kwargs: None)
        self.uidcounter_save_patch.start()
        self.uidnode_save_patch.start()
        self.uidrequestnode_save_patch.start()
        self.uidrequesttoken_save_patch.start()

    def tearDown(self):
        self.db_patch.stop()
        self.sleep_patch.stop()
        self.uidcounter_nodes_patch.stop()
        self.uidnode_nodes_patch.stop()
        self.provider_nodes_patch.stop()
        self.genuidlog_patch.stop()
        self.uidcounter_save_patch.stop()
        self.uidnode_save_patch.stop()
        self.uidrequestnode_save_patch.stop()
        self.uidrequesttoken_save_patch.stop()
        patch.stopall()

    def patch_relationship_connect(self):
        return patch("neomodel.sync_.relationship_manager.RelationshipManager.connect", return_value=None)

    def test_Provider_create_provider(self):
        uid_node_instance = UIDNode(uid="0x00000001")
        uid_node_instance.save = lambda *args, **kwargs: None
        with patch('uid.models.UIDNode.create_node', return_value=uid_node_instance):
            counter_obj = MagicMock(spec=UIDCounter)
            with patch('uid.models.UIDCounter.get_instance', return_value=counter_obj):
                with patch.object(Provider, 'save', lambda self, *args, **kwargs: None):
                    with self.patch_relationship_connect():
                        provider = Provider.create_provider("TestProvider")
                        provider.uid = MagicMock()
                        provider.uid_counter = MagicMock()
                        provider.uid.connect(uid_node_instance)
                        provider.uid_counter.connect(counter_obj)
                        self.assertEqual(provider.name, "TestProvider")
                        self.assertEqual(provider.default_uid, "0x00000001")
                        provider.uid.connect.assert_called_with(uid_node_instance)
                        provider.uid_counter.connect.assert_called_with(counter_obj)

    def test_UIDCounter_get_instance_no_existing(self):
        self.fake_node_set.get_or_none = MagicMock(return_value=None)
        with patch.object(UIDCounter, 'save', lambda self, *args, **kwargs: None):
            instance = UIDCounter.get_instance("test_owner")
            self.assertEqual(instance.owner_uid, "test_owner")

    def test_UIDNode_create_node(self):
        def fake_save(*args, **kwargs):
            return None
        with patch.object(UIDNode, 'save', fake_save):
            with patch('uid.models.generate_uid', return_value="0x00000001") as mock_generate_uid:
                node = UIDNode.create_node("owner_dummy")
                self.assertEqual(node.uid, "0x00000001")
                mock_generate_uid.assert_called_with("owner_dummy")

    def test_UIDRequestNode_create_requested_uid(self):
        provider_inst = Provider(name="TestProvider", default_uid="0xDEFAULT")
        provider_inst.save = lambda *args, **kwargs: None
        with patch('uid.models.ProviderDjangoModel.ensure_provider_exists', return_value=provider_inst):
            node_instance = UIDNode(uid="0x00000001")
            node_instance.save = lambda *args, **kwargs: None
            with patch('uid.models.UIDNode.create_node', return_value=node_instance):
                with self.patch_relationship_connect():
                    with patch.object(UIDRequestNode, 'save', lambda self, *args, **kwargs: None):
                        req_node = UIDRequestNode.create_requested_uid("TestProvider")
                        req_node.uid = MagicMock()
                        req_node.provider = MagicMock()
                        req_node.uid.connect(node_instance)
                        req_node.provider.connect(provider_inst)
                        req_node.uid.connect.assert_called_with(node_instance)
                        req_node.provider.connect.assert_called_with(provider_inst)
                        self.assertEqual(req_node.default_uid, "0x00000001")
                        expected_chain = f"{provider_inst.default_uid}-0x00000001"
                        self.assertEqual(req_node.default_uid_chain, expected_chain)
                        self.assertIsNotNone(req_node.token)

    # def test_UIDRequestToken_save(self):
    # # Create a dummy node with the expected attributes.
    #     DummyNode = type("DummyNode", (), {
    #         "token": "token123",
    #         "default_uid": "0x00000001",
    #         "default_uid_chain": "chain123",
    #         "save": lambda self: None
    #     })
    #     dummy_node = DummyNode()
    #     # Patch create_requested_uid so that it returns our dummy node.
    #     with patch("uid.models.UIDRequestNode.create_requested_uid", return_value=dummy_node):
    #         token_instance = UIDRequestToken(
    #             provider_name="TestProvider",
    #             echelon="level1",
    #             termset="set1",
    #             uid="",
    #             uid_chain=""
    #         )
    #         # Patch the base Model.save so that it does nothing.
    #         with patch("django.db.models.Model.save", lambda self, *args, **kwargs: None):
    #             token_instance.save()
    #         self.assertEqual(token_instance.token, "token123")
    #         self.assertEqual(token_instance.uid, "0x00000001")
    #         self.assertEqual(token_instance.uid_chain, "chain123")

    def test_report_uids_by_echelon(self):
        node1 = MagicMock()
        node1.uid = "0xAAA11111"
        node2 = MagicMock()
        node2.uid = "0xBBB22222"
        self.fake_node_set.filter = MagicMock(return_value=[node1, node2])
        with patch.object(UIDNode, 'nodes', self.fake_node_set):
            uids = report_uids_by_echelon("level1")
            self.assertEqual(uids, ["0xAAA11111", "0xBBB22222"])

    def test_report_all_uids(self):
        node1 = MagicMock()
        node1.uid = "0xAAA11111"
        node2 = MagicMock()
        node2.uid = "0xBBB22222"
        self.fake_node_set.all = MagicMock(return_value=[node1, node2])
        with patch.object(UIDNode, 'nodes', self.fake_node_set):
            uids = report_all_uids()
            self.assertEqual(uids, ["0xAAA11111", "0xBBB22222"])

    def test_report_all_generated_uids(self):
        log1 = MagicMock()
        log1.uid = "0xAAA11111"
        log1.uid_full = "prov-0xAAA11111"
        log1.generated_at = "2025-03-04"
        log2 = MagicMock()
        log2.uid = "0xBBB22222"
        log2.uid_full = "prov-0xBBB22222"
        log2.generated_at = "2025-03-04"
        self.mock_genuidlog_objects.all.return_value = [log1, log2]
        report = report_all_generated_uids()
        expected = [
            {"uid": "0xAAA11111", "uid_full": "prov-0xAAA11111", "generated_at": "2025-03-04"},
            {"uid": "0xBBB22222", "uid_full": "prov-0xBBB22222", "generated_at": "2025-03-04"},
        ]
        self.assertEqual(report, expected)
            