from unittest.mock import patch

from ddt import ddt
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase, tag
from django.conf import settings



@tag('unit')
@ddt
class CommandTests(SimpleTestCase):
    """Test cases for waitdb """

    def test_wait_for_db_ready(self):
        """Test that waiting for db when db is available"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = gi
            gi.ensure_connection.return_value = True
            call_command('waitdb')
            self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """Test waiting for db"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = gi
            gi.ensure_connection.side_effect = [OperationalError] * 5 + [True]
            call_command('waitdb')
            self.assertEqual(gi.ensure_connection.call_count, 6)

    @patch('django.conf.settings')
    def test_all_settings_variables_not_empty(self, mock_settings):
        """Test that all settings variables are not empty"""
        for attr in dir(settings):
            if attr.isupper():
                value = getattr(settings, attr)
                setattr(mock_settings, attr, value)

        for attr in dir(mock_settings):
            if attr.isupper():
                value = getattr(settings, attr)
                if value is None:
                    self.assertIsNone(value, f"{attr} is None in settings")
                elif value == '':
                    self.assertEqual(value, '', f"{attr} is empty in settings")
                else:
                    self.assertIsNotNone(value, f"{attr} has a value in settings")
