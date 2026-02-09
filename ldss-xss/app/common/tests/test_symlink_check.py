import os
import tempfile
import shutil
import unittest
from django.test import tag

# adjust the import to your module path
from common.symlink_check import symlink_check

@tag('unit')
class SymlinkCheckTestCase(unittest.TestCase):
    """Unit tests for common.symlink_check.symlink_check"""

    def setUp(self):
        """Create a temporary directory with a subdirectory for allowed_base."""
        self.temp_dir = tempfile.mkdtemp()
        self.allowed_base = os.path.join(self.temp_dir, "base")
        os.mkdir(self.allowed_base)

    def tearDown(self):
        """Remove the temporary directory after each test."""
        shutil.rmtree(self.temp_dir)

    def test_allows_regular_file_under_base(self):
        """A normal file under allowed_base should not raise."""
        fpath = os.path.join(self.allowed_base, "file.txt")
        with open(fpath, "w", encoding="utf-8") as f:
            f.write("hello")
        # should complete without exception
        symlink_check(fpath, self.allowed_base)

    def test_refuses_symlink(self):
        """A symlink under allowed_base should raise the symlink error."""
        target = os.path.join(self.allowed_base, "real.txt")
        with open(target, "w", encoding="utf-8") as f:
            f.write("data")
        link = os.path.join(self.allowed_base, "link.txt")
        os.symlink(target, link)

        with self.assertRaises(RuntimeError) as cm:
            symlink_check(link, self.allowed_base)
        expected = f"Refusing symlink at {repr(link)}"
        self.assertEqual(str(cm.exception), expected)

    @unittest.skipIf(os.name == "nt", reason="hard links may require elevated privileges on Windows")
    def test_refuses_hard_link(self):
        """A hard link (nlink > 1) under allowed_base should raise the hard link error."""
        original = os.path.join(self.allowed_base, "orig.txt")
        with open(original, "w", encoding="utf-8") as f:
            f.write("payload")
        hard = os.path.join(self.allowed_base, "hard.txt")
        os.link(original, hard)

        # confirm we did create a second link
        self.assertGreater(os.stat(original).st_nlink, 1)

        with self.assertRaises(RuntimeError) as cm:
            # checking either path would trigger, choose original
            symlink_check(original, self.allowed_base)
        expected = f"Refusing hard link at {repr(original)}"
        self.assertEqual(str(cm.exception), expected)

    def test_refuses_outside_base(self):
        """Any path outside allowed_base should raise the outside-base error."""
        outside = os.path.join(self.temp_dir, "outside.txt")
        # note: file need not actually exist for the outside check
        real_out = os.path.realpath(outside)
        real_base = os.path.realpath(self.allowed_base)

        with self.assertRaises(RuntimeError) as cm:
            symlink_check(outside, self.allowed_base)
        expected = f"Path {repr(real_out)} outside allowed base {repr(real_base)}"
        self.assertEqual(str(cm.exception), expected)
