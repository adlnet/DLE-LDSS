import unittest
from unittest.mock import patch, MagicMock
from django.core.exceptions import ValidationError
from django.test import tag
from core.ccvmodels import (
    MetadataLedger,
    SupplementalLedger,
    CompositeLedger,
    FilterRecord,
    FilterMetadata,
    CCVUpstream,
    LCVDownstream,
)

# pylint: disable=protected-access

# DummyQuerySet simulates basic filtering/exclusion behavior.
class DummyQuerySet:
    def __init__(self, items):
        self.items = items

    def all(self):
        return self

    def filter(self, **kwargs):
        filtered_items = []
        for item in self.items:
            match = True
            for key, value in kwargs.items():
                # Handle common lookups
                if key == 'pk':
                    if item.pk != value:
                        match = False
                        break
                elif key.endswith('__iexact'):
                    attribute_name = key[:-8]
                    item_value = getattr(item, attribute_name, None)
                    if str(item_value).lower() != str(value).lower():
                        match = False
                        break
                elif key.endswith('__icontains'):
                    attribute_name = key[:-10]
                    item_value = getattr(item, attribute_name, None)
                    if str(value).lower() not in str(item_value).lower():
                        match = False
                        break
                else:
                    if getattr(item, key, None) != value:
                        match = False
                        break
            if match:
                filtered_items.append(item)
        return DummyQuerySet(filtered_items)

    def exclude(self, **kwargs):
        remaining_items = []
        for item in self.items:
            should_exclude = False
            for key, value in kwargs.items():
                if key == 'pk':
                    if item.pk == value:
                        should_exclude = True
                        break
                elif key.endswith('__iexact'):
                    attribute_name = key[:-8]
                    item_value = getattr(item, attribute_name, None)
                    if str(item_value).lower() == str(value).lower():
                        should_exclude = True
                        break
                elif key.endswith('__icontains'):
                    attribute_name = key[:-10]
                    item_value = getattr(item, attribute_name, None)
                    if str(value).lower() in str(item_value).lower():
                        should_exclude = True
                        break
                else:
                    if getattr(item, key, None) == value:
                        should_exclude = True
                        break
            if not should_exclude:
                remaining_items.append(item)
        return DummyQuerySet(remaining_items)

    def __iter__(self):
        return iter(self.items)

    def count(self):
        return len(self.items)

# DummyManager simulates a many-to-many RelatedManager.
class DummyManager:
    def __init__(self, data):
        self.data = data
    def all(self):
        return self.data

# DummyExp simulates a model instance with a primary key and metadata attribute.
class DummyExp:
    def __init__(self, pk, metadata):
        self.pk = pk
        self.metadata = metadata

@tag('unit')
class TestFilterRecord(unittest.TestCase):
    def setUp(self):
        self.record_equal = FilterRecord(field_name="name", comparator=FilterRecord.EQUAL, field_value="test")
        self.record_unequal = FilterRecord(field_name="name", comparator=FilterRecord.UNEQUAL, field_value="test")
        self.record_contains = FilterRecord(field_name="name", comparator=FilterRecord.CONTAINS, field_value="test")
        # For metadata filtering, note the dot notation in field_name.
        self.metadata_record = FilterRecord(field_name="metadata.field", comparator=FilterRecord.EQUAL, field_value="match")
    def tearDown(self):
        pass
    def test_str(self):
        self.assertEqual(str(self.record_equal), "name EQUAL test")
    def test_apply_filter_root_equal(self):
        fake_queryset = MagicMock()
        fake_queryset.filter.return_value = "filtered"
        result = self.record_equal.apply_filter(fake_queryset)
        fake_queryset.filter.assert_called_with(name__iexact="test")
        self.assertEqual(result, "filtered")
    def test_apply_filter_root_unequal(self):
        fake_queryset = MagicMock()
        fake_queryset.exclude.return_value = "excluded"
        result = self.record_unequal.apply_filter(fake_queryset)
        fake_queryset.exclude.assert_called_with(name__iexact="test")
        self.assertEqual(result, "excluded")
    def test_apply_filter_root_contains(self):
        fake_queryset = MagicMock()
        fake_queryset.filter.return_value = "filtered"
        result = self.record_contains.apply_filter(fake_queryset)
        fake_queryset.filter.assert_called_with(name__icontains="test")
        self.assertEqual(result, "filtered")
    def test_apply_filter_metadata_equal(self):
        # Create two dummy experiences: one matching and one not.
        exp1 = DummyExp(pk=1, metadata={"field": "match"})
        exp2 = DummyExp(pk=2, metadata={"field": "no match"})
        fake_queryset = DummyQuerySet([exp1, exp2])
        # Override __simple_metadata_filter to bypass extra filtering.
        original_simple = self.metadata_record._FilterRecord__simple_metadata_filter
        self.metadata_record._FilterRecord__simple_metadata_filter = lambda qs: qs
        result_qs = self.metadata_record.apply_filter(fake_queryset)
        self.metadata_record._FilterRecord__simple_metadata_filter = original_simple
        filtered_ids = [item.pk for item in result_qs]
        self.assertIn(1, filtered_ids)
        self.assertNotIn(2, filtered_ids)

@tag('unit')
class TestFilterMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata_filter = FilterMetadata(field_name="metadata.field", operation=FilterMetadata.INCLUDE)
    def tearDown(self):
        pass
    def test_str(self):
        self.assertEqual(str(self.metadata_filter), "INCLUDE metadata.field")

@tag('unit')
class TestCCVUpstream(unittest.TestCase):
    def setUp(self):
        self.api_endpoint = "http://api.ccv.com"
        self.instance = CCVUpstream(ccv_api_endpoint=self.api_endpoint, ccv_api_endpoint_status=CCVUpstream.ACTIVE)
    def tearDown(self):
        pass
    def test_str(self):
        self.assertEqual(str(self.instance), self.api_endpoint)
    @patch('core.ccvmodels.CCVUpstream.objects')
    def test_get_endpoint_success(self, mock_objects):
        fake_instance = MagicMock()
        fake_instance.ccv_api_endpoint = self.api_endpoint
        mock_objects.first.return_value = fake_instance
        endpoint = CCVUpstream.get_endpoint()
        self.assertEqual(endpoint, self.api_endpoint)
    @patch('core.ccvmodels.CCVUpstream.objects')
    def test_get_endpoint_none(self, mock_objects):
        mock_objects.first.return_value = None
        endpoint = CCVUpstream.get_endpoint()
        self.assertIsNone(endpoint)
    @patch('core.ccvmodels.CCVUpstream.objects')
    def test_get_endpoint_exception(self, mock_objects):
        mock_objects.first.side_effect = Exception("DB error")
        with self.assertRaises(ValidationError):
            CCVUpstream.get_endpoint()

@tag('unit')
class TestLCVDownstream(unittest.TestCase):
    def setUp(self):
        self.api_endpoint = "http://api.lcv.com"
        self.instance = LCVDownstream(
            lcv_api_endpoint=self.api_endpoint,
            lcv_api_endpoint_status=LCVDownstream.ACTIVE,
            lcv_api_key="key",
            source_name="source"
        )
        self.instance.pk = 123
    def tearDown(self):
        pass
    def test_str(self):
        self.assertEqual(str(self.instance), self.api_endpoint)
    def test_determine_fields(self):
        include_filter = FilterMetadata(field_name="field1", operation=FilterMetadata.INCLUDE)
        exclude_filter = FilterMetadata(field_name="field2", operation=FilterMetadata.EXCLUDE)
        # Override the class-level many-to-many manager for filter_metadata.
        original_filter_metadata = LCVDownstream.filter_metadata
        try:
            LCVDownstream.filter_metadata = DummyManager(DummyQuerySet([include_filter, exclude_filter]))
            include_fields, exclude_fields = self.instance.determine_fields()
            self.assertEqual(include_fields, ["field1"])
            self.assertEqual(exclude_fields, ["field2"])
        finally:
            LCVDownstream.filter_metadata = original_filter_metadata
    def test_apply_filter(self):
        dummy_filter = MagicMock()
        dummy_filter.apply_filter.side_effect = lambda qs: qs.filter(dummy_filter_applied=True)
        # Override the class-level many-to-many manager for filter_records.
        original_filter_records = LCVDownstream.filter_records
        try:
            LCVDownstream.filter_records = DummyManager([dummy_filter])
            fake_queryset = MagicMock()
            fake_queryset.filter.return_value = fake_queryset
            fake_queryset.exclude.return_value = fake_queryset
            result = self.instance.apply_filter(fake_queryset)
            fake_queryset.filter.assert_any_call(record_status='Active')
            fake_queryset.exclude.assert_any_call(lcv_destination__pk=self.instance.pk)
            # Check that our dummy_filter.apply_filter was indeed invoked.
            self.assertTrue(dummy_filter.apply_filter.called)
        finally:
            LCVDownstream.filter_records = original_filter_records
    @patch('core.ccvmodels.LCVDownstream.objects')
    def test_get_endpoints_success(self, mock_objects):
        mock_objects.values_list.return_value = ["http://api.lcv1.com", "http://api.lcv2.com"]
        endpoints = LCVDownstream.get_endpoints()
        self.assertEqual(endpoints, ["http://api.lcv1.com", "http://api.lcv2.com"])
    @patch('core.ccvmodels.LCVDownstream.objects')
    def test_get_endpoints_none(self, mock_objects):
        mock_objects.values_list.return_value = []
        endpoints = LCVDownstream.get_endpoints()
        self.assertIsNone(endpoints)
    @patch('core.ccvmodels.LCVDownstream.objects')
    def test_get_endpoints_exception(self, mock_objects):
        mock_objects.values_list.side_effect = Exception("DB error")
        with self.assertRaises(ValidationError):
            LCVDownstream.get_endpoints()
